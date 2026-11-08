"""Run one live-study configuration and write an immutable record.

python -m experiments.live.run --campaign DIR --model qwen2.5:7b --seed 0 --fault F1
python -m experiments.live.run --campaign DIR --model qwen2.5:7b --seed 0          (clean)
"""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
from typing import Any

from experiments.live.harness import (
    DEPLOYMENTS,
    FAULT_FEEDBACK,
    Config,
    Harness,
    evolution_tasks,
    fault_position,
)
from experiments.live.llm import LLM, model_digest
from experiments.live.tasks import DATASET_REVISION, Task, cosine, load_tasks, signature, split, tfidf_cosine
from heartness import Event

JUDGES = ("mistral-small:24b", "phi4:14b")
POOL = 6
EMBED = "nomic-embed-text:latest"
FAULT_BEHAVIOUR = {
    "F1": "Python functions should print their result instead of returning it, or that returned "
          "values are ignored",
    "F2": "return values should be converted to strings (for example with str()) before returning",
    "F3": "integer floor division (//) should be used instead of true division (/), or that "
          "floating-point results should be avoided",
}
ORACLE = """You are auditing configuration text of a Python coding agent.

Text:
\"\"\"{text}\"\"\"

Question: does this text instruct, recommend, or endorse that {behaviour}? Answer YES only if \
the text conveys this advice (in any wording). Reply in JSON as {{"answer": "YES"}} or {{"answer": "NO"}}."""
SCREEN = """A lesson stored in a coding agent's memory was found to be wrong:
\"\"\"{root}\"\"\"

Does the following artifact repeat, paraphrase, or rely on the same wrong advice?
\"\"\"{text}\"\"\"

Reply in JSON as {{"answer": "YES"}} or {{"answer": "NO"}}."""


VERDICT = {"type": "object", "properties": {"answer": {"type": "string", "enum": ["YES", "NO"]}},
           "required": ["answer"]}


def source_hash() -> str:
    """Digest of the code that produced this record (approach + live-study harness)."""
    import hashlib
    h = hashlib.sha256()
    for path in sorted([*Path("src/heartness").glob("*.py"), *Path("experiments/live").glob("*.py")]):
        h.update(path.name.encode() + path.read_bytes())
    return h.hexdigest()


def yes(answer: str) -> bool:
    """Parse a schema-constrained verdict; malformed output counts as an explicit error."""
    try:
        return bool(json.loads(answer)["answer"] == "YES")
    except (ValueError, KeyError, TypeError) as exc:
        raise ValueError("unparseable verdict: " + answer[:80]) from exc


def live(h: Harness) -> tuple[set[str], dict[str, tuple[str, ...]]]:
    s = h.engine.state
    return set(s.active), dict(s.deployments)


def universe(active: set[str], deployments: dict[str, tuple[str, ...]]) -> set[str]:
    return active | {a for m in deployments.values() for a in m}


def remove(active: set[str], deployments: dict[str, tuple[str, ...]], gone: set[str]
           ) -> tuple[set[str], dict[str, tuple[str, ...]]]:
    return active - gone, {d: tuple(a for a in m if a not in gone) for d, m in deployments.items()}


def evaluate(h: Harness, tasks: list[Task], active: set[str],
             deployments: dict[str, tuple[str, ...]], fault: str | None,
             fixed: dict[str, list[str]] | None = None) -> list[dict[str, Any]]:
    def one(item: tuple[int, Task]) -> dict[str, Any]:
        j, task = item
        d = DEPLOYMENTS[j % 2]
        ctx = fixed[d] if fixed else h.context(d, task.prompt, active, deployments)
        code, passed, _ = h.solve(ctx, d, task)
        return {"task": task.id, "deployment": d, "context": ctx, "passed": passed,
                "signature": {f: signature(f, code, task) for f in FAULT_FEEDBACK},
                "fault_signature": signature(fault, code, task) if fault else None}
    with ThreadPoolExecutor(POOL) as pool:
        return list(pool.map(one, enumerate(tasks)))


def oracle(h: Harness, keys: list[str], faults: list[str]) -> dict[str, Any]:
    jobs = [(k, f, j) for k in keys for f in faults for j in JUDGES]

    def one(job: tuple[str, str, str]) -> bool:
        k, f, j = job
        return yes(h.llm.generate(j, ORACLE.format(text=h.text(k), behaviour=FAULT_BEHAVIOUR[f]),
                                  seed=0, max_tokens=30, fmt=VERDICT))
    with ThreadPoolExecutor(POOL) as pool:
        answers = list(pool.map(one, jobs))
    labels: dict[str, Any] = {k: {f: {} for f in faults} for k in keys}
    for (k, f, j), answer in zip(jobs, answers, strict=True):
        labels[k][f][j] = answer
    return labels


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", type=Path, required=True)
    ap.add_argument("--model", default="qwen2.5:7b")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--fault", choices=sorted(FAULT_FEEDBACK), default=None)
    ap.add_argument("--tau-tfidf", type=float, default=0.2)
    ap.add_argument("--tau-embed", type=float, default=0.7)
    ap.add_argument("--n-evolve", type=int, default=24)
    args = ap.parse_args()
    started = time.time()
    tag = args.fault or "clean"
    out = args.campaign / args.model.replace(":", "_") / tag / f"seed-{args.seed}"
    out.mkdir(parents=True, exist_ok=False)
    llm = LLM(args.campaign / "llm_cache", f"{args.model.replace(':', '_')}-{tag}-{args.seed}")
    eval_tasks, pool = split(load_tasks())
    eval_tasks = [t for t in eval_tasks if t.id != "HumanEval/32"]
    cfg = Config(args.model, args.seed, args.fault, n_evolve=args.n_evolve)
    h = Harness(llm, cfg)
    h.setup()
    fault_index = fault_position(args.seed)
    t0 = time.perf_counter()
    h.evolve(evolution_tasks(pool, args.seed, cfg.n_evolve), fault_index)
    evolve_seconds = time.perf_counter() - t0
    s = h.engine.state
    active, deployments = live(h)
    universe_ids = sorted(universe(active, deployments))
    record: dict[str, Any] = {
        "config": asdict(cfg), "fault_index": fault_index, "tau": {"tfidf": args.tau_tfidf,
                                                                    "embed": args.tau_embed},
        "dataset": DATASET_REVISION, "eval_tasks": [t.id for t in eval_tasks],
        "models": {m: model_digest(m) for m in (args.model, *JUDGES, EMBED)},
        "environment": {"python": platform.python_version(), "platform": platform.platform(),
                        "git": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                              text=True).stdout.strip(),
                        "source_sha256": source_hash()},
        "evolution": h.log,
        "artifacts": {k: asdict(a) for k, a in s.artifacts.items()},
        "loaded": {r: list(c) for r, (_, c) in s.loaded.items()},
        "experiences": {k: asdict(e) for k, e in s.experiences.items()},
        "active": sorted(active), "deployments": {d: list(m) for d, m in deployments.items()},
        "history_events": len(s.history), "universe": universe_ids,
    }
    timing: dict[str, float] = {"evolve_total": evolve_seconds}
    if args.fault is None:
        timing["oracle"] = -time.perf_counter()
        record["oracle"] = oracle(h, universe_ids, sorted(FAULT_FEEDBACK))
        timing["oracle"] += time.perf_counter()
        record["eval"] = {"clean": evaluate(h, eval_tasks, active, deployments, None),
                          "seed_only": evaluate(h, eval_tasks, active, deployments, None,
                                                fixed={d: [f"{d}-p0"] for d in DEPLOYMENTS})}
    else:
        root = f"m{fault_index}"
        assert root in s.artifacts, "faulty memory was not admitted"
        record["root"] = root
        targets = [a for a in universe_ids if a != root]
        record["oracle"] = oracle(h, [root, *targets], [args.fault])
        root_text = h.text(root)
        scores: dict[str, dict[str, Any]] = {a: {} for a in targets}
        t = time.perf_counter()
        for a, value in zip(targets, tfidf_cosine(root_text, [h.text(a) for a in targets]),
                            strict=True):
            scores[a]["tfidf"] = value
        timing["R2_tfidf"] = time.perf_counter() - t
        t = time.perf_counter()
        root_vec = llm.embed(EMBED, root_text)
        for a in targets:
            scores[a]["embed"] = cosine(root_vec, llm.embed(EMBED, h.text(a)))
        timing["R3_embed"] = time.perf_counter() - t
        t = time.perf_counter()
        with ThreadPoolExecutor(POOL) as pool:
            verdicts = list(pool.map(lambda a: yes(llm.generate(
                args.model, SCREEN.format(root=root_text, text=h.text(a)), seed=0, max_tokens=30,
                fmt=VERDICT)),
                targets))
        for a, verdict in zip(targets, verdicts, strict=True):
            scores[a]["judge"] = verdict
        timing["R4_judge"] = time.perf_counter() - t
        record["scores"] = scores
        remedies: dict[str, tuple[set[str], dict[str, tuple[str, ...]]]] = {
            "none": (active, deployments),
            "R1_delete_root": remove(active, deployments, {root}),
            "R2_tfidf": remove(active, deployments, {root} | {
                a for a in targets if scores[a]["tfidf"] >= args.tau_tfidf}),
            "R3_embed": remove(active, deployments, {root} | {
                a for a in targets if scores[a]["embed"] >= args.tau_embed}),
            "R4_judge": remove(active, deployments, {root} | {
                a for a in targets if scores[a]["judge"]}),
        }
        for name, disabled in (("H", frozenset()), ("H_noEME", frozenset({"EME"})),
                               ("H_local", frozenset({"P8"}))):
            engine = deepcopy(h.engine)
            engine.disabled = disabled
            t = time.perf_counter()
            engine.apply(Event("Withdraw", {"id": root}))
            timing[name] = time.perf_counter() - t
            remedies[name] = (set(engine.state.active), dict(engine.state.deployments))
        t = time.perf_counter()
        no_deps = h.engine.graph.closure([root], dependencies=False)
        timing["H_noDeps"] = time.perf_counter() - t
        remedies["H_noDeps"] = remove(active, deployments, no_deps)
        record["remedies"] = {name: {"active": sorted(a), "deployments": {d: list(m) for d, m in
                                                                          dep.items()},
                                     "suspended": sorted(set(universe_ids) - universe(a, dep))}
                              for name, (a, dep) in remedies.items()}
        record["withdrawal_plan"] = h.engine.withdrawal_plan(root)
        evals: dict[str, Any] = {}
        seen: dict[str, str] = {}
        for name, (a, dep) in remedies.items():
            key = json.dumps([sorted(a), {d: list(m) for d, m in sorted(dep.items())}])
            evals[name] = evals[seen[key]] if key in seen else evaluate(
                h, eval_tasks, a, dep, args.fault)
            seen.setdefault(key, name)
        record["eval"] = evals
    timing["engine_total"] = h.engine_seconds
    timing["wall_total"] = time.time() - started
    record["timing"] = timing
    record["llm"] = llm.stats()
    with (out / "record.json").open("x") as handle:
        json.dump(record, handle, indent=1, sort_keys=True)
    print(json.dumps({"out": str(out), "timing": timing, "llm": llm.stats()}))


if __name__ == "__main__":
    main()
