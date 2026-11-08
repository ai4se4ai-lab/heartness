"""Transactional, policy-independent evolution operators and append-only audit."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from typing import Any

from heartness.graph import Graph
from heartness.model import (
    DERIVATIONS,
    KINDS,
    Artifact,
    Event,
    Experience,
    ExternalEffect,
    HarnessVersion,
    Proposal,
    State,
    ValidationRecord,
    digest,
)


class Rejected(ValueError):
    """An inadmissible event leaves the entire prior state unchanged."""


class Engine:
    def __init__(self, *, disabled: frozenset[str] = frozenset()) -> None:
        self.state = State(versions=[HarnessVersion(0, (), (), "seed")])
        self.disabled = disabled

    @property
    def graph(self) -> Graph:
        return Graph(self.state.artifacts)

    def require(self, condition: bool, message: str, property_id: str = "") -> None:
        if not condition and property_id not in self.disabled:
            raise Rejected(message)

    def _snapshot(self, reason: str) -> None:
        s = self.state
        s.versions.append(HarnessVersion(
            len(s.versions), tuple(sorted(s.active)),
            tuple((a, s.artifacts[a].hash) for a in sorted(s.active)), reason,
        ))

    def _safe(self, active: set[str]) -> bool:
        s = self.state
        forbidden = s.withdrawn | s.quarantined
        affected = self.graph.closure(forbidden, dependencies=True)
        return not bool(active & affected)

    def _consistent(self, active: set[str]) -> bool:
        s = self.state
        for key in active:
            item = s.artifacts[key]
            if not set(item.dependencies) <= active:
                return False
            available = {p for d in item.dependencies for p in s.artifacts[d].contract.provides}
            if not set(item.contract.requires) <= available:
                return False
        return True

    def _admissible(self, active: set[str]) -> None:
        self.require(self._safe(active), "withdrawn/quarantined lineage", "P2")
        self.require(self._consistent(active), "stale or absent dependency", "P3")

    def _suspend(self, root: str) -> set[str]:
        s = self.state
        affected = self.graph.closure([root], dependencies=True)
        s.quarantined.update(affected - {root})
        s.active.difference_update(affected)
        if "P8" not in self.disabled:
            for deployment, active in list(s.deployments.items()):
                s.deployments[deployment] = tuple(sorted(set(active) - affected))
        return affected

    def apply(self, event: Event) -> str:
        """Execute atomically; rejected guards roll back even intermediate writes."""
        before = deepcopy(self.state)
        try:
            self._dispatch(event)
            record = {"op": event.op, "args": deepcopy(event.args),
                      "previous": digest(self.state.history[-1]) if self.state.history else "root"}
            self.state.history.append(record)
            return self.state.hash
        except (Rejected, KeyError, TypeError, ValueError) as exc:
            self.state = before
            raise Rejected(str(exc)) from exc

    def _dispatch(self, event: Event) -> None:
        s, args, op = self.state, event.args, event.op
        if op == "Experience":
            e = Experience(**args)
            self.require(e.id not in s.experiences, "duplicate experience")
            s.experiences[e.id] = e
        elif op in {"Propose", "Derive", "Edit", "Merge"}:
            a = Artifact.from_dict(args["artifact"])
            pid = str(args["id"])
            sources = set(a.sources)
            self.require(pid not in s.proposals and a.id not in s.artifacts, "duplicate revision")
            self.require(all(p.artifact.id != a.id for p in s.proposals.values()), "pending ID")
            self.require(a.kind in KINDS and a.derivation in DERIVATIONS, "unknown type")
            self.require(sources <= s.artifacts.keys() and a.id not in sources,
                         "unknown source or self-derivation", "P6")
            self.require(set(a.dependencies) <= s.artifacts.keys(), "unknown dependency")
            self.require(set(a.experiences) <= s.experiences.keys(), "unknown experience", "P1")
            self.require(bool(a.experiences or sources or a.authorized_seed), "no history", "P1")
            self.require(op != "Merge" or len(sources) >= 2, "merge needs multiple sources")
            replaces = args.get("replaces")
            self.require(op != "Edit" or replaces in sources, "edit must retain prior revision")
            motivated = tuple(args.get("motivated_by", a.experiences))
            self.require(set(motivated) <= s.experiences.keys(), "unknown motivation", "P1")
            self.require(type(args.get("base", len(s.versions) - 1)) is int, "base must be integer")
            s.proposals[pid] = Proposal(pid, a, int(args.get("base", len(s.versions) - 1)),
                                        motivated, replaces)
        elif op == "Validate":
            pid = str(args["id"])
            p = s.proposals[pid]
            self.require(pid not in s.accepted, "already accepted")
            self.require(type(args["passed"]) is bool, "validation result must be Boolean")
            s.validations[pid] = ValidationRecord(pid, p.artifact.hash, p.base, args["passed"])
        elif op == "Accept":
            pid = str(args["id"])
            p, validation = s.proposals[pid], s.validations[pid]
            self.require(pid not in s.accepted, "already accepted")
            self.require(validation.passed and validation.artifact_hash == p.artifact.hash,
                         "not the validated candidate", "P4")
            self.require(p.base == len(s.versions) - 1, "stale proposal base", "P9")
            s.artifacts[p.artifact.id] = p.artifact
            candidate = s.active | {p.artifact.id}
            if p.replaces is not None:
                self.require(p.replaces in s.active, "replacement is not active")
                candidate.remove(p.replaces)
            self._admissible(candidate)
            s.active = candidate
            s.accepted.add(pid)
            self._snapshot("accept:" + pid)
        elif op in {"Withdraw", "Quarantine"}:
            root = str(args["id"])
            self.require(root in s.artifacts, "unknown artifact")
            if op == "Withdraw":
                s.withdrawn.add(root)
            else:
                s.quarantined.add(root)
            if "P2" in self.disabled:
                s.active.discard(root)
            else:
                self._suspend(root)
            self._snapshot(op.lower() + ":" + root)
        elif op == "Rollback":
            self.require(type(args["version"]) is int, "version must be integer")
            version = int(args["version"])
            self.require(0 <= version < len(s.versions), "unknown version")
            target = set(s.versions[version].active)
            # Exact restoration is incompatible with global revocation: reject it.
            self._admissible(target)
            s.active = target
            self._snapshot("rollback:" + str(version))
        elif op in {"Deploy", "Reuse"}:
            deployment = str(args["deployment"])
            active = set(args.get("active", sorted(s.active)))
            self.require(active <= s.artifacts.keys(), "unknown deployment artifact")
            self._admissible(active)
            s.deployments[deployment] = tuple(sorted(active))
        elif op == "Load":
            run = str(args["run"])
            self.require(run not in s.loaded, "duplicate run")
            version = len(s.versions) - 1
            loaded_active = tuple(sorted(s.active))
            self.require(dict(s.versions[version].hashes) ==
                         {a: s.artifacts[a].hash for a in loaded_active}, "snapshot content drift", "P4")
            s.loaded[run] = (version, loaded_active)
        elif op == "Effect":
            run = str(args["run"])
            self.require(all(e.id != str(args["id"]) for e in s.effects), "duplicate effect")
            version = s.loaded[run][0]
            s.effects.append(ExternalEffect(str(args["id"]), run, version, str(args["description"])))
        else:
            raise Rejected("unknown operator: " + op)

    def withdrawal_plan(self, root: str) -> dict[str, Any]:
        s = self.state
        all_active = s.active | {a for values in s.deployments.values() for a in values}
        return {
            "root": root,
            "affected_active": sorted(self.graph.impact(root, all_active)),
            "deployments": {d: sorted(self.graph.impact(root, active))
                            for d, active in sorted(s.deployments.items())},
            "actions": ["suspend affected revisions", "inspect derivatives", "propose fresh revisions"],
            "external_effects_not_reversed": [asdict(e) for e in s.effects],
            "complete_only_for_recorded_edges": True,
        }

    def rollback_plan(self, version: int) -> dict[str, Any]:
        target = set(self.state.versions[version].active)
        return {"target": version, "active": sorted(target),
                "admissible": self._safe(target) and self._consistent(target),
                "external_effects_not_reversed": [asdict(e) for e in self.state.effects]}

    def last_good_version(self, root: str) -> int | None:
        affected = self.graph.closure([root], dependencies=True)
        for version in reversed(self.state.versions):
            if not set(version.active) & affected and self._safe(set(version.active)):
                return version.id
        return None

    def culprit_revision(self, artifact: str) -> int | None:
        """First installation, a diagnostic candidate rather than a causal finding."""
        return next((v.id for v in self.state.versions if artifact in v.active), None)
