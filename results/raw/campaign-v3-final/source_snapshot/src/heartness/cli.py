"""JSON CLI for recorded trace queries and conservative remediation plans."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from heartness.checker import bfs, promela
from heartness.engine import Engine
from heartness.model import Event, canonical
from heartness.monitor import monitor, observation_summary
from heartness.properties import violations
from heartness.simulator import example


def main() -> None:
    parser = argparse.ArgumentParser(prog="heartness")
    parser.add_argument("command", choices=("trace", "impact", "withdraw", "check", "rollback-plan",
                                            "monitor", "export-model", "example"))
    parser.add_argument("--events", type=Path)
    parser.add_argument("--artifact", default="m1")
    parser.add_argument("--version", type=int, default=0)
    parser.add_argument("--scope", type=int, default=3)
    parser.add_argument("--depth", type=int, default=7)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--save-events", type=Path,
                        help="Save resulting event history to a fresh JSON file for later commands")
    args = parser.parse_args()
    if args.events:
        events = [Event(**e) for e in json.loads(args.events.read_text())]
        engine = Engine()
        if args.command != "monitor":
            for event in events:
                engine.apply(event)
    else:
        engine, events = example()
    if args.command == "export-model":
        print(promela(args.scope, args.depth))
        return
    result: dict[str, Any]
    if args.command == "trace":
        result = {"origins": sorted(engine.graph.origins(args.artifact)),
                  "descendants": sorted(engine.graph.descendants(args.artifact)),
                  "first_installation": engine.culprit_revision(args.artifact)}
    elif args.command in {"withdraw", "impact"}:
        result = engine.withdrawal_plan(args.artifact)
        if args.command == "withdraw" and not args.dry_run:
            withdrawal = Event("Withdraw", {"id": args.artifact})
            observed = engine.apply(withdrawal)
            events.append(Event(withdrawal.op, withdrawal.args, observed))
            result["active_after"] = sorted(engine.state.active)
    elif args.command == "rollback-plan":
        result = engine.rollback_plan(args.version)
    elif args.command == "monitor":
        result = {"deviations": [asdict(d) for d in monitor(events)],
                  "observation_coverage": observation_summary(events)}
    elif args.command == "check":
        result = {"runtime": violations(engine), "projection": bfs(args.scope, args.depth)}
    else:
        result = {"events": [asdict(e) for e in events], "state": engine.state.semantic()}
    if args.save_events:
        with args.save_events.open("x") as stream:
            stream.write(canonical([asdict(event) for event in events]) + "\n")
        result["events_saved"] = str(args.save_events)
    print(canonical(result))
