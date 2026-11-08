"""Insert traceable measured macros and inline tables into the single paper source."""
import json
from pathlib import Path


def main():
    summary = json.loads(Path("results/processed/summary.json").read_text())
    coverage_path = Path("results/validation/coverage.json")
    if not coverage_path.exists():
        coverage_path = Path("build/coverage.json")
    coverage = json.loads(coverage_path.read_text())["totals"]
    selection = Path("results/validation/mutation_selection.json")
    mutation_path = json.loads(selection.read_text())["report"] if selection.exists() else "results/validation/mutation.json"
    mutation = json.loads(Path(mutation_path).read_text())
    real = json.loads(Path("results/processed/realistic.json").read_text())
    macros = {}
    def add(name, value):
        macros[name] = str(value)
    add("RawRecords", summary["records"])
    add("TraceCases", len(list(Path(summary["campaign"]).glob("E01*/*/*/record.json"))))
    add("HistoryImpact", f"{summary['rq1']['B0_file_history:impact']['mean']:.3f}")
    add("LexicalImpact", f"{summary['rq1']['B1_lexical:impact']['mean']:.3f}")
    add("CheckerComparisons", len(summary["checking"]))
    add("CheckerAgreements", sum(r["agree"] for r in summary["checking"]))
    add("Counterexamples", len(summary["counterexamples"]))
    add("ReplaySuccesses", sum(not r["implementation_rejected"] and bool(r["implementation_violation"])
                               for r in summary["counterexamples"]))
    add("WitnessMin", min(r["length"] for r in summary["counterexamples"]))
    add("WitnessMax", max(r["length"] for r in summary["counterexamples"]))
    add("LineCoverage", f"{coverage['percent_statements_covered']:.1f}")
    add("BranchCoverage", f"{coverage['percent_branches_covered']:.1f}")
    add("MutationKilled", mutation["killed"])
    add("MutationTotal", mutation["total"])
    add("GraphMilliseconds", f"{1000*summary['robustness']['graph_2048']['seconds']['mean']:.2f}")
    add("GraphKilobytes", f"{summary['robustness']['graph_2048']['peak_bytes']['mean']/1024:.1f}")
    add("MonitorMilliseconds", f"{1000*summary['conformance']['replay_seconds']['mean']:.1f}")
    add("MonitorOverhead", f"{summary['conformance']['time_overhead_percent']['mean']:.1f}")
    add("OmissionDetections", summary["conformance"]["omitted_event"]["positives"])
    add("PublicRevisions", real["revision_count"])
    add("PublicEvents", real["event_count"])
    correspondence = summary.get("correspondence", [])
    add("MappedTransitions", sum(r["attempted_transitions"] for r in correspondence))
    add("MappedMismatches", sum(len(r["mismatches"]) for r in correspondence))
    add("LinterFOne", f"{summary.get('linter', {}).get('f1', {}).get('mean', 0):.3f}")
    runtime = summary.get("runtime_cost", [])
    add("AdmissionMilliseconds", f"{1000*next((r['mean'] for r in runtime if r['artifacts']==32 and r['phase']=='admission'),0):.1f}")
    add("WithdrawalMilliseconds", f"{1000*next((r['mean'] for r in runtime if r['artifacts']==32 and r['phase']=='withdrawal'),0):.1f}")
    for fraction in (0, .25, .5, .75, 1):
        key = f"{fraction}:ours:impact"
        entry = summary["capture"].get(key) or summary["capture"][f"{float(fraction)}:ours:impact"]
        add({0:"CaptureZero",.25:"CaptureQuarter",.5:"CaptureHalf",.75:"CaptureThreeQuarters",1:"CaptureFull"}[fraction],
            f"{entry['mean']:.3f}")
    generated = "\n".join("\\newcommand{\\"+name+"}{"+value+"}" for name,value in macros.items())
    generated += "\n\\newcommand{\\AccuracyRows}{\n"
    labels = {"B0_file_history":"B0: within-file history", "B1_lexical":"B1: token similarity",
              "B2_capture_only":"B2: capture only", "ours":"HEARTNESS"}
    for method, label in labels.items():
        cells = []
        for task in ("origins", "descendants", "impact"):
            v = summary["rq1"][method+":"+task]
            cells.append(f"{v['mean']:.3f} [{v['lo']:.3f},{v['hi']:.3f}]")
        generated += label + " & " + " & ".join(cells) + " \\\\\n"
    generated += "}\n\\newcommand{\\CheckerRows}{\n"
    for r in sorted(summary["checking"], key=lambda r:(r["topology"],r["mutant"])):
        generated += f"{r['topology']} & {r['mutant'] or 'reference'} & {r['states']:,} & "
        generated += ("--" if r["safe"] else str(r["length"])) + " & " + ("safe in bound" if r["safe"] else "violation") + " \\\\\n"
    generated += "}\n\\newcommand{\\ScaleRows}{\n"
    for r in sorted(summary["scale"], key=lambda r:(r["n"],r["topology"])):
        if r["depth"] != 10:
            continue
        generated += f"{r['n']} & {r['topology']} & {r['states']:,} & {r['seconds']:.3f} & " + ("yes" if r["complete"] else "capped") + " \\\\\n"
    generated += "}\n\\newcommand{\\SearchRows}{\n"
    for mutant in ("reference","P2","P3","P4","P8","P9"):
        cells = []
        for method in ("random","hypothesis","bfs"):
            r = next(r for r in summary["search"] if r["mutant"]==mutant and r["method"]==method)
            cells.append(f"{r['detection']['positives']}/30")
        generated += mutant + " & " + " & ".join(cells) + " \\\\\n"
    generated += "}\n"
    path = Path("docs/TSE/main.tex")
    paper = path.read_text()
    start = paper.index("% BEGIN MEASURED RESULTS")
    stop = paper.index("% END MEASURED RESULTS") + len("% END MEASURED RESULTS")
    paper = paper[:start] + "% BEGIN MEASURED RESULTS\n" + generated + "% END MEASURED RESULTS" + paper[stop:]
    path.write_text(paper)
    Path("results/processed/paper_macro_index.json").write_text(json.dumps(
        {"macros": macros, "summary": "results/processed/summary.json", "campaign": summary["campaign"],
         "coverage": str(coverage_path), "mutation": mutation_path,
         "public_replay": "results/processed/realistic.json"}, indent=2)+"\n")


if __name__ == "__main__":
    main()
