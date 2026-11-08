"""Exhaustive small reference-state mapping, not a refinement proof."""
from collections import deque
from copy import deepcopy
from dataclasses import asdict

from heartness import Artifact, Engine, Event, Rejected
from heartness.checker import SmallState, actions, initial, masks, step


def translated_event(engine, action, n, topology):
    op, i = action
    aid, pid = "a" + str(i), "p" + str(i)
    if op == "propose":
        parent_mask = masks(n, topology)[0][i]
        parents = tuple("a" + str(j) for j in range(n) if parent_mask & (1 << j))
        artifact = Artifact(aid, "skill", "projected content", sources=parents,
                            dependencies=parents, authorized_seed=not parents)
        return Event("Propose", {"id": pid, "artifact": asdict(artifact)})
    if op == "validate":
        return Event("Validate", {"id": pid, "passed": True})
    if op == "accept":
        return Event("Accept", {"id": pid})
    if op == "withdraw":
        return Event("Withdraw", {"id": aid})
    if op == "deploy":
        return Event("Deploy", {"deployment": "d"})
    return Event("Rollback", {"version": i})


def mapped(engine, n):
    s = engine.state
    def bits(ids):
        return sum(1 << i for i in range(n) if "a" + str(i) in ids)
    proposed = sum(1 << i for i in range(n) if "p" + str(i) in s.proposals)
    validated = sum(1 << i for i in range(n) if "p" + str(i) in s.validations
                    and s.validations["p" + str(i)].passed)
    bases = tuple(s.proposals["p" + str(i)].base if "p" + str(i) in s.proposals else -1
                  for i in range(n))
    return SmallState(proposed, validated, bits(s.artifacts), bits(s.active), bits(s.withdrawn),
                      bits(s.deployments.get("d", ())), len(s.versions)-1, bases,
                      tuple(bits(v.active) for v in s.versions))


def compare_reference(n=2, depth=6, topology="chain"):
    queue = deque([(initial(n), Engine(), 0)])
    seen = {initial(n)}
    transitions, enabled, stutters = 0, 0, 0
    mismatches = []
    while queue:
        state, engine, level = queue.popleft()
        if level == depth:
            continue
        for action in actions(n):
            transitions += 1
            expected = step(state, action, n, topology=topology)
            actual_engine = deepcopy(engine)
            try:
                actual_engine.apply(translated_event(actual_engine, action, n, topology))
                actual = mapped(actual_engine, n)
            except Rejected:
                actual = None
            # Overwriting identical validation/deployment records is projection stuttering.
            if expected is None and actual == state:
                stutters += 1
                continue
            if actual != expected:
                mismatches.append({"state": asdict(state), "action": action,
                                   "expected": asdict(expected) if expected else None,
                                   "actual": asdict(actual) if actual else None})
            if expected is not None:
                enabled += 1
                if expected not in seen and actual == expected:
                    seen.add(expected)
                    queue.append((expected, actual_engine, level+1))
    return {"n": n, "depth": depth, "topology": topology, "states": len(seen),
            "attempted_transitions": transitions, "enabled_transitions": enabled,
            "projection_stutters": stutters, "mismatches": mismatches,
            "scope": "all successors of discovered reference states; one shortest history per state"}
