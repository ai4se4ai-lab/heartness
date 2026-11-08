"""Regenerate tidy metrics, seed-clustered inference and figures from immutable raw."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import binomtest, rankdata, wilcoxon

from benchmark.generate import FAMILIES


def scores(predicted, expected):
    p, t = set(predicted), set(expected)
    hit = len(p & t)
    precision = hit / len(p) if p else float(not t)
    recall = hit / len(t) if t else 1.0
    return {"precision": precision, "recall": recall,
            "f1": 2 * hit / (len(p) + len(t)) if p or t else 1.0,
            "jaccard": hit / len(p | t) if p or t else 1.0,
            "exact": int(p == t)}


def interval(values):
    values = np.asarray(values, dtype=float)
    if len(values) == 0:
        return {"mean": None, "lo": None, "hi": None, "n": 0}
    rng = np.random.default_rng(20261106)
    means = np.mean(rng.choice(values, (2000, len(values)), replace=True), axis=1)
    return {"mean": float(np.mean(values)), "lo": float(np.quantile(means, .025)),
            "hi": float(np.quantile(means, .975)), "n": len(values)}


def rate_interval(values):
    values = list(values)
    n, k = len(values), sum(bool(v) for v in values)
    ci = binomtest(k, n).proportion_ci(method="wilson")
    return {"mean": k / n, "lo": float(ci.low), "hi": float(ci.high), "n": n,
            "ci_method": "Wilson", "positives": k}


def compare(x, y):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    d = x - y
    nonzero = d[d != 0]
    p = float(wilcoxon(x, y).pvalue) if len(nonzero) else 1.0
    ranks = rankdata(abs(nonzero))
    rbc = float(np.sum(ranks * np.sign(nonzero)) / np.sum(ranks)) if len(nonzero) else 0.
    cliff = float(np.mean(np.sign(x[:, None] - y[None, :])))
    return {"p": p, "paired_rank_biserial": rbc, "cliff_descriptive": cliff,
            "paired_difference": interval(d)}


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def process(root):
    out = Path("results/processed")
    out.mkdir(parents=True, exist_ok=True)
    figures = Path("results/figures")
    figures.mkdir(parents=True, exist_ok=True)
    records = [json.loads(p.read_text()) | {"raw": str(p)} for p in sorted(root.glob("E*/*/*/record.json"))]
    metrics = []
    for r in records:
        if "scenario" not in r or "outputs" not in r:
            continue
        for method, output in r["outputs"].items():
            for task, values in output["queries"].items():
                metrics.append({"experiment": r["experiment"], "config_hash": r["config_hash"],
                                "seed": r["seed"], "family": r["config"]["family"],
                                "artifacts": r["config"]["artifacts"],
                                "capture": r["config"]["capture"],
                                "paraphrase": r["config"]["paraphrase"],
                                "fanout": r["config"]["fanout"],
                                "deployments": r["config"]["deployments"],
                                "source_edges": r["scenario"].get("realized", {}).get("source_edges", 0),
                                "max_sources": r["scenario"].get("realized", {}).get("max_sources", 0),
                                "dependency_only_edges": r["scenario"].get("realized", {}).get("dependency_only_edges", 0),
                                "deployment_memberships": r["scenario"].get("realized", {}).get("deployment_memberships", 0),
                                "method": method, "task": task,
                                **scores(values, r["scenario"]["truth"][task]),
                                "seconds": output["seconds"], "peak_bytes": output["peak_bytes"],
                                "raw": r["raw"]})
    write_csv(out / "trace_metrics.csv", metrics)
    summary = {"campaign": str(root), "records": len(records), "rq1": {}, "capture": {},
               "paraphrase": {}, "checking": [], "counterexamples": [], "scale": [],
               "conformance": {}, "remediation": {}, "ablations": [], "search": [], "robustness": {}}
    tests = []
    # Cluster repeated family/size cases by seed before confidence intervals/inference.
    cluster = defaultdict(list)
    for row in metrics:
        if row["experiment"] == "E01_traceability":
            cluster[(row["method"], row["task"], row["seed"])].append(row["f1"])
    methods = sorted({key[0] for key in cluster})
    for task in ("impact", "origins", "descendants"):
        for method in methods:
            values = [np.mean(cluster[(method, task, s)]) for s in range(30)]
            summary["rq1"][method + ":" + task] = interval(values)
            if method != "ours":
                ours = [np.mean(cluster[("ours", task, s)]) for s in range(30)]
                result = compare(ours, values)
                tests.append({"task": task, "comparison": "ours vs " + method,
                              "p": result["p"], "paired_rank_biserial": result["paired_rank_biserial"],
                              "cliff_descriptive": result["cliff_descriptive"],
                              "difference_mean": result["paired_difference"]["mean"]})
    # Holm over all nine planned RQ1 comparisons.
    maximum = 0.
    for rank, row in enumerate(sorted(tests, key=lambda r: r["p"])):
        maximum = max(maximum, min(1., (len(tests) - rank) * row["p"]))
        row["holm_p"] = maximum
    write_csv(out / "statistical_tests.csv", tests)
    for experiment, factor, name in (("E02_capture", "capture", "capture"),
                                      ("E03_paraphrase", "paraphrase", "paraphrase")):
        for level in sorted({r[factor] for r in metrics if r["experiment"] == experiment}):
            for method in methods:
                for task in ("impact", "origins", "descendants"):
                    subset = [r for r in metrics if r["experiment"] == experiment and
                              r[factor] == level and r["method"] == method and r["task"] == task]
                    summary[name][f"{level}:{method}:{task}"] = interval([r["f1"] for r in subset])
    for r in records:
        experiment = r["experiment"]
        if experiment == "E05_model_checking":
            summary["checking"].append({**r["config"], "agree": r["agree"],
                "safe": r["python"]["safe"], "complete": r["python"]["complete"],
                "states": r["python"]["states"], "length": len(r["python"]["trace"]),
                "seconds": r["python_cost"]["seconds"], "spin_seconds": r["spin_cost"]["seconds"],
                "raw": r["raw"]})
        elif experiment == "E06_counterexamples":
            summary["counterexamples"].append({**r["config"], "length": r["length"],
                "shorter_safe": r["shorter_safe"], "projection_replayed": bool(r["projection_replay"]),
                "implementation_rejected": r["implementation_replay"]["rejected"],
                "implementation_violation": r["implementation_replay"]["violations"], "raw": r["raw"]})
        elif experiment == "E08_state_scale":
            summary["scale"].append({**r["config"], "states": r["full"]["states"],
                "complete": r["full"]["complete"], "seconds": r["cost"]["seconds"],
                "peak_bytes": r["cost"]["peak_bytes"],
                "projection_states": r["two_node_projection"]["states"],
                "projection_seconds": r["projection_cost"]["seconds"], "raw": r["raw"]})
        elif experiment == "E04_ablations":
            summary["ablations"] = r["checks"]
            summary["property_ablations"] = r.get("targeted", [])
    conformance = [r for r in records if r["experiment"] == "E09_conformance"]
    for variant in conformance[0]["outputs"]:
        summary["conformance"][variant] = rate_interval([bool(r["outputs"][variant]) for r in conformance])
    summary["conformance"]["replay_seconds"] = interval([r["monitor_cost"]["seconds"] for r in conformance])
    summary["conformance"]["time_overhead_percent"] = interval([
        100 * r["monitor_cost"]["seconds"] / r["execution_cost"]["seconds"] for r in conformance])
    remediation = [r for r in records if r["experiment"] == "E07_remediation"]
    summary["remediation"] = {"runs": len(remediation),
        "unsafe_rollback_rejected": sum(r["unsafe_rollback_rejected"] for r in remediation),
        "effects_retained": sum(len(r["after"]["effects"]) == 1 for r in remediation),
        "violations": sum(bool(r["violations"]) for r in remediation)}
    for mutant in ("", "P2", "P3", "P4", "P8", "P9"):
        for method in ("random", "hypothesis", "bfs"):
            subset = [r["outputs"][method] for r in records if r["experiment"] == "E11_search"
                      and r["config"]["mutant"] == mutant]
            summary["search"].append({"mutant": mutant or "reference", "method": method,
                "detection": rate_interval([r["found"] for r in subset]),
                "seconds": interval([r["seconds"] for r in subset])})
    summary["correspondence"] = [r for r in records if r["experiment"] == "E15_correspondence"]
    runtime = []
    for size in (4, 8, 16, 32):
        selected = [r for r in records if r["experiment"] == "E13_runtime_cost" and
                    r["config"]["artifacts"] == size]
        for phase in ("capture", "admission", "monitor", "withdrawal"):
            if selected:
                value = interval([r[phase+"_cost"]["seconds"] for r in selected])
                runtime.append({"artifacts": size, "phase": phase, **value,
                                "mean_peak_bytes": float(np.mean([r[phase+"_cost"]["peak_bytes"]
                                                                  for r in selected]))})
    summary["runtime_cost"] = runtime
    write_csv(out / "runtime_cost.csv", runtime)
    linter_records = [r for r in records if r["experiment"] == "E14_linter"]
    if linter_records:
        summary["linter"] = {"f1": interval([scores(r["B3_fault"], r["truth_violations"])["f1"]
                                              for r in linter_records]),
                             "benign_alarms": sum(bool(r["B3_benign"]) for r in linter_records),
                             "cases": len(linter_records)}
    factors = []
    for fanout in (1, 3, 6):
        for deployments in (1, 4):
            selected = [r for r in metrics if r["experiment"] == "E10_robustness" and
                        r["method"] == "ours" and r["task"] == "deployment_impact" and
                        r["fanout"] == fanout and r["deployments"] == deployments]
            if selected:
                factors.append({"fanout": fanout, "deployments": deployments,
                    "mean_source_edges": float(np.mean([r["source_edges"] for r in selected])),
                    "max_sources": max(r["max_sources"] for r in selected),
                    "mean_dependency_only_edges": float(np.mean([r["dependency_only_edges"] for r in selected])),
                    "mean_memberships": float(np.mean([r["deployment_memberships"] for r in selected])),
                    "mean_f1": float(np.mean([r["f1"] for r in selected])),
                    "mean_seconds": float(np.mean([r["seconds"] for r in selected]))})
    summary["factor_analysis"] = factors
    write_csv(out / "factor_analysis.csv", factors)
    exact = []
    for family in FAMILIES:
        for size in (16, 64, 256):
            for method in methods:
                selected = [r for r in metrics if r["experiment"] == "E01_traceability" and
                            r["family"] == family and r["artifacts"] == size and r["method"] == method
                            and r["task"] == "origins"]
                exact.append({"family": family, "artifacts": size, "method": method,
                              "exact_origin_accuracy": float(np.mean([r["exact"] for r in selected]))})
    write_csv(out / "exact_origins.csv", exact)
    for size in (16, 64, 256, 1024, 2048):
        subset = [r for r in metrics if r["experiment"] == "E08_graph_scale" and
                  r["method"] == "ours" and r["task"] == "impact" and r["artifacts"] == size]
        summary["robustness"]["graph_" + str(size)] = {
            "seconds": interval([r["seconds"] for r in subset]),
            "peak_bytes": interval([r["peak_bytes"] for r in subset]),
            "f1": interval([r["f1"] for r in subset])}
    for omitted in FAMILIES:
        subset = [r["f1"] for r in metrics if r["experiment"] == "E01_traceability" and
                  r["method"] == "ours" and r["task"] == "impact" and r["family"] != omitted]
        summary["robustness"]["omit_" + omitted] = {"mean": float(np.mean(subset)),
                                                   "interpretation": "no training; sensitivity only"}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    write_csv(out / "checking.csv", summary["checking"])
    write_csv(out / "state_scale.csv", summary["scale"])
    fig, ax = plt.subplots(figsize=(5, 3))
    for method in ("ours", "B0_file_history", "B1_lexical", "B2_capture_only"):
        x = [0, .25, .5, .75, 1]
        y = [summary["capture"][f"{v}:{method}:impact"]["mean"] if
             f"{v}:{method}:impact" in summary["capture"] else
             summary["capture"][f"{float(v)}:{method}:impact"]["mean"] for v in x]
        ax.plot(x, y, marker="o", label=method)
    ax.set(xlabel="Captured derivation fraction", ylabel="Mean impact F1", ylim=(0, 1.05))
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(figures / "capture.pdf")
    plt.close(fig)
    index = ["# Experiment-to-evidence index", "", f"Selected campaign: `{root}`.", "",
             "All paper numeric macros are inserted by `scripts/build_paper_results.py` from",
             "`results/processed/summary.json`; all graph metrics are in `trace_metrics.csv`.", "",
             "| Experiment | Raw records | Derived evidence |", "|---|---|---|"]
    for name in sorted({r["experiment"] for r in records}):
        count = sum(r["experiment"] == name for r in records)
        index.append(f"| {name} | `{root}/{name}/*/*/record.json` ({count}) | `experiments/process.py` |")
    index.extend(["", "Paper Table I: notation (definitions, no measured values).",
                  "Paper property/operator tables: specification (design/metamodel.md).",
                  "Paper RQ1 table and capture plot: E01/E02; RQ2 table: E05/E06;",
                  "paper scale table: E08; monitor/remediation numbers: E07/E09;",
                  "search table: E11; coverage/mutation: results/validation/*.json.",
                  "Counts, seed ranges and size/depth limits are protocol settings, not outcomes."])
    Path("experiments/EXPERIMENT_INDEX.md").write_text("\n".join(index) + "\n")
    print(json.dumps({"records": len(records), "processed": str(out)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path)
    args = parser.parse_args()
    root = args.input or sorted(p.parent for p in Path("results/raw").glob("campaign-*/manifest.json"))[-1]
    process(root)
