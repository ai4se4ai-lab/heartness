"""Closure-bounded revalidation (post-review extension), evaluated on recorded live states.

For each faulty-run record: suspend the HEARTNESS closure, then re-admit the suspended non-root
members that a screen clears and that were in use before the withdrawal, in history order,
rejecting a member whose dependency stays suspended (Algorithm 5; the decision is made by
heartness.revalidation.plan, the function the engine executes).
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
from heartness.revalidation import Plan, plan


def history_order(rec: dict[str, Any]) -> list[str]:
    """Acceptance order: task index from the evolution log; within a task memory < skill < profile."""
    when: dict[str, int] = {}  # same rule as experiments.live.process.created_at
    for entry in rec["evolution"]:
        ids = [entry.get("memory"), (entry.get("skill") or {}).get("id")]
        ids += [p.get("id") for p in (entry.get("profiles") or {}).values() if isinstance(p, dict)]
        ids += [op.get("id") for op in (entry.get("extraction") or {}).get("ops", [])]
        for a in ids:
            if a and a not in when:
                when[a] = entry["i"]
    rank = {"memory": 0, "skill": 1, "agent": 2}
    return sorted(rec["artifacts"], key=lambda a: (when.get(a, -1),
                                                    rank.get(rec["artifacts"][a]["kind"], 3), a))


def restore(rec: dict[str, Any], keep: set[str]
            ) -> tuple[set[str], dict[str, tuple[str, ...]], Plan]:
    """State after H plus Algorithm 5 re-admission of the cleared members `keep`.

    Uses heartness.revalidation.plan, the same function the engine executes: a cleared member
    is re-admitted only if each dependency is active after H or re-admitted before it. Fresh
    copies carry the original's text, so they are evaluated under the original's identity.
    """
    h = rec["remedies"]["H"]
    deps = {k: tuple(a["dependencies"]) for k, a in rec["artifacts"].items()}
    in_use = set(rec["active"]) | {a for m in rec["deployments"].values() for a in m}
    p = plan(history_order(rec), deps, set(h["active"]), keep & in_use)  # as revalidate()
    back = set(p.admitted)
    active = set(h["active"]) | back
    deployments = {d: tuple(sorted(set(m) | (back & set(rec["deployments"][d]))))
                   for d, m in h["deployments"].items()}
    return active, deployments, p


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
        active, deployments, p = restore(rec, keep)
        live = active | {a for m in deployments.values() for a in m}
        result["remedies"][name] = {"cleared": sorted(keep), "restored": sorted(p.admitted),
                                    "rejected": p.rejected,
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
