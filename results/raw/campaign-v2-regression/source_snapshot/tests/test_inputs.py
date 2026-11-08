from dataclasses import asdict

import pytest

from heartness import Artifact, Engine, Event, Rejected
from heartness.checker import bfs, initial, promela


def test_strict_json_types():
    engine = Engine()
    a = Artifact("a", "skill", "body", authorized_seed=True)
    engine.apply(Event("Propose", {"id": "p", "artifact": asdict(a)}))
    for result in ("false", "true", 0, 1, None):
        with pytest.raises(Rejected):
            engine.apply(Event("Validate", {"id": "p", "passed": result}))
    for version in (True, "0", .0):
        with pytest.raises(Rejected):
            engine.apply(Event("Rollback", {"version": version}))
    for overrides in ({"id": 1}, {"authorized_seed": "false"}, {"sources": "a"}):
        payload = asdict(a) | overrides
        with pytest.raises(ValueError):
            Artifact.from_dict(payload)


def test_projection_scope_rejection():
    for n in (0, 9):
        with pytest.raises(ValueError):
            initial(n)
    for depth in (0, 201):
        with pytest.raises(ValueError):
            promela(2, depth)
        with pytest.raises(ValueError):
            bfs(2, depth)
    assert not bfs(2, 10, seconds=0)["complete"]
