import json
import sys

import pytest

from heartness.cli import main
from heartness.simulator import example


@pytest.mark.parametrize("command", ["trace", "impact", "withdraw", "check", "rollback-plan",
                                     "monitor", "example", "export-model"])
def test_cli(command, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["heartness", command, "--depth", "3"])
    main()
    out = capsys.readouterr().out
    if command == "export-model":
        assert "init" in out
    else:
        assert isinstance(json.loads(out), dict)


def test_cli_event_file(tmp_path, monkeypatch, capsys):
    from dataclasses import asdict
    _, events = example()
    path = tmp_path / "events.json"
    path.write_text(json.dumps([asdict(e) for e in events]))
    monkeypatch.setattr(sys, "argv", ["heartness", "withdraw", "--dry-run", "--events", str(path)])
    main()
    assert "affected_active" in capsys.readouterr().out
