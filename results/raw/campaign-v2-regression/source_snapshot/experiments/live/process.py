"""Aggregate live-study records. Never edits raw records.

python -m experiments.live.process tune  CAMPAIGN   # thresholds from dev seeds only
python -m experiments.live.process report CAMPAIGN  # metrics, statistics, tables
"""
from __future__ import annotations

import csv
import json
import random
import sys
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from scipy.stats import wilcoxon

DEV_SEEDS = {100, 101}
REMEDIES = ("none", "R1_delete_root", "R2_tfidf", "R3_embed", "R4_judge",
            "H", "H_noEME", "H_noDeps", "H_local")
OUT = Path("results/processed/live")


def records(campaign: Path, clean: bool = False) -> list[dict[str, Any]]:
    out = []
    for path in sorted(campaign.glob("*/*/seed-*/record.json")):
        tag = path.parts[-3]
        if (tag == "clean") == clean:
            rec = json.loads(path.read_text())
            rec["_path"] = str(path)
            out.append(rec)
    return out


def labels(rec: dict[str, Any], fault: str) -> dict[str, str]:
    """unanimous YES -> 'c' (contaminated), unanimous NO -> 'n', otherwise 'a' (ambiguous)."""
    result = {}
    for key, per_fault in rec["oracle"].items():
        votes = list(per_fault[fault].values())
        result[key] = "c" if all(votes) else "n" if not any(votes) else "a"
    return result


def prf(suspended: set[str], lab: dict[str, str], targets: list[str],
        ambiguous_as: str = "skip") -> dict[str, float | None]:
    def cls(a: str) -> str:
        return lab[a] if lab[a] != "a" else ambiguous_as
    contaminated = {a for a in targets if cls(a) == "c"}
    clean = {a for a in targets if cls(a) == "n"}
    tp = len(suspended & contaminated)
    fp = len(suspended & clean)
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / len(contaminated) if contaminated else None
    f1 = (2 * precision * recall / (precision + recall)
          if precision is not None and recall is not None and precision + recall else
          (0.0 if contaminated else None))
    return {"tp": tp, "fp": fp, "precision": precision, "recall": recall, "f1": f1,
            "residual": len(contaminated - suspended), "collateral": fp,
            "contaminated": len(contaminated)}


def tune(campaign: Path) -> dict[str, float]:
    dev = [r for r in records(campaign) if r["config"]["seed"] in DEV_SEEDS]
    if not dev:
        raise SystemExit("no dev records")
    best: dict[str, float] = {}
    for metric in ("tfidf", "embed"):
        grid = [round(0.05 * i, 2) for i in range(1, 20)]
        scored = []
        for tau in grid:
            f1s = []
            for rec in dev:
                lab = labels(rec, rec["config"]["fault"])
                targets = [a for a in rec["universe"] if a != rec["root"]]
                chosen = {a for a in targets if rec["scores"][a][metric] >= tau}
                f1 = prf(chosen, lab, targets)["f1"]
                if f1 is not None:
                    f1s.append(f1)
            scored.append((mean(f1s) if f1s else 0.0, -tau, tau))
        best[metric] = max(scored)[2]
        best[metric + "_dev_f1"] = max(scored)[0]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "thresholds.json").write_text(json.dumps({**best, "dev_runs": len(dev)}, indent=1))
    return best


def a12(x: list[float], y: list[float]) -> float:
    gt = sum(1.0 if a > b else 0.5 if a == b else 0.0 for a in x for b in y)
    return gt / (len(x) * len(y))


def boot(values: list[float], seed: int = 20261106, n: int = 2000) -> tuple[float, float]:
    rng = random.Random(seed)
    means = sorted(mean(rng.choices(values, k=len(values))) for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n) - 1]


def holm(pvalues: dict[str, float]) -> dict[str, float]:
    order = sorted(pvalues, key=pvalues.get)  # type: ignore[arg-type]
    adjusted, running = {}, 0.0
    for i, key in enumerate(order):
        running = max(running, min(1.0, (len(order) - i) * pvalues[key]))
        adjusted[key] = running
    return adjusted


def kappa(pairs: list[tuple[bool, bool]]) -> float:
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    pa = sum(a for a, _ in pairs) / n
    pb = sum(b for _, b in pairs) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def report(campaign: Path) -> dict[str, Any]:
    runs = [r for r in records(campaign) if r["config"]["seed"] not in DEV_SEEDS]
    cleans = {(r["config"]["model"], r["config"]["seed"]): r for r in records(campaign, True)}
    rows: list[dict[str, Any]] = []
    for rec in runs:
        fault, root = rec["config"]["fault"], rec["root"]
        lab = labels(rec, fault)
        targets = [a for a in rec["universe"] if a != root]
        clean = cleans.get((rec["config"]["model"], rec["config"]["seed"]))
        base = {"model": rec["config"]["model"], "fault": fault, "seed": rec["config"]["seed"],
                "root_label": lab[root], "artifacts": len(targets),
                "contaminated": sum(lab[a] == "c" for a in targets),
                "ambiguous": sum(lab[a] == "a" for a in targets),
                "contaminated_kinds": "+".join(sorted(rec["artifacts"][a]["kind"]
                                                      for a in targets if lab[a] == "c")),
                "clean_pass": (mean(x["passed"] for x in clean["eval"]["clean"]) if clean else None),
                "seed_only_pass": (mean(x["passed"] for x in clean["eval"]["seed_only"])
                                   if clean else None)}
        for name in REMEDIES:
            suspended = set(rec["remedies"][name]["suspended"]) & set(targets)
            m = prf(suspended, lab, targets)
            m_amb = prf(suspended, lab, targets, ambiguous_as="c")
            ev = rec["eval"][name]
            rows.append({**base, "remedy": name, **m, "recall_amb_c": m_amb["recall"],
                         "precision_amb_c": m_amb["precision"], "suspended": len(suspended),
                         "pass": mean(x["passed"] for x in ev),
                         "signature": mean(bool(x["fault_signature"]) for x in ev),
                         "seconds": rec["timing"].get(name if name.startswith("H") else
                                                      {"R2_tfidf": "R2_tfidf", "R3_embed": "R3_embed",
                                                       "R4_judge": "R4_judge"}.get(name, ""), 0.0)})
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "live_runs.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    def col(name: str, key: str, cond: Any = None) -> list[float]:
        return [r[key] for r in rows if r["remedy"] == name and r[key] is not None
                and (cond is None or cond(r))]

    summary: dict[str, Any] = {"runs": len(runs), "campaign": str(campaign),
                               "propagated_runs": sum(1 for r in rows if r["remedy"] == "none"
                                                      and r["contaminated"] > 0),
                               "root_adopted": sum(1 for r in rows if r["remedy"] == "none"
                                                   and r["root_label"] == "c"),
                               "remedies": {}}
    propagated = lambda r: r["contaminated"] > 0  # noqa: E731
    for name in REMEDIES:
        entry: dict[str, Any] = {}
        for key in ("precision", "recall", "f1", "residual", "collateral", "pass", "signature",
                    "suspended", "seconds", "recall_amb_c", "precision_amb_c"):
            values = col(name, key, propagated if key in ("recall", "f1", "recall_amb_c")
                         else None)
            if values:
                lo, hi = boot(values)
                entry[key] = {"mean": mean(values), "sd": pstdev(values), "lo": lo, "hi": hi,
                              "n": len(values)}
        summary["remedies"][name] = entry
    tests: dict[str, Any] = {}
    for key in ("recall", "f1", "residual", "pass", "signature", "collateral"):
        pvals, detail = {}, {}
        for name in REMEDIES:
            if name == "H":
                continue
            pairs = [(h[key], o[key]) for h in rows if h["remedy"] == "H"
                     for o in rows if o["remedy"] == name and o["seed"] == h["seed"]
                     and o["fault"] == h["fault"] and o["model"] == h["model"]
                     and h[key] is not None and o[key] is not None]
            if not pairs:
                continue
            x, y = [p[0] for p in pairs], [p[1] for p in pairs]
            diffs = [a - b for a, b in pairs]
            p = 1.0 if all(d == 0 for d in diffs) else float(wilcoxon(x, y).pvalue)
            pvals[name] = p
            detail[name] = {"n": len(pairs), "p": p, "a12": a12(x, y),
                            "mean_diff": mean(diffs)}
        for name, adj in holm(pvals).items():
            detail[name]["p_holm"] = adj
        tests[key] = detail
    summary["tests_H_vs"] = tests
    pairs = [(v[j1], v[j2]) for rec in [*runs, *cleans.values()] for per in rec["oracle"].values()
             for v in per.values() for j1, j2 in [tuple(v)]]
    summary["judge_agreement"] = {"items": len(pairs), "raw": mean(a == b for a, b in pairs),
                                  "kappa": kappa(pairs)}
    fp = {}
    for fault in ("F1", "F2", "F3"):
        votes = [labels(c, fault)[a] for c in cleans.values() for a in c["universe"]]
        fp[fault] = {"artifacts": len(votes), "contaminated": votes.count("c"),
                     "ambiguous": votes.count("a")}
    summary["clean_run_labels"] = fp
    summary["clean_pass"] = {"clean": mean(mean(x["passed"] for x in c["eval"]["clean"])
                                           for c in cleans.values()),
                             "seed_only": mean(mean(x["passed"] for x in c["eval"]["seed_only"])
                                               for c in cleans.values())} if cleans else {}
    summary["cost"] = {
        "evolve_seconds": mean(r["timing"]["evolve_total"] for r in runs),
        "engine_seconds": mean(r["timing"]["engine_total"] for r in runs),
        "history_events": mean(r["history_events"] for r in runs),
        "llm_calls": mean(r["llm"]["calls"] for r in runs),
        "tokens_in": mean(r["llm"]["tokens_in"] for r in runs),
        "tokens_out": mean(r["llm"]["tokens_out"] for r in runs)}
    (OUT / "live_summary.json").write_text(json.dumps(summary, indent=1))
    return summary


if __name__ == "__main__":
    command, target = sys.argv[1], Path(sys.argv[2])
    result = tune(target) if command == "tune" else report(target)
    print(json.dumps(result, indent=1)[:4000])
