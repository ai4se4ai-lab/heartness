"""Experience-mediated exposure: behaviour -> experience -> reflection propagation."""
from dataclasses import asdict

import pytest

from heartness import Artifact, Engine, Event
from heartness.engine import Rejected


def admit(e: Engine, artifact: Artifact, op: str = "Propose") -> None:
    pid = "p-" + artifact.id
    e.apply(Event(op, {"id": pid, "artifact": asdict(artifact)}))
    e.apply(Event("Validate", {"id": pid, "passed": True}))
    e.apply(Event("Accept", {"id": pid}))


def scenario(disabled: frozenset[str] = frozenset()) -> Engine:
    e = Engine(disabled=disabled)
    e.apply(Event("Experience", {"id": "e0", "task": "t0", "run": "r0", "outcome": "fail"}))
    admit(e, Artifact("m0", "memory", "print results", experiences=("e0",)))
    admit(e, Artifact("u", "memory", "unrelated", authorized_seed=True))
    # run r1 loads m0 into its context; its experience motivates m1 without a synthesis edge
    e.apply(Event("Load", {"run": "r1", "context": ["m0"]}))
    e.apply(Event("Experience", {"id": "e1", "task": "t1", "run": "r1", "outcome": "fail"}))
    admit(e, Artifact("m1", "memory", "outputs go to stdout", experiences=("e1",)))
    return e


def test_mediated_edge_enters_withdrawal_closure() -> None:
    e = scenario()
    assert e.graph.mediated["m0"] == {"m1"}
    e.apply(Event("Withdraw", {"id": "m0"}))
    assert e.state.active == {"u"}
    assert "m1" in e.state.quarantined


def test_ablation_without_eme_leaves_mediated_descendant_active() -> None:
    e = scenario(frozenset({"EME"}))
    e.apply(Event("Withdraw", {"id": "m0"}))
    assert e.state.active == {"u", "m1"}


def test_context_must_be_active_or_deployed() -> None:
    e = scenario()
    with pytest.raises(Rejected):
        e.apply(Event("Load", {"run": "r2", "context": ["missing"]}))
    e.apply(Event("Withdraw", {"id": "m0"}))
    with pytest.raises(Rejected):
        e.apply(Event("Load", {"run": "r3", "context": ["m0"]}))


def test_load_without_context_records_full_active_state() -> None:
    e = scenario()
    e.apply(Event("Load", {"run": "r4"}))
    assert e.state.loaded["r4"][1] == ("m0", "m1", "u")


def test_revalidated_readmission_is_a_fresh_attested_lineage() -> None:
    """Closure-bounded revalidation re-admits screened content as a new seed revision."""
    e = scenario()
    e.apply(Event("Withdraw", {"id": "m0"}))
    text = e.state.artifacts["m1"].text
    admit(e, Artifact("m1-r", "memory", text, authorized_seed=True, derivation="seed"))
    assert "m1-r" in e.state.active and "m1" in e.state.quarantined
    # the withdrawn lineage itself can never be re-activated
    with pytest.raises(Rejected):
        admit(e, Artifact("m2", "memory", "x", sources=("m1",)))


def test_only_the_recorded_context_creates_mediated_edges() -> None:
    e = scenario()
    assert e.state.loaded["r1"][1] == ("m0",)
    e.apply(Event("Withdraw", {"id": "u"}))  # u was active but not in r1's context
    assert "m1" in e.state.active


def test_retire_removes_one_revision_without_closure() -> None:
    e = scenario()
    admit(e, Artifact("k", "skill", "uses m1", sources=("m1",)))
    e.apply(Event("Deploy", {"deployment": "d", "active": ["m1", "k"]}))
    e.apply(Event("Retire", {"id": "m1"}))
    assert "m1" not in e.state.active and "k" in e.state.active
    assert e.state.deployments["d"] == ("k",)
    assert e.state.versions[-1].reason == "retire:m1"


def test_retire_refuses_to_break_a_dependency() -> None:
    e = scenario()
    admit(e, Artifact("k", "skill", "needs u", dependencies=("u",), authorized_seed=True))
    with pytest.raises(Rejected):
        e.apply(Event("Retire", {"id": "u"}))
    with pytest.raises(Rejected):
        e.apply(Event("Retire", {"id": "missing"}))


def test_load_after_experience_is_rejected() -> None:
    """Late Load would retroactively expose accepted revisions; the engine refuses it."""
    import pytest

    from heartness import Engine, Event, Rejected
    e = Engine()
    e.apply(Event("Experience", {"id": "e9", "task": "t", "run": "r9", "outcome": "fail"}))
    with pytest.raises(Rejected):
        e.apply(Event("Load", {"run": "r9", "context": []}))


def test_withdrawing_an_experience_blocks_relearning_from_it() -> None:
    """Withdrawing the corrupted experience covers revisions motivated by it, now and later."""
    e = scenario()
    e.apply(Event("Withdraw", {"id": "e0"}))
    assert "m0" in e.state.withdrawn and "m1" in e.state.quarantined  # m1 via EME from m0
    # the policy re-reads its experience pool and re-derives the lesson: refused
    with pytest.raises(Rejected):
        admit(e, Artifact("m0b", "memory", "print results", experiences=("e0",)))
    # unrelated evidence is unaffected
    e.apply(Event("Experience", {"id": "e9", "task": "t9", "run": "r9", "outcome": "pass"}))
    admit(e, Artifact("m9", "memory", "return values", experiences=("e9",)))
    assert "m9" in e.state.active


def test_withdrawing_only_the_revision_still_admits_relearning() -> None:
    """Documents the scope of revision withdrawal (the reason experience withdrawal exists)."""
    e = scenario()
    e.apply(Event("Withdraw", {"id": "m0"}))
    admit(e, Artifact("m0b", "memory", "print results", experiences=("e0",)))
    assert "m0b" in e.state.active
