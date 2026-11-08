from copy import deepcopy
from dataclasses import asdict, replace

import pytest
from hypothesis import given, settings, strategies as st

from heartness import Artifact, Contract, Engine, Event, Rejected
from heartness.model import ValidationRecord
from heartness.monitor import monitor
from heartness.properties import violations
from heartness.simulator import example, install


def attempt(engine, event):
    before = engine.state.hash
    with pytest.raises(Rejected):
        engine.apply(event)
    assert engine.state.hash == before


def seed(engine, key="x"):
    return install(engine, Artifact(key, "skill", "body", authorized_seed=True,
                                    contract=Contract(provides=("cap",))))


def test_example_withdraw_rollback():
    engine, events = example()
    assert not violations(engine)
    assert not monitor(events)
    plan = engine.withdrawal_plan("m1")
    assert plan["affected_active"] == ["a1", "a2", "m1", "s1"]
    before = deepcopy(engine.state)
    engine.apply(Event("Withdraw", {"id": "m1"}))
    assert engine.state.active == {"m2"}
    assert all(set(a) == {"m2"} for a in engine.state.deployments.values())
    assert not violations(engine, before)
    assert engine.state.effects == before.effects
    assert len(engine.rollback_plan(0)["external_effects_not_reversed"]) == 1
    assert not engine.rollback_plan(5)["admissible"]
    attempt(engine, Event("Rollback", {"version": 5}))
    engine.apply(Event("Rollback", {"version": 0}))
    assert not engine.state.active
    assert not violations(engine)
    assert engine.last_good_version("m1") is not None
    assert engine.culprit_revision("m1") == 1
    assert engine.culprit_revision("missing") is None


def test_guards_and_transactionality():
    e = Engine()
    bad = Artifact("x", "skill", "no history")
    attempt(e, Event("Propose", {"id": "p", "artifact": asdict(bad)}))
    for a in (replace(bad, sources=("x",)), replace(bad, kind="nonsense", authorized_seed=True),
              replace(bad, experiences=("unknown",)), replace(bad, dependencies=("unknown",))):
        attempt(e, Event("Propose", {"id": "p", "artifact": asdict(a)}))
    a = replace(bad, authorized_seed=True)
    event = Event("Propose", {"id": "p", "artifact": asdict(a)})
    e.apply(event)
    attempt(e, event)
    attempt(e, Event("Propose", {"id": "other", "artifact": asdict(a)}))
    attempt(e, Event("Accept", {"id": "p"}))
    e.apply(Event("Validate", {"id": "p", "passed": False}))
    attempt(e, Event("Accept", {"id": "p"}))
    e.apply(Event("Validate", {"id": "p", "passed": True}))
    e.state.validations["p"] = ValidationRecord("p", "drift", 0, True)
    attempt(e, Event("Accept", {"id": "p"}))
    e.apply(Event("Validate", {"id": "p", "passed": True}))
    e.apply(Event("Accept", {"id": "p"}))
    attempt(e, Event("Accept", {"id": "p"}))
    attempt(e, Event("Validate", {"id": "p", "passed": True}))
    attempt(e, Event("Unknown", {}))
    attempt(e, Event("Rollback", {"version": -1}))
    attempt(e, Event("Withdraw", {"id": "missing"}))
    attempt(e, Event("Deploy", {"deployment": "d", "active": ["missing"]}))


def test_stale_base():
    e = Engine()
    seed(e, "x")
    a = Artifact("y", "skill", "new", authorized_seed=True)
    e.apply(Event("Propose", {"id": "p", "artifact": asdict(a), "base": 0}))
    e.apply(Event("Validate", {"id": "p", "passed": True}))
    attempt(e, Event("Accept", {"id": "p"}))


def test_derive_edit_merge_quarantine():
    e = Engine()
    seed(e, "x")
    seed(e, "z")
    install(e, Artifact("y", "memory", "summary", sources=("x",)), "Derive")
    install(e, Artifact("m", "prompt", "merged", sources=("x", "z"), derivation="merge"), "Merge")
    install(e, Artifact("x2", "skill", "edit", sources=("x",), derivation="edit"), "Edit", "x")
    assert "x" not in e.state.active and "x" in e.state.artifacts
    assert not violations(e)
    attempt(e, Event("Merge", {"id": "q", "artifact": asdict(Artifact(
        "q", "skill", "bad", sources=("y",)))}))
    attempt(e, Event("Edit", {"id": "q", "artifact": asdict(Artifact(
        "q", "skill", "bad", sources=("y",))), "replaces": "z"}))
    e.apply(Event("Quarantine", {"id": "x"}))
    assert not {"y", "x2", "m"} & e.state.active
    assert not violations(e)
    a = Artifact("q", "skill", "revive", sources=("x",))
    e.apply(Event("Propose", {"id": "q", "artifact": asdict(a)}))
    e.apply(Event("Validate", {"id": "q", "passed": True}))
    attempt(e, Event("Accept", {"id": "q"}))


def test_contracts_load_and_effects():
    e = Engine()
    seed(e)
    consumer = Artifact("consumer", "agent", "use x", dependencies=("x",),
                        authorized_seed=True, contract=Contract(requires=("cap",)))
    install(e, consumer)
    wrong = Artifact("x2", "skill", "loses cap", sources=("x",))
    e.apply(Event("Edit", {"id": "p", "artifact": asdict(wrong), "replaces": "x"}))
    e.apply(Event("Validate", {"id": "p", "passed": True}))
    attempt(e, Event("Accept", {"id": "p"}))
    attempt(e, Event("Deploy", {"deployment": "d", "active": ["consumer"]}))
    e.apply(Event("Load", {"run": "r"}))
    attempt(e, Event("Load", {"run": "r"}))
    e.apply(Event("Effect", {"id": "f", "run": "r", "description": "sent"}))
    attempt(e, Event("Effect", {"id": "f", "run": "r", "description": "sent"}))
    before = e.state.artifacts["x"]
    e.state.artifacts["x"] = replace(before, text="drift")
    attempt(e, Event("Load", {"run": "r2"}))
    assert "P4" in violations(e)


def test_monitor_deviation_boundaries():
    _, events = example()
    corrupted = list(events)
    corrupted[-1] = replace(corrupted[-1], observed="bad-digest")
    assert monitor(corrupted)[0].kind == "state_mismatch"
    assert monitor([Event("Accept", {"id": "unknown"})])[0].kind == "rejected"
    assert not monitor(events)  # A hidden external action with no event is unobservable.


def test_auditor_injected_corruption():
    e, _ = example()
    before = deepcopy(e.state)
    e.state.artifacts["orphan"] = Artifact("orphan", "skill", "missing history")
    assert "P1" in violations(e)
    e.state.artifacts["orphan"] = Artifact("orphan", "skill", "cycle", sources=("orphan",))
    assert "P6" in violations(e)
    e.state.withdrawn.add("m1")
    assert {"P2", "P8"} <= set(violations(e))
    e.state.history.pop()
    assert "P7" in violations(e, before)
    e.state.history[-1]["previous"] = "edited"
    assert "P10" in violations(e)
    e.state.effects.clear()
    assert "P5" in violations(e, before)


@settings(max_examples=100, deadline=None, derandomize=True)
@given(st.lists(st.tuples(st.sampled_from(["withdraw", "rollback", "deploy", "quarantine"]),
                         st.integers(min_value=0, max_value=5)), max_size=25))
def test_random_evolution_preserves_properties(sequence):
    e, _ = example()
    for op, i in sequence:
        before = deepcopy(e.state)
        if op in {"withdraw", "quarantine"}:
            event = Event(op.title(), {"id": ["m1", "m2", "s1", "a1", "a2", "absent"][i]})
        elif op == "rollback":
            event = Event("Rollback", {"version": i})
        else:
            event = Event("Deploy", {"deployment": "d" + str(i)})
        try:
            e.apply(event)
        except Rejected:
            assert e.state.hash == before.hash
        assert not violations(e, before)
