r"""Closure-bounded revalidation (Algorithm 5), composed from ordinary engine operators.

After Withdraw(R) quarantines the affected set A, a screen clears some members of A \ R. Only
members that were in use (active or deployed) before the withdrawal are candidates, so a revision
that a later version had already replaced does not come back beside its successor. Candidates are
processed in history order; a member whose dependency is neither active nor re-admitted is
rejected (the admission guard P3 would refuse it). If any member is admissible, one ATTESTATION
revision <R, screen, cleared set> is admitted first (a host-authorized seed).

Each admitted member x becomes a FRESH revision x' with x's text and contract. Its lineage is
x's lineage with the withdrawn part replaced by the attestation: sources are the attestation,
x's sources outside the forbidden closure (active or not), and the re-admitted copies of
cleared sources; experiences of
x are kept if their run context avoided the forbidden closure; every source or experience that
cannot be kept is replaced by its CLEAN FRONTIER (nearest ancestors outside the forbidden
closure, active or not); dependencies are dep(x) with quarantined dependencies replaced by their copies. A later
withdrawal of the attestation or of any clean ancestor therefore reaches x'. Revalidation adds no
operator and no semantics: P2/P8 and Proposition 2 cover it unchanged.

`plan` is a pure function shared by the engine execution (`revalidate`) and the live-study
evaluation (experiments/live/supplement.py), so both yield the same loadable state.
"""
from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass, field

from heartness.engine import Engine, Rejected
from heartness.model import Artifact, Event


def fresh_id(key: str) -> str:
    return key + "~r"


@dataclass(frozen=True)
class Plan:
    admitted: dict[str, str] = field(default_factory=dict)  # original -> fresh copy
    rejected: dict[str, str] = field(default_factory=dict)  # original -> reason


def plan(order: Sequence[str], dependencies: Mapping[str, Iterable[str]], active: set[str],
         cleared: set[str]) -> Plan:
    """Which cleared members Algorithm 5 re-admits, given the active set after withdrawal.

    `order` is the history (acceptance) order of all revisions; `dependencies[x]` is dep(x).
    """
    result = Plan()
    for key in order:
        if key not in cleared:
            continue
        missing = [d for d in dependencies.get(key, ()) if d not in active
                   and d not in result.admitted]
        if missing:
            result.rejected[key] = "dependency not active: " + ",".join(sorted(missing))
        else:
            result.admitted[key] = fresh_id(key)
    return result


def revalidate(engine: Engine, roots: str | Iterable[str], cleared: set[str], screen: str,
               deployments_before: Mapping[str, Iterable[str]],
               active_before: Iterable[str]) -> Plan:
    """Execute Algorithm 5 on the engine with ordinary Propose/Validate/Accept/Deploy events."""
    s = engine.state
    roots = (roots,) if isinstance(roots, str) else tuple(sorted(roots))
    affected = engine.graph.closure(roots, dependencies=True) - set(roots)
    # C is drawn from the affected set A \ R, and only from revisions in use before the
    # withdrawal: a revision a later version had already replaced must not come back beside it.
    in_use = set(active_before) | {a for members in deployments_before.values() for a in members}
    candidates = cleared & affected & s.quarantined & in_use
    order = list(s.artifacts)  # insertion order = acceptance order
    deps = {k: s.artifacts[k].dependencies for k in order}
    p = plan(order, deps, set(s.active), candidates)
    if not p.admitted:
        return p
    attestation = Artifact(
        "att~" + "+".join(roots) + "~" + screen, "attestation",
        json.dumps({"roots": list(roots), "screen": screen, "cleared": sorted(candidates)}),
        authorized_seed=True, derivation="seed")
    _admit(engine, attestation)
    forbidden = engine.graph.closure(s.forbidden_roots(), dependencies=True)
    done: dict[str, str] = {}
    for key, new in p.admitted.items():
        x = s.artifacts[key]
        # Keep every part of x's lineage that is not withdrawn, so that a LATER withdrawal of a
        # clean ancestor still reaches the copy: clean sources stay (active or not), re-admitted
        # sources map to their copies, and experiences stay if they are not withdrawn and their
        # run context avoided the forbidden closure. Only withdrawn lineage is replaced by the
        # attestation.
        sources = [attestation.id] + [done.get(y, y) for y in x.sources
                                      if y in done or y not in forbidden]
        experiences = tuple(e for e in x.experiences if e not in s.tainted and not set(
            s.loaded.get(s.experiences[e].run, (0, ()))[1]) & forbidden)
        # Parts of the lineage that cannot be kept (quarantined sources, experiences whose run
        # loaded forbidden state) are replaced by their CLEAN FRONTIER: the nearest clean
        # ancestor revisions and clean motivating experiences, so that withdrawing any of them
        # later still reaches x'.
        dropped = [y for y in x.sources if y not in done and y not in sources]
        dropped += [a for e in x.experiences if e not in experiences
                    for a in s.loaded.get(s.experiences[e].run, (0, ()))[1]]
        revs, exps = clean_frontier(engine, dropped, forbidden, done)
        sources += sorted(revs - set(sources))
        experiences += tuple(sorted(exps - set(experiences)))
        copy = Artifact(new, x.kind, x.text, sources=tuple(dict.fromkeys(sources)),
                        dependencies=tuple(done.get(d, d) for d in x.dependencies),
                        experiences=experiences, derivation="copy", contract=x.contract,
                        path=x.path)
        try:
            _admit(engine, copy)
        except Rejected as exc:  # admission guards have the last word
            p.rejected[key] = "admission: " + str(exc)
            continue
        done[key] = new
    for key in [k for k in p.admitted if k not in done]:
        del p.admitted[key]
    for deployment, before in deployments_before.items():
        back = {done[k] for k in before if k in done}
        if back:
            current = set(s.deployments.get(deployment, ())) | back
            engine.apply(Event("Deploy", {"deployment": deployment, "active": sorted(current)}))
    return p


def clean_frontier(engine: Engine, start: Iterable[str], forbidden: set[str],
                   done: Mapping[str, str]) -> tuple[set[str], set[str]]:
    """Nearest clean ancestors of `start`, walking back over sources, dependencies and EME
    contexts: revisions outside the forbidden closure (active or not) or their re-admitted copies,
    and the motivating experiences of forbidden intermediates that are not withdrawn and whose
    run context avoided the forbidden closure."""
    s = engine.state
    found: set[str] = set()
    found_exps: set[str] = set()
    seen: set[str] = set()
    todo = list(start)
    while todo:
        y = todo.pop()
        if y in seen or y not in s.artifacts:
            continue
        seen.add(y)
        if y in done:
            found.add(done[y])
        elif y not in forbidden:  # clean, active or not (retired/replaced ancestors count)
            found.add(y)
        else:
            a = s.artifacts[y]
            todo += list(a.sources) + list(a.dependencies)
            for e in a.experiences:
                ctx = s.loaded.get(s.experiences[e].run, (0, ()))[1]
                if e not in s.tainted and not set(ctx) & forbidden:
                    found_exps.add(e)
                todo += list(ctx)
    return found, found_exps


def _admit(engine: Engine, artifact: Artifact) -> None:
    pid = "reval-" + artifact.id
    engine.apply(Event("Propose", {"id": pid, "artifact": asdict(artifact)}))
    engine.apply(Event("Validate", {"id": pid, "passed": True}))
    engine.apply(Event("Accept", {"id": pid}))
