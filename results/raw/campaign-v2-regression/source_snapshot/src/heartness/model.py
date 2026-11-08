"""Immutable typed records; mutable state is owned exclusively by the engine."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any

KINDS = {"memory", "skill", "prompt", "workflow", "tool", "agent", "executable"}
DERIVATIONS = {"copy", "summary", "transform", "merge", "edit", "seed"}


def canonical(value: Any) -> str:
    """Canonical semantic serialization, independent of Python hash randomization."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


@dataclass(frozen=True)
class Contract:
    """Finite capability requirements, not semantic claims about natural language."""

    requires: tuple[str, ...] = ()
    provides: tuple[str, ...] = ()


@dataclass(frozen=True)
class Experience:
    id: str
    task: str
    run: str
    outcome: str


@dataclass(frozen=True)
class Artifact:
    id: str
    kind: str
    text: str
    sources: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    experiences: tuple[str, ...] = ()
    authorized_seed: bool = False
    derivation: str = "transform"
    contract: Contract = field(default_factory=Contract)
    path: str = ""

    @property
    def hash(self) -> str:
        return digest(asdict(self))

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Artifact:
        fields = dict(data)
        if any(not isinstance(fields.get(key), str) for key in ("id", "kind", "text")):
            raise ValueError("artifact identity, type and text must be strings")
        if type(fields.get("authorized_seed", False)) is not bool:
            raise ValueError("authorized_seed must be a Boolean host assertion")
        for key in ("sources", "dependencies", "experiences"):
            if not isinstance(fields.get(key, ()), (list, tuple)) or any(
                    not isinstance(value, str) for value in fields.get(key, ())):
                raise ValueError("references must be lists of string identities")
            fields[key] = tuple(fields.get(key, ()))
        c = fields.get("contract", {})
        fields["contract"] = Contract(tuple(c.get("requires", ())), tuple(c.get("provides", ())))
        return Artifact(**fields)


@dataclass(frozen=True)
class Proposal:
    id: str
    artifact: Artifact
    base: int
    motivated_by: tuple[str, ...]
    replaces: str | None = None


@dataclass(frozen=True)
class ValidationRecord:
    proposal: str
    artifact_hash: str
    base: int
    passed: bool


@dataclass(frozen=True)
class HarnessVersion:
    id: int
    active: tuple[str, ...]
    hashes: tuple[tuple[str, str], ...]
    reason: str


@dataclass(frozen=True)
class ExternalEffect:
    id: str
    run: str
    version: int
    description: str


@dataclass(frozen=True)
class Event:
    op: str
    args: dict[str, Any]
    observed: str = ""


@dataclass
class State:
    experiences: dict[str, Experience] = field(default_factory=dict)
    artifacts: dict[str, Artifact] = field(default_factory=dict)
    proposals: dict[str, Proposal] = field(default_factory=dict)
    validations: dict[str, ValidationRecord] = field(default_factory=dict)
    accepted: set[str] = field(default_factory=set)
    withdrawn: set[str] = field(default_factory=set)
    quarantined: set[str] = field(default_factory=set)
    active: set[str] = field(default_factory=set)
    versions: list[HarnessVersion] = field(default_factory=list)
    deployments: dict[str, tuple[str, ...]] = field(default_factory=dict)
    loaded: dict[str, tuple[int, tuple[str, ...]]] = field(default_factory=dict)
    effects: list[ExternalEffect] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)

    def semantic(self) -> dict[str, Any]:
        data = asdict(self)
        for key in ("accepted", "withdrawn", "quarantined", "active"):
            data[key] = sorted(data[key])
        return data

    @property
    def hash(self) -> str:
        return digest(self.semantic())
