import pytest

from heartness.checker import bad, bfs, initial, masks, promela, replay, spin_check, step


@pytest.mark.parametrize("mutant", ["", "P2", "P3", "P4", "P8", "P9"])
def test_independent_checker(mutant):
    py = bfs(2, 9, mutant)
    spin = spin_check(2, 9, mutant)
    assert py["complete"] and spin["complete"], spin["log"]
    assert py["safe"] == spin["safe"], spin["log"]
    if mutant:
        assert not py["safe"]
        assert mutant in replay(py["trace"], 2, mutant)
        assert bfs(2, py["depth"] - 1, mutant)["safe"]
    else:
        assert py["safe"]


def test_bounds_and_replay():
    assert not bfs(5, 8, state_limit=10)["complete"]
    assert step(initial(2), ("accept", 0), 2) is None
    assert not bad(initial(2), 2)
    assert masks(3, "independent")[0] == (0, 0, 0)
    assert "assert" in promela(2, 5)
    with pytest.raises(ValueError):
        replay([["accept", 0]], 2)
