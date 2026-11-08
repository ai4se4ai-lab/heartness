"""Run eleven campaigns; immutable raw records precede all aggregation."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import random
import subprocess
import time
import tracemalloc
from copy import deepcopy
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path

from hypothesis import Phase, find, settings, strategies as st
from hypothesis.errors import NoSuchExample, Unsatisfiable

from benchmark.generate import Config, FAMILIES, generate
from heartness import Artifact, Engine, Event, Rejected
from heartness.baselines import capture, file_history, linter, query, similarity
from heartness.checker import actions, bad, bfs, initial, replay, spin_check, step
from heartness.model import canonical, digest
from heartness.monitor import monitor
from heartness.properties import PROPERTY_IDS, violations
from heartness.simulator import example


def environment():
    files = sorted(p for folder in ("src", "benchmark", "experiments", "formal", "tests")
                   for p in Path(folder).rglob("*") if p.is_file() and "__pycache__" not in str(p))
    return {"python": platform.python_version(), "platform": platform.platform(),
            "cpu": platform.processor(), "cpu_count": os.cpu_count(),
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
            "git_status": subprocess.check_output(["git", "status", "--short"], text=True),
            "source_sha256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
            "packages": {p: importlib.metadata.version(p) for p in
                         ("numpy", "scipy", "hypothesis", "pytest")}}


class Writer:
    def __init__(self, root):
        self.root = root
        root.mkdir(parents=True, exist_ok=False)
        self.env = environment()
        self.put("environment.json", self.env)
        for name in self.env["source_sha256"]:
            path = self.root / "source_snapshot" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as stream:
                stream.write(Path(name).read_bytes())

    def put(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x") as f:
            f.write(canonical(value) + "\n")

    def record(self, experiment, config, seed, data):
        self.put(f"{experiment}/{digest(config)[:12]}/{seed}/record.json",
                 {"experiment": experiment, "config": config, "seed": seed,
                  "config_hash": digest(config), **data})


def measure(call):
    tracemalloc.start()
    start = time.perf_counter()
    output = call()
    seconds = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return output, {"seconds": seconds, "peak_bytes": peak}


def trace_record(writer, experiment, config, methods=True):
    scenario = generate(config)
    items = [Artifact.from_dict(a) for a in scenario["artifacts"]]
    captured = capture(items, config.capture, config.seed)
    variants = {"ours": captured, "B2_capture_only": captured}
    if methods:
        variants.update({"B0_file_history": file_history(items), "B1_lexical": similarity(items)})
    truth = scenario["truth"]
    outputs = {}
    for name, artifacts in variants.items():
        result, cost = measure(lambda: query(artifacts, truth["root"], truth["target"],
                                             scenario["active"], scenario["deployments"]))
        outputs[name] = {"queries": result, **cost}
    writer.record(experiment, asdict(config), config.seed,
                  {"scenario": scenario, "outputs": outputs})


def engine_challenges():
    """Same fixtures with every property disabled; independent injected observations."""
    base, events = example()
    checks = []
    for prop in ("full", *PROPERTY_IDS, "no_contracts", "no_monitor", "no_model_checking"):
        disabled = frozenset({"P3" if prop == "no_contracts" else prop}) if prop != "full" else frozenset()
        e = Engine(disabled=disabled)
        for event in events:
            e.apply(Event(event.op, event.args))
        e.apply(Event("Withdraw", {"id": "m1"}))
        checks.append({"ablation": prop, "violations": violations(e),
                       "remaining_active": sorted(e.state.active),
                       "remaining_deployed": e.state.deployments,
                       "latent_mutant_found": None if prop == "no_model_checking" else
                       not bfs(2, 9, "P4")["safe"],
                       "observed_drift_detected": prop != "no_monitor" and bool(monitor(
                           events[:-1] + [replace(events[-1], observed="wrong")]))})
    targeted = [{"property": prop, "full": property_challenge(prop, False),
                 "removed": property_challenge(prop, True)} for prop in PROPERTY_IDS]
    return {"checks": checks, "targeted": targeted, "events": [asdict(e) for e in events],
            "base_state": base.state.semantic()}


def property_challenge(prop, remove):
    """Guard removal and audit removal are different interventions, labeled below."""
    from heartness.simulator import install
    e = Engine(disabled=frozenset({prop}) if remove else frozenset())
    base, events = example()
    for event in events:
        e.apply(Event(event.op, event.args))
    before = deepcopy(e.state)
    rejected = False
    mode = "guard"
    try:
        if prop in {"P2", "P8"}:
            e.apply(Event("Withdraw", {"id": "m1"}))
        elif prop == "P1":
            install(e, Artifact("orphan", "skill", "no anchor"))
        elif prop == "P6":
            install(e, Artifact("cycle", "skill", "self source", sources=("cycle",)))
        elif prop == "P3":
            from heartness.model import Contract
            install(e, Artifact("consumer", "agent", "requires missing capability",
                    dependencies=("s1",), authorized_seed=True,
                    contract=Contract(requires=("absent",))))
        elif prop in {"P4", "P9"}:
            artifact = Artifact("candidate", "skill", "candidate", authorized_seed=True)
            e.apply(Event("Propose", {"id": "candidate", "artifact": asdict(artifact),
                                      "base": 0 if prop == "P9" else len(e.state.versions)-1}))
            e.apply(Event("Validate", {"id": "candidate", "passed": prop != "P4"}))
            e.apply(Event("Accept", {"id": "candidate"}))
        else:
            mode = "audit predicate removed; out-of-API corruption"
            if prop == "P5":
                e.state.effects.clear()
            elif prop == "P7":
                e.state.history.pop()
            elif prop == "P10":
                e.state.history[-1]["previous"] = "tampered"
    except Rejected:
        rejected = True
    found = violations(e, before)
    if mode.startswith("audit") and remove:
        found = [p for p in found if p != prop]
    return {"intervention": mode, "rejected": rejected, "audit_findings": found,
            "target_alarm": prop in found,
            "content_changed": e.state.hash != before.hash}


def engine_replay_projection(trace, n, mutant, topology):
    """Replay projected operators through the real engine with stable IDs."""
    e = Engine(disabled=frozenset({mutant}) if mutant else frozenset())
    observed = []
    rejected = None
    from heartness.checker import masks
    parents, _ = masks(n, topology)
    for op, idx in trace:
        aid, pid = "a" + str(idx), "p" + str(idx)
        if op == "propose":
            sources = tuple("a" + str(j) for j in range(n) if parents[idx] & (1 << j))
            a = Artifact(aid, "skill", "projection", sources=sources,
                         dependencies=sources, authorized_seed=not sources)
            event = Event("Propose", {"id": pid, "artifact": asdict(a)})
        elif op == "validate":
            event = Event("Validate", {"id": pid, "passed": True})
        elif op == "accept":
            # Boolean absent validation in the projection is a failed validation record.
            if pid not in e.state.validations:
                e.apply(Event("Validate", {"id": pid, "passed": False}))
            event = Event("Accept", {"id": pid})
        elif op == "withdraw":
            event = Event("Withdraw", {"id": aid})
        elif op == "deploy":
            event = Event("Deploy", {"deployment": "d"})
        else:
            event = Event("Rollback", {"version": idx})
        try:
            e.apply(event)
        except Rejected as exc:
            rejected = str(exc)
            break
        observed.append({"event": asdict(event), "violations": violations(e)})
    return {"events": observed, "rejected": rejected, "violations": violations(e)}


class BudgetExpired(Exception):
    pass


def search_fault(seed, mutant, method, budget=.05):
    start = time.perf_counter()
    rng = random.Random(seed)
    action_space = actions(2)
    attempts = 0
    if method == "bfs":
        result = bfs(2, 9, mutant, seconds=budget)
        return {"found": result["safe"] is False, "attempts": result["transitions"],
                "seconds": time.perf_counter()-start, "indices": result["trace"],
                "budget_seconds": budget, "complete": result["complete"]}

    def fails(indices):
        nonlocal attempts
        attempts += 1
        if time.perf_counter() - start > budget:
            raise BudgetExpired
        s = initial(2)
        for index in indices:
            action = action_space[index]
            nxt = step(s, action, 2, mutant)
            if nxt is not None:
                if bad(nxt, 2, s, action):
                    return True
                s = nxt
        return False

    witness = None
    try:
        if method == "random":
            while witness is None:
                indices = [rng.randrange(len(action_space)) for _ in range(9)]
                if fails(indices):
                    witness = indices
        else:
            witness = find(st.lists(st.integers(0, len(action_space) - 1), min_size=1, max_size=9),
                           fails, random=rng, settings=settings(max_examples=100000, database=None,
                           deadline=None, phases=(Phase.generate,)))
    except (BudgetExpired, NoSuchExample, Unsatisfiable):
        pass
    return {"found": witness is not None, "attempts": attempts,
            "seconds": time.perf_counter() - start, "indices": witness, "budget_seconds": budget}


def run(root):
    writer = Writer(root)
    # RQ1 main and sensitivities. All methods use the same input scenario per seed.
    for family in FAMILIES:
        for size in (16, 64, 256):
            for seed in range(30):
                trace_record(writer, "E01_traceability", Config(family=family, artifacts=size, seed=seed))
    print("E01 complete", flush=True)
    for fraction in (0, .25, .5, .75, 1):
        for seed in range(30):
            trace_record(writer, "E02_capture", Config(capture=fraction, seed=seed))
    for paraphrase in (0, .5, 1):
        for seed in range(30):
            trace_record(writer, "E03_paraphrase", Config(paraphrase=paraphrase, seed=seed))
    writer.record("E04_ablations", {"fixture": "running-example"}, 0, engine_challenges())
    print("E02–E04 complete", flush=True)
    for topology in ("chain", "star", "independent"):
        for mutant in ("", "P2", "P3", "P4", "P8", "P9"):
            config = {"n": 3, "depth": 10, "mutant": mutant, "topology": topology}
            py, cost = measure(lambda: bfs(**config))
            sp, spcost = measure(lambda: spin_check(**config))
            writer.record("E05_model_checking", config, 0,
                          {"python": py, "spin": sp, "python_cost": cost, "spin_cost": spcost,
                           "agree": py["safe"] == sp["safe"]})
            if py["trace"]:
                re = replay(py["trace"], config["n"], mutant, topology)
                implementation = engine_replay_projection(py["trace"], config["n"], mutant, topology)
                shorter = bfs(config["n"], py["depth"] - 1, mutant, topology)
                writer.record("E06_counterexamples", config, 0,
                              {"trace": py["trace"], "projection_replay": re,
                               "implementation_replay": implementation, "shorter_safe": shorter["safe"],
                               "length": len(py["trace"])})
    print("E05–E06 complete", flush=True)
    for seed in range(30):
        e, events = example()
        # Randomize deployment count without changing the containment truth.
        for deployment in range(1 + seed % 4):
            e.apply(Event("Deploy", {"deployment": "extra" + str(deployment)}))
        plan = e.withdrawal_plan("m1")
        e.apply(Event("Withdraw", {"id": "m1"}))
        rejected = False
        try:
            e.apply(Event("Rollback", {"version": 5}))
        except Rejected:
            rejected = True
        e.apply(Event("Rollback", {"version": 0}))
        writer.record("E07_remediation", {"deployments": 1 + seed % 4}, seed,
                      {"plan": plan, "after": e.state.semantic(), "unsafe_rollback_rejected": rejected,
                       "violations": violations(e)})
    for size in (16, 64, 256, 1024, 2048):
        for seed in range(30):
            trace_record(writer, "E08_graph_scale", Config(artifacts=size, seed=seed), methods=False)
    for n in (2, 3, 4, 5, 6):
        for depth in (4, 6, 8, 10):
            for topology in ("chain", "independent"):
                config = {"n": n, "depth": depth, "topology": topology, "state_limit": 20000}
                result, cost = measure(lambda: bfs(**config))
                sliced, slice_cost = measure(lambda: bfs(2, depth, topology="chain", state_limit=20000))
                writer.record("E08_state_scale", config, 0,
                              {"full": result, "cost": cost, "two_node_projection": sliced,
                               "projection_cost": slice_cost,
                               "preservation_claim": "local properties only; no global safety inference"})
    print("E07–E08 complete", flush=True)
    for seed in range(30):
        e, events = example()
        idx = random.Random(seed).randrange(len(events))
        variants = {
            "benign": events,
            "observed_state_drift": events[:idx] + [replace(events[idx], observed="drift")] + events[idx+1:],
            "invalid_event": events + [Event("Accept", {"id": "absent"})],
            "hidden_external_effect": events,
            "omitted_event": events[:idx] + events[idx+1:],
        }
        outputs = {name: [asdict(d) for d in monitor(trace)] for name, trace in variants.items()}
        _, replay_cost = measure(lambda: monitor(events))
        def execute():
            engine = Engine()
            for event in events:
                engine.apply(event)
        _, execution_cost = measure(execute)
        writer.record("E09_conformance", {"fixture": "running-example"}, seed,
                      {"index": idx, "events": [asdict(event) for event in events], "outputs": outputs,
                       "monitor_cost": replay_cost, "execution_cost": execution_cost,
                       "hidden_action": "not logged and therefore deliberately undetectable"})
    for fanout in (1, 3, 6):
        for deployments in (1, 4):
            for seed in range(30):
                trace_record(writer, "E10_robustness", Config(fanout=fanout, deployments=deployments,
                             noise=.25, synthesis=.8, seed=seed))
    for mutant in ("", "P2", "P3", "P4", "P8", "P9"):
        for seed in range(30):
            outputs = {method: search_fault(seed, mutant, method)
                       for method in ("random", "hypothesis", "bfs")}
            writer.record("E11_search", {"n": 2, "depth": 9, "mutant": mutant}, seed,
                          {"outputs": outputs})
    from experiments.correspondence import compare_reference
    from experiments.runtime_cost import campaign as runtime_campaign
    runtime_campaign(writer, measure)
    from examples.recovery import run as recovery_run
    recovered, recovery_summary = recovery_run()
    writer.record("E16_recovery", {"fixture": "independently anchored correction"}, 0,
                  {"summary": recovery_summary, "state": recovered.state.semantic(),
                   "violations": violations(recovered)})
    for topology in ("chain", "independent"):
        writer.record("E15_correspondence", {"n": 2, "depth": 6, "topology": topology}, 0,
                      compare_reference(2, 6, topology))
    for size in (16, 64, 256):
        for seed in range(30):
            scenario = generate(Config(artifacts=size, seed=seed))
            artifacts = [Artifact.from_dict(a) for a in scenario["artifacts"]]
            questioned = scenario["truth"]["root"]
            active = set(scenario["active"]) - {questioned}
            true_faults = sorted(set(scenario["truth"]["impact"]) - {questioned})
            found, cost = measure(lambda: sorted(linter(artifacts, active, {questioned})))
            clean, clean_cost = measure(lambda: sorted(linter(artifacts, active, set())))
            writer.record("E14_linter", {"artifacts": size}, seed,
                          {"scenario": scenario, "truth_violations": true_faults,
                           "B3_fault": found, "B3_benign": clean, "fault_cost": cost,
                           "benign_cost": clean_cost})
    finalize(root)
    print(str(root), flush=True)


def finalize(root):
    """Exclusive completion metadata, also usable after an interrupted finalizer."""
    sample = random.Random(20261106).sample(sorted(root.glob("E01*/*/*/record.json")), 12)
    audit = {"kind": "approach-versus-oracle agreement; not independent benchmark validation",
             "samples": [str(p) for p in sample],
             "checks": [json.loads(p.read_text())["outputs"]["ours"]["queries"] ==
                         {key: sorted(json.loads(p.read_text())["scenario"]["truth"][key])
                          for key in ("descendants", "origins", "impact", "deployment_impact")}
                         for p in sample]}
    manifest = {"complete": True, "records": len(list(root.glob("E*/*/*/record.json"))),
                "experiments": sorted({p.name for p in root.glob("E*")})}
    for filename, data in (("benchmark_audit.json", audit), ("manifest.json", manifest)):
        with (root/filename).open("x") as stream:
            stream.write(canonical(data)+"\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/raw") /
                        datetime.now(timezone.utc).strftime("campaign-%Y%m%dT%H%M%S%fZ"))
    run(parser.parse_args().output)
