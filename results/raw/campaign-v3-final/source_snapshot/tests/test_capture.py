import json
import sys

import pytest

from examples.recovery import run
from heartness.capture import prepare
from heartness.cli import main
from heartness.monitor import observation_summary
from heartness.properties import violations
from heartness.simulator import example


def test_recovery_and_capture_boundary():
    engine, report = run()
    assert engine.state.active == {"m3", "s2", "a3"}
    assert engine.state.artifacts["s2"].sources == ("m3",)
    assert "m1" in engine.state.withdrawn
    assert "s1" in engine.state.quarantined
    assert not violations(engine)
    exposure = prepare(engine, ("m3",), ("untracked ambient input",))
    assert exposure.untracked_inputs
    with pytest.raises(KeyError):
        prepare(engine, ("unknown",))


def test_observation_coverage():
    from heartness.model import Event
    assert observation_summary([])["status"] == "event admissibility only"
    assert observation_summary([Event("unknown", {})])["missing_observations"] == 1
    _, events = example()
    assert observation_summary(events)["status"] == "all events observed"
    assert observation_summary(events+[Event("unknown", {})])["status"] == "partial state observations"


def test_cli_saved_withdrawal(tmp_path, monkeypatch, capsys):
    path = tmp_path / "withdrawn.json"
    monkeypatch.setattr(sys, "argv", ["heartness", "withdraw", "--save-events", str(path)])
    main()
    capsys.readouterr()
    monkeypatch.setattr(sys, "argv", ["heartness", "rollback-plan", "--version", "5", "--events", str(path)])
    main()
    assert not json.loads(capsys.readouterr().out)["admissible"]
