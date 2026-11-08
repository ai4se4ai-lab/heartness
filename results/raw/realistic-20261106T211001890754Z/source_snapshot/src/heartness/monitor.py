"""Replay observed events; reject differences without trusting the claimed state."""

from __future__ import annotations

from collections.abc import Iterable
from copy import deepcopy
from dataclasses import dataclass

from heartness.engine import Engine, Rejected
from heartness.model import Event
from heartness.properties import violations


@dataclass(frozen=True)
class Deviation:
    index: int
    kind: str
    detail: str


def monitor(events: Iterable[Event]) -> list[Deviation]:
    engine = Engine()
    findings: list[Deviation] = []
    for idx, event in enumerate(events):
        previous = deepcopy(engine.state)
        try:
            actual = engine.apply(event)
        except Rejected as exc:
            findings.append(Deviation(idx, "rejected", str(exc)))
            # Fail closed: later comparisons have no synchronized reference state.
            break
        if event.observed and actual != event.observed:
            findings.append(Deviation(idx, "state_mismatch", "observed digest differs"))
        for prop in violations(engine, previous):
            findings.append(Deviation(idx, "invariant", prop))
    return findings


def observation_summary(events: Iterable[Event]) -> dict[str, int | str]:
    sequence = list(events)
    supplied = sum(bool(event.observed) for event in sequence)
    return {"events": len(sequence), "supplied_observations": supplied,
            "missing_observations": len(sequence) - supplied,
            "status": "all events observed" if sequence and supplied == len(sequence)
            else "event admissibility only" if not supplied else "partial state observations"}
