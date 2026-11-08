"""Instrument an explicit host-supplied generation boundary, not model internals."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass

from heartness import Artifact, Engine, Event


@dataclass(frozen=True)
class Exposure:
    sources: tuple[str, ...]
    texts: tuple[str, ...]
    untracked_inputs: tuple[str, ...] = ()


def prepare(engine: Engine, sources: tuple[str, ...],
            untracked_inputs: tuple[str, ...] = ()) -> Exposure:
    """Host selects immutable source IDs before the proposing policy executes."""
    return Exposure(sources, tuple(engine.state.artifacts[s].text for s in sources), untracked_inputs)


def propose(engine: Engine, exposure: Exposure, key: str,
            policy: Callable[[tuple[str, ...]], str], kind: str = "skill") -> Event:
    """Policy writes text; captured IDs are attached by the host rather than the policy."""
    text = policy(exposure.texts)
    artifact = Artifact(key, kind, text, sources=exposure.sources,
                        derivation="merge" if len(exposure.sources) > 1 else "transform")
    event = Event("Merge" if len(exposure.sources) > 1 else "Derive",
                  {"id": "p-"+key, "artifact": asdict(artifact), "exposure": asdict(exposure),
                   "capture_scope": "explicit host inputs only; no semantic causality claim"})
    engine.apply(event)
    return event
