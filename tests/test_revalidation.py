"""Closure-bounded revalidation (Algorithm 5) composed from ordinary operators."""
from dataclasses import asdict

import pytest

from heartness import Artifact, Engine, Event
from heartness.engine import Rejected
from heartness.revalidation import plan, revalidate


def admit(e: Engine, artifact: Artifact) -> None:
    pid = "p-" + artifact.id
    e.apply(Event("Propose", {"id": pid, "artifact": asdict(artifact)}))
    e.apply(Event("Validate", {"id": pid, "passed": True}))
    e.apply(Event("Accept", {"id": pid}))


def harness() -> Engine:
    """Running example: m7 -> k1 -> profile p (p depends on k0 and k1)."""
    e = Engine()
    e.apply(Event("Experience", {"id": "e7", "task": "t7", "run": "r7", "outcome": "fail"}))
    admit(e, Artifact("m6", "memory", "check edge cases", authorized_seed=True))
    admit(e, Artifact("m7", "memory", "print instead of return", experiences=("e7",)))
    admit(e, Artifact("k0", "skill", "iterate once", authorized_seed=True))
    admit(e, Artifact("k1", "skill", "merge of m6 and m7", sources=("m6", "m7")))
    admit(e, Artifact("p", "agent", "profile", sources=("k0", "k1"), dependencies=("k0", "k1")))
    e.apply(Event("Deploy", {"deployment": "D1", "active": ["k0", "k1", "m6", "m7", "p"]}))
    return e


def withdraw(e: Engine) -> tuple[dict[str, tuple[str, ...]], set[str]]:
    before, active = dict(e.state.deployments), set(e.state.active)
    e.apply(Event("Withdraw", {"id": "m7"}))
    assert {"k1", "p"} <= e.state.quarantined
    return before, active


def test_dependent_is_rejected_while_its_dependency_stays_quarantined() -> None:
    e = harness()
    before, active = withdraw(e)
    result = revalidate(e, "m7", {"p"}, "judge", before, active)
    assert result.admitted == {} and "p" in result.rejected
    assert "p" not in e.state.active and "p~r" not in e.state.artifacts


def test_cleared_chain_is_readmitted_in_history_order_with_mapped_dependencies() -> None:
    e = harness()
    before, active = withdraw(e)
    result = revalidate(e, "m7", {"k1", "p"}, "judge", before, active)
    assert result.admitted == {"k1": "k1~r", "p": "p~r"}
    copy = e.state.artifacts["p~r"]
    assert copy.sources == ("att~m7~judge", "k0", "k1~r") and copy.dependencies == ("k0", "k1~r")
    assert e.state.artifacts["k1~r"].sources == ("att~m7~judge", "m6")
    assert {"k1~r", "p~r"} <= e.state.active and {"k1", "p"} <= e.state.quarantined
    assert {"k1~r", "p~r"} <= set(e.state.deployments["D1"])
    # the withdrawn lineage itself stays blocked
    with pytest.raises(Rejected):
        admit(e, Artifact("k2", "skill", "x", sources=("k1",)))


def test_withdrawing_the_attestation_withdraws_every_readmission() -> None:
    e = harness()
    before, active = withdraw(e)
    revalidate(e, "m7", {"k1", "p"}, "judge", before, active)
    e.apply(Event("Withdraw", {"id": "att~m7~judge"}))
    assert not {"k1~r", "p~r"} & e.state.active
    assert not {"k1~r", "p~r"} & set(e.state.deployments["D1"])


def test_pure_plan_agrees_with_engine_execution() -> None:
    for cleared in ({"k1"}, {"p"}, {"k1", "p"}, set()):
        e = harness()
        before, active = withdraw(e)
        order = list(e.state.artifacts)
        deps = {k: e.state.artifacts[k].dependencies for k in order}
        expected = plan(order, deps, set(e.state.active), cleared)
        assert revalidate(e, "m7", set(cleared), "judge", before, active).admitted == expected.admitted


def test_copy_keeps_clean_lineage_so_a_later_withdrawal_reaches_it() -> None:
    """Withdraw m7, re-admit k1 (sources m6, m7), then withdraw m6: the copy must follow."""
    e = harness()
    before, active = withdraw(e)
    revalidate(e, "m7", {"k1"}, "judge", before, active)
    assert "k1~r" in e.state.active and "k1~r" in e.state.deployments["D1"]
    e.apply(Event("Withdraw", {"id": "m6"}))
    assert "k1~r" not in e.state.active and "k1~r" not in e.state.deployments["D1"]


def test_frontier_keeps_clean_ancestor_reached_through_a_quarantined_source() -> None:
    """Case A: z -> y (quarantined with m7) -> p; re-admitting p must keep z in its lineage."""
    e = Engine()
    e.apply(Event("Experience", {"id": "e7", "task": "t", "run": "r7", "outcome": "fail"}))
    admit(e, Artifact("z", "memory", "clean seed", authorized_seed=True))
    admit(e, Artifact("m7", "memory", "faulty", experiences=("e7",)))
    admit(e, Artifact("y", "skill", "merge", sources=("z", "m7")))
    admit(e, Artifact("p", "agent", "profile", sources=("y",)))
    e.apply(Event("Deploy", {"deployment": "D", "active": ["m7", "p", "y", "z"]}))
    before, active = dict(e.state.deployments), set(e.state.active)
    e.apply(Event("Withdraw", {"id": "m7"}))
    revalidate(e, "m7", {"p"}, "judge", before, active)
    assert "z" in e.state.artifacts["p~r"].sources
    e.apply(Event("Withdraw", {"id": "z"}))
    assert "p~r" not in e.state.active


def test_frontier_keeps_clean_context_of_a_dropped_experience() -> None:
    """Case B: memory motivated by a run that loaded {z, m7}: z stays in the copy's lineage."""
    e = Engine()
    e.apply(Event("Experience", {"id": "e7", "task": "t", "run": "r7", "outcome": "fail"}))
    admit(e, Artifact("z", "memory", "clean seed", authorized_seed=True))
    admit(e, Artifact("m7", "memory", "faulty", experiences=("e7",)))
    e.apply(Event("Load", {"run": "r8", "context": ["m7", "z"]}))
    e.apply(Event("Experience", {"id": "e8", "task": "t8", "run": "r8", "outcome": "fail"}))
    admit(e, Artifact("m8", "memory", "lesson", experiences=("e8",)))
    before, active = dict(e.state.deployments), set(e.state.active)
    e.apply(Event("Withdraw", {"id": "m7"}))
    revalidate(e, "m7", {"m8"}, "judge", before, active)
    assert "z" in e.state.artifacts["m8~r"].sources
    e.apply(Event("Withdraw", {"id": "z"}))
    assert "m8~r" not in e.state.active


def test_superseded_revision_is_not_readmitted_beside_its_successor() -> None:
    """A cleared revision that was no longer in use before the withdrawal stays out."""
    e = harness()
    admit(e, Artifact("p2", "agent", "profile v2", sources=("k0", "k1"), dependencies=("k0",)),)
    e.apply(Event("Deploy", {"deployment": "D1", "active": ["k0", "k1", "m6", "m7", "p2"]}))
    before, active = dict(e.state.deployments), set(e.state.deployments["D1"])
    e.apply(Event("Withdraw", {"id": "m7"}))
    result = revalidate(e, "m7", {"p", "p2"}, "judge", before, active)
    assert "p" not in result.admitted and "p~r" not in e.state.artifacts


def _chain_with(e: Engine) -> dict[str, tuple[str, ...]]:
    e.apply(Event("Experience", {"id": "e7", "task": "t", "run": "r7", "outcome": "fail"}))
    admit(e, Artifact("z", "memory", "clean", authorized_seed=True))
    admit(e, Artifact("m7", "memory", "faulty", experiences=("e7",)))
    admit(e, Artifact("k", "skill", "merge", sources=("z", "m7")))
    e.apply(Event("Deploy", {"deployment": "D", "active": ["k", "m7", "z"]}))
    return dict(e.state.deployments)


def test_retired_clean_source_stays_in_the_copy_lineage() -> None:
    """Probe C: a clean source retired before the withdrawal still reaches the copy."""
    e = Engine()
    before = _chain_with(e)
    e.apply(Event("Retire", {"id": "z"}))
    before, active = dict(e.state.deployments), set(e.state.active)
    e.apply(Event("Withdraw", {"id": "m7"}))
    revalidate(e, "m7", {"k"}, "judge", before, active)
    assert "z" in e.state.artifacts["k~r"].sources
    e.apply(Event("Withdraw", {"id": "z"}))
    assert "k~r" not in e.state.active


def test_replaced_clean_source_stays_in_the_copy_lineage() -> None:
    """Probe D: a clean source replaced by an edit still reaches the copy."""
    e = Engine()
    _chain_with(e)
    e.apply(Event("Edit", {"id": "p-z2", "replaces": "z", "artifact": asdict(
        Artifact("z2", "memory", "clean v2", sources=("z",), derivation="edit"))}))
    e.apply(Event("Validate", {"id": "p-z2", "passed": True}))
    e.apply(Event("Accept", {"id": "p-z2"}))
    before, active = dict(e.state.deployments), set(e.state.active)
    e.apply(Event("Withdraw", {"id": "m7"}))
    revalidate(e, "m7", {"k"}, "judge", before, active)
    assert "z" in e.state.artifacts["k~r"].sources
    e.apply(Event("Withdraw", {"id": "z"}))
    assert "k~r" not in e.state.active


def test_clean_experience_of_a_dropped_intermediate_stays_in_the_copy_lineage() -> None:
    """Probe E: y (sources m7, motivated by clean e9) -> x; withdrawing e9 must reach x's copy."""
    e = Engine()
    e.apply(Event("Experience", {"id": "e7", "task": "t", "run": "r7", "outcome": "fail"}))
    admit(e, Artifact("z", "memory", "clean seed", authorized_seed=True))
    admit(e, Artifact("m7", "memory", "faulty", experiences=("e7",)))
    e.apply(Event("Load", {"run": "r9", "context": ["z"]}))
    e.apply(Event("Experience", {"id": "e9", "task": "t9", "run": "r9", "outcome": "fail"}))
    admit(e, Artifact("y", "memory", "merge", sources=("m7",), experiences=("e9",)))
    admit(e, Artifact("x", "skill", "from y", sources=("y",)))
    e.apply(Event("Deploy", {"deployment": "D", "active": sorted(e.state.active)}))
    before, active = dict(e.state.deployments), set(e.state.active)
    e.apply(Event("Withdraw", {"id": "m7"}))
    revalidate(e, "m7", {"x"}, "judge", before, active)
    assert "e9" in e.state.artifacts["x~r"].experiences
    e.apply(Event("Withdraw", {"id": "e9"}))
    assert "x~r" not in e.state.active
