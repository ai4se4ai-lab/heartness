"""A feedback-to-persistent-state running example, without model-service access."""

from __future__ import annotations

from dataclasses import asdict

from heartness.engine import Engine
from heartness.model import Artifact, Contract, Event


def install(engine: Engine, artifact: Artifact, op: str = "Propose",
            replaces: str | None = None) -> list[Event]:
    pid = "p-" + artifact.id
    events = [Event(op, {"id": pid, "artifact": asdict(artifact),
                         "base": len(engine.state.versions) - 1, "replaces": replaces}),
              Event("Validate", {"id": pid, "passed": True}), Event("Accept", {"id": pid})]
    observed = []
    for event in events:
        observed.append(Event(event.op, event.args, engine.apply(event)))
    return observed


def example() -> tuple[Engine, list[Event]]:
    engine = Engine()
    events: list[Event] = []

    def emit(event: Event) -> None:
        events.append(Event(event.op, event.args, engine.apply(event)))

    emit(Event("Experience", {"id": "e1", "task": "repair timeout", "run": "r0",
                              "outcome": "incorrect lesson: skip validation"}))
    records = [
        Artifact("m1", "memory", "skip validation after timeout", experiences=("e1",),
                 contract=Contract(provides=("lesson",))),
        Artifact("m2", "prompt", "retry within budget", authorized_seed=True,
                 contract=Contract(provides=("budget",))),
        Artifact("s1", "skill", "fast recovery procedure", sources=("m1", "m2"),
                 derivation="merge", contract=Contract(provides=("recover",))),
        Artifact("a1", "agent", "coding agent", dependencies=("s1",),
                 contract=Contract(requires=("recover",))),
        Artifact("a2", "agent", "review agent", dependencies=("s1",),
                 contract=Contract(requires=("recover",))),
    ]
    for a in records:
        # An agent configuration's own origin is authorized; uses != derivedFrom.
        if a.id in {"a1", "a2"}:
            a = Artifact(a.id, a.kind, a.text, dependencies=a.dependencies,
                         authorized_seed=True, contract=a.contract)
        events.extend(install(engine, a, "Merge" if a.id == "s1" else "Propose"))
    emit(Event("Deploy", {"deployment": "d1"}))
    emit(Event("Reuse", {"deployment": "d2"}))
    emit(Event("Load", {"run": "r1"}))
    emit(Event("Effect", {"id": "x1", "run": "r1", "description": "sent external patch"}))
    return engine, events
