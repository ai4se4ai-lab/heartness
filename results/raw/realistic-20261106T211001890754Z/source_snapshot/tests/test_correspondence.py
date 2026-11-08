from experiments.correspondence import compare_reference, mapped, translated_event
from heartness import Engine
from heartness.checker import initial, step


def test_reference_transition_correspondence():
    for topology in ("chain", "independent"):
        result = compare_reference(2, 6, topology)
        assert not result["mismatches"], result["mismatches"][:2]


def test_deploy_replaces_after_rollback():
    e, state = Engine(), initial(2)
    path = [("propose", 0), ("validate", 0), ("accept", 0), ("deploy", 0),
            ("propose", 1), ("validate", 1), ("accept", 1), ("deploy", 0),
            ("rollback", 1), ("deploy", 0)]
    for action in path:
        state = step(state, action, 2, topology="independent")
        assert state is not None
        e.apply(translated_event(e, action, 2, "independent"))
        assert mapped(e, 2) == state
    assert e.state.deployments["d"] == ("a0",)
