"""Deterministic replay of public Voyager primitive revisions; no inferred lineage."""
import json
import subprocess
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from heartness import Artifact, Engine
from heartness.model import digest
from heartness.monitor import monitor
from heartness.properties import violations
from heartness.simulator import install
from experiments.run import Writer, measure


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True)


def run(repo):
    head = git(repo, "rev-parse", "HEAD").strip()
    commits = git(repo, "log", "--reverse", "--format=%H", "--all", "--",
                  "voyager/control_primitives/*.js").splitlines()
    engine, events, imported = Engine(), [], []
    previous = {}
    for commit in commits:
        paths = git(repo, "ls-tree", "-r", "--name-only", commit,
                    "voyager/control_primitives").splitlines()
        for path in sorted(p for p in paths if p.endswith(".js")):
            text = git(repo, "show", f"{commit}:{path}")
            old = previous.get(path)
            if old and old[1] == digest(text):
                continue
            key = "git-" + digest([commit, path])[:20]
            artifact = Artifact(key, "executable", text, sources=(old[0],) if old else (),
                                authorized_seed=old is None, derivation="edit" if old else "seed",
                                path=path)
            events.extend(install(engine, artifact, "Edit" if old else "Propose",
                                  old[0] if old else None))
            imported.append({"commit": commit, "path": path, "id": key,
                             "sha256": digest(text), "revision": asdict(artifact)})
            previous[path] = (key, digest(text))
    findings, cost = measure(lambda: monitor(events))
    root = Path("results/raw") / datetime.now(timezone.utc).strftime("realistic-%Y%m%dT%H%M%S%fZ")
    writer = Writer(root)
    record = {"repository": "https://github.com/MineDojo/Voyager", "head": head,
              "commits": commits, "imports": imported, "revision_count": len(imported),
              "event_count": len(events), "events": [asdict(e) for e in events],
              "deviations": [asdict(d) for d in findings], "violations": violations(engine),
              "cost": cost, "limits": "File revision lineage only; no autonomous synthesis truth, "
              "no execution of imported JavaScript, shallow history of 40 commits."}
    writer.record("E12_public_replay", {"head": head}, 0, record)
    writer.put("manifest.json", {"complete": True, "records": 1, "supplement": True})
    Path("results/processed/realistic.json").write_text(json.dumps(
        {key: record[key] for key in ("head", "commits", "revision_count", "event_count",
                                    "deviations", "violations", "cost", "limits")} |
        {"raw": str(root)}, indent=2) + "\n")
    print(root, len(imported), len(events), len(findings), flush=True)


if __name__ == "__main__":
    run(Path("build/Voyager"))
