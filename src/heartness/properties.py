"""State/transition audit predicates; the engine guards are checked separately."""

from __future__ import annotations

from heartness.engine import Engine
from heartness.model import State, digest

PROPERTY_IDS = tuple("P" + str(i) for i in range(1, 11))


def violations(engine: Engine, previous: State | None = None) -> list[str]:
    s, graph = engine.state, engine.graph
    bad: set[str] = set()
    for a in s.artifacts.values():
        if not (a.experiences or a.sources or a.authorized_seed):
            bad.add("P1")
        if not set(a.experiences) <= s.experiences.keys():
            bad.add("P1")
    if not graph.acyclic():
        bad.add("P6")
    forbidden = graph.closure(s.forbidden_roots(), dependencies=True)
    if s.active & forbidden:
        bad.add("P2")
    if not engine._consistent(s.active):
        bad.add("P3")
    for deployment in s.deployments.values():
        if set(deployment) & forbidden:
            bad.add("P8")
        if not engine._consistent(set(deployment)):
            bad.add("P3")
    for version in s.versions:
        if dict(version.hashes) != {a: s.artifacts[a].hash for a in version.active}:
            bad.add("P4")
        if version.reason.startswith("rollback:"):
            target = int(version.reason.split(":")[1])
            if version.active != s.versions[target].active:
                bad.add("P5")
    for pid in s.accepted:
        p, validation = s.proposals[pid], s.validations[pid]
        if not validation.passed or validation.artifact_hash != p.artifact.hash:
            bad.add("P4")
        version = next(v for v in s.versions if v.reason == "accept:" + pid)
        if p.base != version.id - 1:
            bad.add("P9")
    for idx, record in enumerate(s.history):
        if record["previous"] != (digest(s.history[idx - 1]) if idx else "root"):
            bad.add("P10")
    if previous is not None:
        if s.history[:len(previous.history)] != previous.history:
            bad.add("P7")
        if not previous.artifacts.keys() <= s.artifacts.keys():
            bad.add("P7")
        if s.effects[:len(previous.effects)] != previous.effects:
            bad.add("P5")
    return sorted(bad, key=lambda key: int(key[1:]))
