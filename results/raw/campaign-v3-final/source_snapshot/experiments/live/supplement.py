"""Closure-bounded revalidation (post-review extension), evaluated on recorded live states.

For each faulty-run record: suspend the HEARTNESS closure, then re-admit every suspended
non-root member that a screen clears, as a fresh validator-attested revision with the
same content (tests/test_eme.py shows the controller supports this without bypassing P2).
Screens reuse verdicts/scores already stored in the record (no new screening calls):
  HS_judge  - generator-model judge says the member does not repeat the root's advice
  HS_embed  - embedding cosine to the root below the dev-tuned threshold
Only held-out evaluation solves are new. Output: supplement.json beside record.json
(exclusive creation); main records are never modified.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from experiments.live.harness import Config, Harness
from experiments.live.llm import LLM
from experiments.live.run import evaluate
from experiments.live.tasks import load_tasks
from heartness import Artifact


def restore(rec: dict[str, Any], keep: set[str]) -> tuple[set[str], dict[str, tuple[str, ...]]]:
    """State after H plus re-admission of `keep` into the active set and original deployments."""
    h = rec["remedies"]["H"]
    active = set(h["active"]) | (keep & set(rec["active"]))
    deployments = {d: tuple(sorted(set(m) | (keep & set(rec["deployments"][d]))))
                   for d, m in h["deployments"].items()}
    return active, deployments


def main(path: Path) -> None:
    rec = json.loads(path.read_text())
    out = path.with_name("supplement.json")
    if out.exists():
        print("exists", out)
        return
    cfg = Config(**{k: (tuple(v) if isinstance(v, list) else v) for k, v in rec["config"].items()})
    campaign = next(q for q in path.parents if (q / "llm_cache").is_dir())
    llm = LLM(campaign / "llm_cache",
              f"supp-{cfg.model.replace(':', '_')}-{cfg.benchmark}-{cfg.policy}-{cfg.fault}-{cfg.seed}")
    h = Harness(llm, cfg)
    h.engine.state.artifacts = {k: Artifact.from_dict(v) for k, v in rec["artifacts"].items()}
    tasks = {t.id: t for t in load_tasks(cfg.benchmark)}
    eval_tasks = [tasks[t] for t in rec["eval_tasks"]]
    roots = set(rec.get("roots") or [rec["root"]])
    if not rec.get("remedies"):
        print("no roots (fault not adopted); nothing to revalidate", path)
        return
    suspended = set(rec["remedies"]["H"]["suspended"]) - roots
    tau = rec["tau"]["embed"]
    screens = {
        "HS_judge": {a for a in suspended if not rec["scores"][a]["judge"]},
        "HS_embed": {a for a in suspended if rec["scores"][a]["embed"] < tau},
    }
    result: dict[str, Any] = {"source_record": str(path), "remedies": {}, "eval": {}}
    universe = set(rec["universe"])
    for name, keep in screens.items():
        active, deployments = restore(rec, keep)
        live = active | {a for m in deployments.values() for a in m}
        result["remedies"][name] = {"restored": sorted(keep),
                                    "suspended": sorted(universe - live)}
        start = time.perf_counter()
        result["eval"][name] = evaluate(h, eval_tasks, active, deployments, cfg.fault)
        result["remedies"][name]["eval_seconds"] = time.perf_counter() - start
    result["llm"] = llm.stats()
    with out.open("x") as handle:
        json.dump(result, handle, indent=1, sort_keys=True)
    print("wrote", out)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        main(Path(arg))
