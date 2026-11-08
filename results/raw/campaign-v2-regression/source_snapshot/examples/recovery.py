"""Single-history containment, rejected rollback, independent correction and redeploy."""
from dataclasses import asdict

from heartness import Artifact, Contract, Event, Rejected
from heartness.capture import prepare, propose
from heartness.model import canonical
from heartness.simulator import example, install


def run():
    e, events = example()
    summary = {"before": sorted(e.state.active)}
    e.apply(Event("Withdraw", {"id": "m1"}))
    summary["contained"] = sorted(e.state.active)
    try:
        e.apply(Event("Rollback", {"version": 5}))
    except Rejected as exc:
        summary["unsafe_rollback"] = str(exc)
    e.apply(Event("Rollback", {"version": 0}))
    summary["restored_local"] = sorted(e.state.active)
    summary["deployments_after_local_rollback"] = e.state.deployments.copy()
    # New host-observed feedback, not generation from the withdrawn text.
    e.apply(Event("Experience", {"id": "e2", "task": "independent schema validation test",
                                "run": "r2", "outcome": "validation detects malformed patch"}))
    install(e, Artifact("m3", "memory", "validate schema before applying a patch",
                        experiences=("e2",), contract=Contract(provides=("checked",))))
    exposure = prepare(e, ("m3",))
    proposal = propose(e, exposure, "s2", lambda texts: "new procedure: " + texts[0])
    e.apply(Event("Validate", {"id": proposal.args["id"], "passed": True}))
    e.apply(Event("Accept", {"id": proposal.args["id"]}))
    install(e, Artifact("a3", "agent", "new configuration", dependencies=("s2",),
                        authorized_seed=True))
    for d in ("d1", "d2"):
        e.apply(Event("Deploy", {"deployment": d}))
    summary["recovered"] = sorted(e.state.active)
    summary["old_quarantine_retained"] = sorted(e.state.quarantined)
    summary["new_exposure"] = asdict(exposure)
    summary["effects_not_reversed"] = [asdict(effect) for effect in e.state.effects]
    return e, summary


if __name__ == "__main__":
    print(canonical(run()[1]))
