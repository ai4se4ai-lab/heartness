"""Generate every measured number in docs/TSE/main.tex from processed result files.

Writes the block between '%% BEGIN GENERATED MACROS' and '%% END GENERATED MACROS' and
records, for each macro, the file it was read from (results/processed/paper_macro_index.json).
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean
from typing import Any

PAPER = Path("docs/TSE/main.tex")
SYN = Path("results/processed/summary.json")
LIVE = {"Q": Path("results/processed/live/live-qwen25-7b"),
        "L": Path("results/processed/live/live-llama31-8b")}
macros: dict[str, str] = {}
sources: dict[str, str] = {}


def add(name: str, value: Any, source: str) -> None:
    assert name.isalpha(), name
    macros[name] = str(value)
    sources[name] = source


def f2(x: float | None) -> str:
    return "--" if x is None else f"{x:.2f}"


def f3(x: float | None) -> str:
    return "--" if x is None else f"{x:.3f}"


def synthetic() -> str:
    s = json.loads(SYN.read_text())
    src = str(SYN)
    add("RawRecords", f"{s['records']:,}".replace(",", "{,}"), src)
    add("TraceCases", sum(1 for _ in Path(s["campaign"]).glob("E01*/*/*/record.json")), s["campaign"])
    for key, name in (("B0_file_history", "History"), ("B1_lexical", "Lexical"),
                      ("B2_capture_only", "CaptureOnly"), ("ours", "Ours")):
        for task, tname in (("impact", "Impact"), ("origins", "Origins"),
                            ("descendants", "Descendants")):
            add(f"Syn{name}{tname}", f3(s["rq1"][f"{key}:{task}"]["mean"]), src)
    names = {0: "Zero", .25: "Quarter", .5: "Half", .75: "ThreeQuarters", 1: "Full"}
    for fraction, word in names.items():
        for key, label in (("ours", "Ours"), ("B1_lexical", "Lexical"), ("B0_file_history", "History")):
            entry = s["capture"].get(f"{fraction}:{key}:impact") or s["capture"][
                f"{float(fraction)}:{key}:impact"]
            add(f"Capture{label}{word}", f3(entry["mean"]), src)
    checking = s["checking"]
    add("CheckerComparisons", len(checking), src)
    add("CheckerAgreements", sum(r["agree"] for r in checking), src)
    add("CheckerViolating", sum(not r["safe"] for r in checking), src)
    add("CheckerSafeMutants", sum(r["safe"] and bool(r["mutant"]) for r in checking), src)
    ce = s["counterexamples"]
    add("Counterexamples", len(ce), src)
    add("ReplaySuccesses", sum(bool(r["implementation_violation"]) and not r["implementation_rejected"]
                               for r in ce), src)
    add("MinimalWitnesses", sum(bool(r["shorter_safe"]) for r in ce), src)
    add("WitnessMin", min(r["length"] for r in ce), src)
    add("WitnessMax", max(r["length"] for r in ce), src)
    add("MaxReferenceStates", f"{max(r['states'] for r in checking if not r['mutant']):,}".replace(
        ",", "{,}"), src)
    corr = s["correspondence"]
    add("MappedTransitions", f"{sum(r['attempted_transitions'] for r in corr):,}".replace(",", "{,}"),
        src)
    add("MappedEnabled", sum(r["enabled_transitions"] for r in corr), src)
    add("MappedMismatches", sum(len(r["mismatches"]) for r in corr), src)
    add("LinterFOne", f3(s["linter"]["f1"]["mean"]), src)
    add("LinterCases", s["linter"]["cases"], src)
    add("LinterBenign", s["linter"]["benign_alarms"], src)
    conf = s["conformance"]
    for key, name in (("observed_state_drift", "Drift"), ("invalid_event", "Invalid"),
                      ("omitted_event", "Omitted"), ("hidden_external_effect", "Hidden"),
                      ("benign", "Benign")):
        add(f"Mon{name}", conf[key]["positives"], src)
    add("MonN", conf["benign"]["n"], src)
    rem = s["remediation"]
    add("RemediationRuns", rem["runs"], src)
    add("UnsafeRollbackRejected", rem["unsafe_rollback_rejected"], src)
    add("EffectsRetained", rem["effects_retained"], src)
    rob = s["robustness"]
    add("GraphMilliseconds", f2(1000 * rob["graph_2048"]["seconds"]["mean"]), src)
    add("GraphKilobytes", f"{rob['graph_2048']['peak_bytes']['mean'] / 1024:.0f}", src)
    rt = {(r["artifacts"], r["phase"]): r for r in s["runtime_cost"]}
    for phase, name in (("admission", "Admission"), ("withdrawal", "Withdrawal"),
                        ("monitor", "Monitor"), ("capture", "Capture")):
        add(f"{name}MsThirtyTwo", f"{1000 * rt[(32, phase)]['mean']:.1f}", src)
        add(f"{name}MsFour", f"{1000 * rt[(4, phase)]['mean']:.1f}", src)
    add("HistoryEventsThirtyTwo", f"{rt[(32, 'admission')]['mean_history_events']:.0f}", src)
    search = {(r["mutant"], r["method"]): r["detection"]["positives"] for r in s["search"]}
    rows = ""
    for mutant in ("reference", "P2", "P3", "P4", "P8", "P9"):
        rows += f"{mutant} & " + " & ".join(f"{search[(mutant, m)]}/30" for m in
                                            ("random", "hypothesis", "bfs")) + " \\\\\n"
    table = "\\newcommand{\\SearchRows}{\n" + rows + "}\n"
    rows = ""
    for r in sorted(checking, key=lambda r: (r["mutant"] or "", r["topology"])):
        verdict = "safe in bound" if r["safe"] else f"violation ({r['length']} ops)"
        rows += (f"{r['mutant'] or 'reference'} & {r['topology']} & {r['states']:,} & "
                 f"{r['spin_seconds']:.2f} & {verdict} & {'yes' if r['agree'] else 'NO'} \\\\\n")
    table += "\\newcommand{\\CheckerRows}{\n" + rows.replace(",", "{,}") + "}\n"
    rows = ""
    for r in sorted(s["scale"], key=lambda r: (r["topology"], r["n"])):
        if r["depth"] == 10:
            rows += (f"{r['n']} & {r['topology']} & {r['states']:,} & {r['seconds']:.2f} & "
                     f"{r['projection_states']:,} & {'yes' if r['complete'] else 'capped'} \\\\\n")
    table += "\\newcommand{\\ScaleRows}{\n" + rows.replace(",", "{,}") + "}\n"
    coords = {k: "" for k in ("ours", "B1_lexical", "B0_file_history")}
    for fraction in (0, .25, .5, .75, 1):
        for key in coords:
            e = s["capture"].get(f"{fraction}:{key}:impact") or s["capture"][
                f"{float(fraction)}:{key}:impact"]
            coords[key] += f"({fraction},{e['mean']:.3f}) "
    table += "".join(f"\\newcommand{{\\CaptureCoords{n}}}{{{coords[k]}}}\n" for k, n in
                     (("ours", "Ours"), ("B1_lexical", "Lexical"), ("B0_file_history", "History")))
    prop = s["property_ablations"]
    add("GuardChallenges", len(prop), src)
    add("GuardRemovedAlarms", sum(bool(p["removed"]["target_alarm"]) for p in prop), src)
    return table


def validation() -> None:
    cov = json.loads(Path("results/validation/coverage.json").read_text())["totals"]
    add("LineCoverage", f"{cov['percent_statements_covered']:.1f}", "results/validation/coverage.json")
    add("BranchCoverage", f"{cov['percent_branches_covered']:.1f}", "results/validation/coverage.json")
    v = json.loads(Path("results/validation/tests.json").read_text())
    add("TestCount", v["passed"], "results/validation/tests.json")
    report = json.loads(Path("results/validation/mutation_selection.json").read_text())["report"]
    mut = json.loads(Path(report).read_text())
    add("MutationKilled", mut["killed"], report)
    add("MutationTotal", mut["total"], report)
    real = json.loads(Path("results/processed/realistic.json").read_text())
    add("PublicRevisions", real["revision_count"], "results/processed/realistic.json")
    add("PublicEvents", real["event_count"], "results/processed/realistic.json")


LABEL = {"none": "No remedy", "R1_delete_root": "R1 delete root", "R2_tfidf": "R2 TF-IDF",
         "R3_embed": "R3 embedding", "R4_judge": "R4 LLM judge", "H": "\\sys{} (H)",
         "H_noEME": "H$_{\\neg\\mathrm{EME}}$", "H_noDeps": "H$_{\\neg\\mathrm{dep}}$",
         "H_local": "H$_{\\mathrm{local}}$", "HS_judge": "HS$_{\\mathrm{judge}}$",
         "HS_embed": "HS$_{\\mathrm{emb}}$"}
WORD = {"none": "None", "R1_delete_root": "Rone", "R2_tfidf": "Rtwo", "R3_embed": "Rthree",
        "R4_judge": "Rfour", "H": "H", "H_noEME": "HnoEME", "H_noDeps": "HnoDeps",
        "H_local": "Hlocal", "HS_judge": "HSjudge", "HS_embed": "HSembed"}


def live(tag: str) -> str:
    base = LIVE[tag]
    summ_path = base / "live_summary.json"
    if not summ_path.exists():
        return ""
    s = json.loads(summ_path.read_text())
    src = str(summ_path)
    rows = list(csv.DictReader((base / "live_runs.csv").open()))
    p = "Live" + tag
    add(p + "Runs", s["runs"], src)
    add(p + "Propagated", s["propagated_runs"], src)
    add(p + "RootAdopted", s["root_adopted"], src)
    none = [r for r in rows if r["remedy"] == "none"]
    add(p + "Contaminated", sum(int(r["contaminated"]) for r in none), str(base / "live_runs.csv"))
    add(p + "Ambiguous", sum(int(r["ambiguous"]) for r in none), str(base / "live_runs.csv"))
    add(p + "MeanArtifacts", f"{mean(int(r['artifacts']) for r in none):.1f}",
        str(base / "live_runs.csv"))
    add(p + "Kappa", f2(s["judge_agreement"]["kappa"]), src)
    add(p + "JudgeItems", s["judge_agreement"]["items"], src)
    add(p + "JudgeRaw", f"{100 * s['judge_agreement']['raw']:.1f}", src)
    add(p + "PassClean", f2(s["clean_pass"].get("clean")), src)
    add(p + "PassSeed", f2(s["clean_pass"].get("seed_only")), src)
    cl = s["clean_run_labels"]
    add(p + "CleanFalseLabels", sum(v["contaminated"] for v in cl.values()), src)
    add(p + "CleanLabelItems", sum(v["artifacts"] for v in cl.values()), src)
    for name, word in WORD.items():
        r = s["remedies"].get(name)
        if not r:
            continue
        for key, kw in (("precision", "Prec"), ("recall", "Rec"), ("f1", "Fone"),
                        ("residual", "Resid"), ("collateral", "Coll"), ("pass", "Pass"),
                        ("signature", "Sig"), ("suspended", "Susp")):
            if key in r:
                add(p + word + kw, f2(r[key]["mean"]), src)
    tests = s["tests_H_vs"]
    for key, kw in (("residual", "Resid"), ("recall", "Rec"), ("pass", "Pass"),
                    ("collateral", "Coll"), ("f1", "Fone")):
        for name, word in WORD.items():
            t = tests.get(key, {}).get(name)
            if t:
                add(p + "Test" + kw + word + "P", f"{t['p_holm']:.3f}" if t["p_holm"] >= .001
                    else "<0.001", src)
                add(p + "Test" + kw + word + "A", f2(t["a12"]), src)
    table = f"\\newcommand{{\\{p}Rows}}{{\n"
    for name in ("none", "R1_delete_root", "R2_tfidf", "R3_embed", "R4_judge", "H", "HS_judge",
                 "HS_embed", "H_noEME", "H_noDeps", "H_local"):
        r = s["remedies"].get(name)
        if not r:
            continue
        cell = []
        for key in ("suspended", "precision", "recall", "f1", "residual", "collateral", "pass",
                    "signature"):
            e = r.get(key)
            cell.append("--" if not e else f"{e['mean']:.2f}")
        if name == "H":
            table += "\\midrule\n"
        if name == "H_noEME":
            table += "\\midrule\n"
        table += LABEL[name] + " & " + " & ".join(cell) + " \\\\\n"
    table += "}\n"
    c = s["cost"]
    add(p + "EvolveMinutes", f"{c['evolve_seconds'] / 60:.1f}", src)
    add(p + "EngineSeconds", f2(c["engine_seconds"]), src)
    add(p + "EnginePercent", f2(100 * c["engine_seconds"] / c["evolve_seconds"]), src)
    add(p + "HistoryEvents", f"{c['history_events']:.0f}", src)
    add(p + "LLMCalls", f"{c['llm_calls']:.0f}", src)
    return table


def live_design() -> None:
    raws = [Path("results/raw/live-qwen25-7b"), Path("results/raw/live-llama31-8b")]
    recs = [x for r in raws for x in r.glob("*/*/seed-*/record.json")]
    one = json.loads(next(iter(recs)).read_text())
    src = "results/raw/live-*/**/record.json"
    add("LiveEvalTasks", len(one["eval_tasks"]), src)
    add("LiveEvolveTasks", one["config"]["n_evolve"], src)
    seeds = {json.loads(x.read_text())["config"]["seed"] for x in recs} - {100, 101}
    add("LiveSeeds", len(seeds), src)
    faulty = [x for x in recs if x.parts[-3] != "clean" and not x.parts[-2].startswith("seed-10")]
    add("LiveRuns", len([x for x in faulty if "qwen" in x.parts[-4]]), src)
    add("LiveCleanRuns", len([x for x in recs if x.parts[-3] == "clean" and "qwen" in x.parts[-4]]), src)
    add("LiveTotalRuns", len(recs), src)
    cache = sum(len(c.read_text().splitlines()) for r in raws for c in (r / "llm_cache").glob("*.jsonl"))
    add("LiveLLMCalls", f"{cache:,}".replace(",", "{,}"), "results/raw/live-*/llm_cache")
    add("LiveConditions", len(LABEL), "experiments/live/process.py")
    tau = json.loads(Path("results/raw/live-qwen25-7b/thresholds.json").read_text())
    add("TauTfidf", f"{tau['tfidf']:.2f}", "results/raw/live-qwen25-7b/thresholds.json")
    add("TauEmbed", f"{tau['embed']:.2f}", "results/raw/live-qwen25-7b/thresholds.json")


def main() -> None:
    validation()
    live_design()
    generated = synthetic() + live("Q") + live("L")
    body = "\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in macros.items())
    paper = PAPER.read_text()
    start = paper.index("%% BEGIN GENERATED MACROS")
    stop = paper.index("%% END GENERATED MACROS")
    paper = (paper[:start] + "%% BEGIN GENERATED MACROS (scripts/paper_macros.py; do not edit by hand)\n"
             + body + "\n" + generated + paper[stop:])
    PAPER.write_text(paper)
    Path("results/processed/paper_macro_index.json").write_text(json.dumps(
        {"macros": macros, "sources": sources}, indent=1) + "\n")
    print(len(macros), "macros")


if __name__ == "__main__":
    main()
