"""Absolute controller/capture cost; no claim to matched production overhead."""
from dataclasses import asdict

from benchmark.generate import Config, generate
from heartness import Artifact, Engine, Event
from heartness.baselines import capture
from heartness.model import canonical
from heartness.monitor import monitor
from heartness.simulator import install


def campaign(writer, measure):
    for size in (4, 8, 16, 32):
        for seed in range(30):
            scenario = generate(Config(artifacts=size, seed=seed))
            items = [Artifact.from_dict(a) for a in scenario["artifacts"]]
            _, capture_cost = measure(lambda: canonical([asdict(a) for a in capture(items, 1, seed)]))
            e, events = Engine(), []
            def admission():
                for a in items:
                    for experience in a.experiences:
                        event = Event("Experience", {"id": experience, "task": "synthetic feedback",
                                    "run": "r-" + experience, "outcome": "propose persistent revision"})
                        events.append(Event(event.op, event.args, e.apply(event)))
                    events.extend(install(e, a))
                for d in range(2):
                    event = Event("Deploy", {"deployment": "d" + str(d)})
                    events.append(Event(event.op, event.args, e.apply(event)))
            _, admission_cost = measure(admission)
            _, monitor_cost = measure(lambda: monitor(events))
            root = scenario["truth"]["root"]
            withdrawal = Event("Withdraw", {"id": root})
            _, withdrawal_cost = measure(lambda: e.apply(withdrawal))
            writer.record("E13_runtime_cost", {"artifacts": size, "deployments": 2}, seed,
                          {"scenario": scenario, "events": [asdict(event) for event in events],
                           "capture_cost": capture_cost, "admission_cost": admission_cost,
                           "monitor_cost": monitor_cost, "withdrawal_cost": withdrawal_cost,
                           "final_hash": e.state.hash, "history_events": len(e.state.history),
                           "capture_bytes": len(canonical([asdict(a) for a in items]).encode()),
                           "timing_scope": "capture serialization; all guarded events; replay; withdrawal",
                           "cost_interpretation": "absolute CPU/allocation cost, not production overhead"})
