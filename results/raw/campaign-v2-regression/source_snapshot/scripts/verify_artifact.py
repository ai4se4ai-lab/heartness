"""Audit bundled evidence references and the final typeset source."""
import json
import re
from pathlib import Path


def main():
    summary = json.loads(Path("results/processed/summary.json").read_text())
    campaign = Path(summary["campaign"])
    manifest = json.loads((campaign/"manifest.json").read_text())
    assert summary["records"] == manifest["records"] == len(list(campaign.glob("E*/*/*/record.json")))
    assert all(r["agree"] for r in summary["checking"])
    assert all(not r["implementation_rejected"] and r["shorter_safe"] for r in summary["counterexamples"])
    assert all(not r["mismatches"] for r in summary["correspondence"])
    for r in summary["checking"] + summary["counterexamples"] + summary["scale"]:
        assert Path(r["raw"]).exists()
    paper = Path("docs/TSE/main.tex").read_text()
    bibliography = Path("docs/TSE/references.bib").read_text()
    keys = set(re.findall(r"@\w+\{([^,]+)", bibliography))
    used = {key for group in re.findall(r"\\cite\{([^}]+)\}", paper) for key in group.split(",")}
    assert used <= keys, used-keys
    assert not re.search(r"\\(?:includegraphics|input|include)\s*\{", paper)
    log = Path("build/paper/main.log").read_text()
    assert "Output written" in log
    assert "Overfull" not in log
    assert not re.search(r"(?:Citation|Reference).*undefined|undefined references", log)
    result = {"main_records": summary["records"], "checking_agreements": len(summary["checking"]),
              "replayed_shortest_faults": len(summary["counterexamples"]),
              "attempted_mapped_transitions": sum(r["attempted_transitions"] for r in summary["correspondence"]),
              "citations": len(used), "inline_graphics": True,
              "latex": "compiled; no undefined references/citations or overfull boxes",
              "remaining_warning": "template lettersize option unused; underfull boxes are nonfatal"}
    Path("results/validation/artifact_audit.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
