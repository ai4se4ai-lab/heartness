"""Targeted source mutation campaign, isolated copies and retained pytest output."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MUTANTS = [
    ("origin_dropped", "graph.py", "result.update(item.experiences)", "result.update(())"),
    ("descendants_empty", "graph.py", "return self.closure([source]) - {source}", "return set()"),
    ("impact_direct_only", "graph.py", "return self.closure([source], dependencies=True) & set(active)",
     "return {source} & set(active)"),
    ("cycle_ignored", "graph.py", "return removed == len(degree)", "return True"),
    ("validation_ignored", "engine.py", "validation.passed and validation.artifact_hash == p.artifact.hash",
     "True"),
    ("base_ignored", "engine.py", "p.base == len(s.versions) - 1", "True"),
    ("closure_guard_ignored", "engine.py", "self._safe(active),", "True,"),
    ("contracts_ignored", "engine.py", "self._consistent(active),", "True,"),
    ("reuse_propagation_removed", "engine.py", 'if "P8" not in self.disabled:', "if False:"),
    ("rollback_empty", "engine.py", "s.active = target", "s.active = set()"),
    ("effects_deleted_on_rollback", "engine.py", "self._snapshot(\"rollback:\" + str(version))",
     "s.effects.clear()\n            self._snapshot(\"rollback:\" + str(version))"),
    ("origin_seed_dropped", "graph.py", 'result.add("seed:" + node)', "result.update(())"),
    ("eme_edges_dropped", "graph.py", "self.children[exposed].add(item.id)", "pass"),
    ("load_context_ignored", "engine.py", "loaded_active = context", "pass"),
]


def main():
    output = Path("results/validation")
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for name, filename, old, new in MUTANTS:
        with tempfile.TemporaryDirectory(prefix="heartness-mutant-") as tmp:
            root = Path(tmp)
            for directory in ("src", "tests", "benchmark"):
                shutil.copytree(directory, root / directory, ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copy("pyproject.toml", root)
            path = root / "src/heartness" / filename
            original = path.read_text()
            assert old in original, name
            path.write_text(original.replace(old, new, 1))
            run = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests/test_engine.py",
                                  "tests/test_graph.py", "tests/test_eme.py"], cwd=root, text=True, capture_output=True,
                                 timeout=60)
            killed = run.returncode == 1
            records.append({"mutant": name, "file": filename, "old": old, "new": new,
                            "killed": killed, "returncode": run.returncode,
                            "stdout": run.stdout, "stderr": run.stderr})
            print(name, "killed" if killed else "SURVIVED/ERROR", flush=True)
    report = {"kind": "targeted hand-authored source mutations; not exhaustive mutation analysis",
              "total": len(records), "killed": sum(r["killed"] for r in records), "records": records}
    target = output / "mutation.json"
    if target.exists():
        import time
        target = output / ("mutation-" + str(time.time_ns()) + ".json")
    target.write_text(json.dumps(report, indent=2) + "\n")
    (output/"mutation_selection.json").write_text(json.dumps({"report": str(target)})+"\n")


if __name__ == "__main__":
    main()
