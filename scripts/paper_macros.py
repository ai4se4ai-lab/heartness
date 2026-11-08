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
# Reported live study (Fir, H100): E = HumanEval+ x ExpeL-style, C = HumanEval+ x curate.
LIVE = {"E": Path("results/processed/live/live-fir"),
        "C": Path("results/processed/live/live-fir-curate"),
        "L": Path("results/processed/live/live-fir-late")}  # late-fault curation slice
LIVE_RAW = {"E": Path("results/raw/live-fir"), "C": Path("results/raw/live-fir-curate")}
PILOT = Path("results/raw/live-qwen25-7b")  # local pilot: threshold tuning (dev seeds) only
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
    for fraction, word in ((0, "Zero"), (0.5, "Half"), (1, "Full")):
        for key, label in (("ours", "Ours"), ("B1_lexical", "Lexical")):
            entry = s["paraphrase"].get(f"{fraction}:{key}:impact")
            if entry:
                add(f"Para{label}{word}", f3(entry["mean"]), src)
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
                     f"{'yes' if r['complete'] else 'capped'} \\\\\n")
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
    add("GuardRemovedAlarms", sum(bool(p["full"]["target_alarm"]) != bool(p["removed"]["target_alarm"])
                                  for p in prop), src)
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
         "HS_embed": "HS$_{\\mathrm{emb}}$", "T_since_fault": "T rollback before fault",
         "A_all_learned": "A reset learned state", "H_faulty_root": "H$_{\\mathrm{faulty}}$",
         "H_EMEfail": "H$_{\\mathrm{EME\\text{-}fail}}$"}
SHORT = {"qwen2.5-coder:7b": "Qwen2.5-Coder 7B", "llama3.1:8b": "Llama 3.1 8B",
         "deepseek-coder-v2:16b": "DS-Coder-V2 16B", "gemma2:9b": "Gemma 2 9B",
         "granite3.3:8b": "Granite 3.3 8B"}
WORD = {"none": "None", "R1_delete_root": "Rone", "R2_tfidf": "Rtwo", "R3_embed": "Rthree",
        "R4_judge": "Rfour", "H": "H", "H_noEME": "HnoEME", "H_noDeps": "HnoDeps",
        "H_local": "Hlocal", "HS_judge": "HSjudge", "HS_embed": "HSembed",
        "T_since_fault": "Tcut", "A_all_learned": "Areset", "H_faulty_root": "Hfaulty",
        "H_EMEfail": "HEMEfail"}


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
    if s["judge_agreement"].get("positive") is not None:
        add(p + "JudgePositive", f2(s["judge_agreement"]["positive"]), src)
    if "hs_judge_differs_from_r4_propagated" in s.get("structure", {}):
        add(p + "HSjudgeDiffersRfour", s["structure"]["hs_judge_differs_from_r4_propagated"], src)
    add(p + "PassClean", f2(s["clean_pass"].get("clean")), src)
    add(p + "PassSeed", f2(s["clean_pass"].get("seed_only")), src)
    cl = s["clean_run_labels"]
    add(p + "CleanFalseLabels", sum(v["contaminated"] for v in cl.values()), src)
    add(p + "CleanLabelItems", sum(v["artifacts"] for v in cl.values()), src)
    add(p + "CleanAmbLabels", sum(v["ambiguous"] for v in cl.values()), src)
    for metric, kw in (("tfidf", "Tfidf"), ("embed", "Embed")):
        b = s.get("oracle_tuned_bound", {}).get(metric)
        if b:
            add(p + "Bound" + kw + "Rec", f2(b["recall"]), src)
    for name, word in WORD.items():
        r = s["remedies"].get(name)
        if not r:
            continue
        for key, kw in (("precision", "Prec"), ("recall", "Rec"), ("f1", "Fone"),
                        ("residual", "Resid"), ("collateral", "Coll"), ("pass", "Pass"),
                        ("signature", "Sig"), ("suspended", "Susp"),
                        ("precision_prop", "PrecProp"), ("suspended_prop", "SuspProp"),
                        ("collateral_prop", "CollProp"), ("pass_prop", "PassProp"),
                        ("signature_prop", "SigProp"), ("recall_amb_c", "RecAmb")):
            if key in r:
                add(p + word + kw, f2(r[key]["mean"]), src)
    for name, word in WORD.items():
        r = s["remedies"].get(name, {})
        if "seconds" in r:
            add(p + word + "Ms", f"{1000 * r['seconds']['mean']:.1f}", src)
    tests = s["tests_H_vs"]
    for key, kw in (("residual", "Resid"), ("recall", "Rec"), ("pass", "Pass"),
                    ("collateral", "Coll"), ("f1", "Fone"), ("signature", "Sig"),
                    ("pass_prop", "PassProp"), ("signature_prop", "SigProp")):
        for name, word in WORD.items():
            t = tests.get(key, {}).get(name)
            if t:
                ph = t.get("p_holm")
                # includes the relation, used as $p\Macro$: "=0.338" or "<0.001"
                add(p + "Test" + kw + word + "P", "--" if ph is None else
                    f"={ph:.3f}" if ph >= .001 else "<0.001", src)
                add(p + "Test" + kw + word + "Hi", t.get("H_higher", 0), src)
                add(p + "Test" + kw + word + "Lo", t.get("H_lower", 0), src)
                add(p + "Test" + kw + word + "A", f2(t["a12"]), src)
    table = f"\\newcommand{{\\{p}Rows}}{{\n"
    for name in ("none", "R1_delete_root", "T_since_fault", "A_all_learned", "R2_tfidf",
                 "R3_embed", "R4_judge", "H", "HS_judge", "HS_embed", "H_noEME", "H_noDeps",
                 "H_local", "H_faulty_root", "H_EMEfail"):
        r = s["remedies"].get(name)
        if not r:
            continue
        cell = []
        for key in ("suspended", "suspended_prop", "precision_prop", "recall", "f1", "residual",
                    "collateral", "pass", "signature"):
            e = r.get(key)
            cell.append("--" if not e else f"{e['mean']:.2f}")
        if name in ("H", "R2_tfidf"):
            table += "\\midrule\n"
        if name == "H_noEME":
            table += "\\midrule\n"
        table += LABEL[name] + " & " + " & ".join(cell) + " \\\\\n"
    table += "}\n"
    b = s.get("oracle_tuned_bound", {})
    for metric, kw in (("tfidf", "Tfidf"), ("embed", "Embed")):
        if metric in b:
            add(p + "Bound" + kw + "Fone", f2(b[metric]["f1"]), src)
            add(p + "Bound" + kw + "Tau", f2(b[metric]["tau"]), src)
    add(p + "NotAdopted", s["not_adopted_runs"], src)
    add(p + "Faulty", s["runs"] + s["not_adopted_runs"], src)
    # per-generator breakdown (no-remedy rows carry the run-level facts)
    models = sorted({r["model"] for r in none})
    mt = f"\\newcommand{{\\{p}ModelRows}}{{\n"
    for m in models:
        rs = [r for r in none if r["model"] == m]
        hs = [r for r in rows if r["remedy"] == "H" and r["model"] == m]
        mt += (f"{SHORT.get(m, m)} & {len(rs)} & {sum(r['root_label'] == 'c' for r in rs)} & "
               f"{sum(int(r['contaminated']) > 0 for r in rs)} & "
               f"{sum(int(r['contaminated']) for r in rs)} & "
               f"{mean(int(r['artifacts']) for r in rs):.1f} & "
               f"{mean(float(r['suspended']) for r in hs):.1f} & "
               f"{mean(float(r['clean_pass']) for r in rs if r['clean_pass']):.2f} \\\\\n")
    mt += "}\n"
    per_fault = {f: [r for r in none if r["fault"] == f] for f in ("F1", "F2", "F3")}
    for f, rs in per_fault.items():
        w = {"F1": "Fone", "F2": "Ftwo", "F3": "Fthree"}[f]
        add(p + w + "Adopted", sum(r["root_label"] == "c" for r in rs), str(base / "live_runs.csv"))
        add(p + w + "Propagated", sum(int(r["contaminated"]) > 0 for r in rs),
            str(base / "live_runs.csv"))
    hrows = {r["seed"] + r["model"] + r["fault"]: r for r in rows if r["remedy"] == "H"}
    for name, word in (("H_noEME", "HnoEME"), ("H_noDeps", "HnoDeps")):
        diff = sum(1 for r in rows if r["remedy"] == name
                   and r["suspended"] != hrows[r["seed"] + r["model"] + r["fault"]]["suspended"])
        add(p + word + "Differs", diff, str(base / "live_runs.csv"))
    def fmt(n: int) -> str:
        return f"{n:,}".replace(",", "{,}")
    nz = s.get("noise_independent", {})
    if nz.get("pairs"):
        add(p + "NoiseFlips", nz["flips"], src)
        add(p + "NoisePairs", fmt(nz["pairs"]), src)
        add(p + "NoiseRate", f"{100 * nz['rate']:.1f}", src)
        add(p + "NoiseFlipsNoLearned", nz.get("flips_without_learned_state", 0), src)
    for block, v in s.get("selectivity", {}).items():
        w = {"1-6": "One", "7-12": "Two", "13-18": "Three", "19-24": "Four"}.get(block)
        if w:
            add(p + "Sel" + w + "Roots", fmt(v["roots"]), src)
            add(p + "Sel" + w + "Ratio", f2(v["ratio"]), src)
            add(p + "Sel" + w + "RatioFail", f2(v["ratio_eme_fail"]), src)
            add(p + "Sel" + w + "Strict", f"{100 * v['strict']:.0f}", src)
            add(p + "Sel" + w + "Later", f"{v.get('later', 0):.1f}", src)
            add(p + "Sel" + w + "Spared", f"{v.get('spared', 0):.1f}", src)
            add(p + "Sel" + w + "ReachFinal", fmt(v.get("reach_final_profiles", 0)), src)
    st = s.get("structure")
    if st:
        for k, w in (("memory", "Memory"), ("skill", "Skill"), ("profile", "Profile"),
                     ("insight", "Insight")):
            add(p + "Cont" + w, st["contaminated_by_kind"].get(k, 0), src)
            for name, rw in (("R3_embed", "Rthree"), ("R4_judge", "Rfour"), ("R2_tfidf", "Rtwo")):
                add(p + "Miss" + rw + w, st["missed_by_kind"][name].get(k, 0), src)
        for name, rw in (("R3_embed", "Rthree"), ("R4_judge", "Rfour"), ("R2_tfidf", "Rtwo")):
            add(p + "MissRuns" + rw, st["missed_runs"][name], src)
            add(p + "MissRunsComposed" + rw, st.get("missed_runs_composed", {}).get(name, 0), src)
        add(p + "CutSubset", st["closure_subset_of_cut"], src)
        add(p + "CutStrict", st["closure_strictly_smaller"], src)
        add(p + "CutGap", sum(st["cut_minus_closure_by_kind"].values()), src)
        add(p + "CutGapBeforeCompose", st["cut_minus_closure_before_first_compose"], src)
        add(p + "ProfilesInClosure", st["runs_all_postfault_profiles_in_closure"], src)
        add(p + "EMEOnlyRuns", len(st["eme_only"]), src)
        add(p + "EMEOnlyItems", sum(len(x["missed"]) for x in st["eme_only"]), src)
        for task, w in (("2", "Two"), ("8", "Eight"), ("9", "Nine")):
            v = st.get("closure_strictly_smaller_by_fault_task", {}).get(task)
            if v:
                add(p + "CutStrictTask" + w, v[0], src)
                add(p + "RunsTask" + w, v[1], src)
        add(p + "FaultyMissAmbiguous", st.get("faulty_root_misses_root_labels", {}).get("a", 0), src)
        add(p + "ProfileRuns", st.get("runs_with_contaminated_profile", 0), src)
        for name, w in (("HS_judge", "HSjudge"), ("HS_embed", "HSembed")):
            rv = st.get("revalidation_rejected", {}).get(name)
            if rv:
                add(p + w + "Rejected", rv["rejected"], src)
                add(p + w + "RejectedRuns", rv["runs"], src)
                add(p + w + "RejectedCont", rv["contaminated"], src)
    pd = s.get("pass_prop_H_minus_none", {})
    if pd:
        add(p + "PassPropHigher", pd["higher"], src)
        add(p + "PassPropLower", pd["lower"], src)
    rp = s.get("roots_per_run", {})
    if rp:
        tot = sum(rp.values())
        add(p + "RootsMean", f"{sum(int(k) * v for k, v in rp.items()) / tot:.1f}", src)
        add(p + "RootsMax", max(int(k) for k in rp), src)
        add(p + "RootsSingle", rp.get("1", 0), src)
    fp = s.get("fault_positions", {})
    if fp:
        add(p + "FaultPositions", ", ".join(str(int(k) + 1) for k in sorted(fp, key=int)), src)
    add(p + "AdoptedAmb", s.get("adopted_with_ambiguous", 0), src)
    add(p + "CleanRevisions", sum(v["artifacts"] for v in s["clean_run_labels"].values()) // 3, src)
    ad = s.get("adopted", {})
    for name, word in WORD.items():
        if name in ad:
            add(p + "Adopt" + word + "Coll", f2(ad[name]["collateral"]), src)
            add(p + "Adopt" + word + "Susp", f2(ad[name]["suspended"]), src)
    curve = s.get("threshold_curve", {})
    for metric, kw in (("tfidf", "Tfidf"), ("embed", "Embed")):
        if curve.get(metric):
            mt += (f"\\newcommand{{\\{p}Curve{kw}}}{{" + " ".join(
                f"({c['tau']},{c['f1']:.3f})" for c in curve[metric]) + "}\n")
    c = s["cost"]
    add(p + "EvolveMinutes", f"{c['evolve_seconds'] / 60:.1f}", src)
    add(p + "EngineSeconds", f2(c["engine_seconds"]), src)
    add(p + "EnginePercent", f2(100 * c["engine_seconds"] / c["evolve_seconds"]), src)
    add(p + "EnginePercentMax", f2(c.get("engine_percent_max", 0)), src)
    add(p + "HistoryEvents", f"{c['history_events']:.0f}", src)
    add(p + "LLMCalls", f"{c['llm_calls']:.0f}", src)
    add(p + "TokensIn", f"{c['tokens_in'] / 1000:.0f}", src)
    add(p + "TokensOut", f"{c['tokens_out'] / 1000:.0f}", src)
    return table + mt


def live_design() -> None:
    recs = sorted(x for tag in ("E", "C") for x in LIVE_RAW[tag].rglob("seed-*/record.json"))
    if not recs:
        return
    data = [json.loads(x.read_text()) for x in recs]
    for d in data:  # curation records predate the policy field (same default as process.py)
        d["config"].setdefault("policy", "curate")
    src = "results/raw/live-fir*/**/record.json"
    one = data[0]
    add("LiveEvalTasks", len(one["eval_tasks"]), src)
    add("LiveEvolveTasks", one["config"]["n_evolve"], src)
    add("LiveSeeds", len({d["config"]["seed"] for d in data}), src)
    add("LiveModels", len({d["config"]["model"] for d in data}), src)
    add("LivePolicies", len({d["config"]["policy"] for d in data}), src)
    add("LiveTotalRuns", len(data), src)
    add("LiveFaultyRuns", sum(d["config"]["fault"] != "clean" and "fault_index" in d
                              and x.parts[-3] != "clean" for d, x in zip(data, recs)), src)
    add("LiveCleanRuns", sum(x.parts[-3] == "clean" for x in recs), src)
    calls = sum(d["llm"]["calls"] for d in data)
    add("LiveLLMCalls", f"{calls:,}".replace(",", "{,}"), src)
    add("LiveGPU", one["environment"]["gpu"].replace("NVIDIA ", ""), src)
    add("LiveConditions", len(LABEL), "experiments/live/process.py")
    src_lines = sum(len(f.read_text().splitlines()) for f in Path("src/heartness").glob("*.py"))
    add("SrcLines", f"{src_lines:,}".replace(",", "{,}"), "src/heartness/*.py")
    lines = sum(len(f.read_text().splitlines()) for f in Path("experiments/live").glob("*.py"))
    add("LiveHarnessLines", f"{lines:,}".replace(",", "{,}"), "experiments/live/*.py")
    add("LiveEvalConditions", len(LABEL) - len(("T_since_fault", "A_all_learned", "H_faulty_root",
                                                "H_EMEfail")), "experiments/live/process.py")
    dev = Path("results/raw/hpc/fir/am-20261107-080855/collected/pipeline/inference_devices.tsv")
    if dev.exists():  # which inference device each Ollama server of the curation campaign used
        rows_ = list(csv.DictReader(dev.open(), delimiter="\t"))
        oracle = [r for r in rows_ if r["stage"] == "oracle"]
        add("LiveCOracleCells", len({r["cell"] for r in oracle}), str(dev))
        add("LiveCCPUCells", len({r["cell"] for r in oracle if r["device"] == "cpu"}), str(dev))
    tau = json.loads((PILOT / "thresholds.json").read_text())
    tsrc = str(PILOT / "thresholds.json")
    add("TauTfidf", f"{tau['tfidf']:.2f}", tsrc)
    add("TauEmbed", f"{tau['embed']:.2f}", tsrc)
    add("TauTfidfDev", f"{tau['tfidf_dev_f1']:.3f}", tsrc)
    add("TauEmbedDev", f"{tau['embed_dev_f1']:.3f}", tsrc)
    add("PilotDevRuns", len(list(PILOT.glob("*/*/seed-10[01]/record.json"))), str(PILOT))


def main() -> None:
    validation()
    live_design()
    generated = synthetic() + live("E") + live("C") + live("L")
    summ = [json.loads((LIVE[t] / "live_summary.json").read_text()) for t in ("E", "C")
            if (LIVE[t] / "live_summary.json").exists()]
    if len(summ) == 2:
        add("LivePropagatedAll", sum(x["propagated_runs"] for x in summ),
            "results/processed/live/live-fir*/live_summary.json")
        add("LiveRootAdoptedAll", sum(x["root_adopted"] for x in summ),
            "results/processed/live/live-fir*/live_summary.json")
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
