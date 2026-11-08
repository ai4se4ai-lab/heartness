"""Generator oracle uses carried labels, never the approach's graph functions."""

from __future__ import annotations

import random
from dataclasses import asdict, dataclass
from typing import Any

from heartness.model import Artifact, Contract

FAMILIES = ("faulty_lesson", "edited_source", "synthesis", "regression", "cross_deployment",
            "stale_dependency", "external_effect", "benign", "adversarial")


@dataclass(frozen=True)
class Config:
    family: str = "faulty_lesson"
    artifacts: int = 64
    fanout: int = 3
    deployments: int = 2
    paraphrase: float = .5
    capture: float = 1.0
    synthesis: float = .4
    depth: int = 12
    noise: float = .1
    edit_frequency: float = .1
    withdrawal_frequency: float = .1
    seed: int = 0


def generate(config: Config) -> dict[str, Any]:
    """Artifact identities are revisions. Truth is inherited at construction time."""
    if config.family not in FAMILIES or config.artifacts < 2:
        raise ValueError("unknown family or too few artifacts")
    if not 0 <= config.capture <= 1 or config.fanout < 1 or config.deployments < 1:
        raise ValueError("invalid generator parameter")
    rng = random.Random(config.seed)
    artifacts: list[Artifact] = []
    ancestry: list[int] = []
    influence: list[int] = []
    origins: list[set[str]] = []
    levels: list[int] = []
    vocab = ("retry network timeout", "validate result schema", "retain task context",
             "check filesystem permission", "compile before testing", "inspect stale cache")
    for i in range(config.artifacts):
        root = i < 2 or rng.random() < config.noise
        eligible = [j for j in range(i) if levels[j] < config.depth]
        sources: list[int] = []
        if not root and eligible:
            multi = rng.random() < config.synthesis or config.family == "synthesis"
            count = min(len(eligible), rng.randint(2, max(2, config.fanout)) if multi else 1,
                        config.fanout)
            sources = sorted(rng.sample(eligible, count))
        dependencies: list[int] = []
        if i > 1 and rng.random() < .35:
            dependencies = [rng.randrange(i)]
        # Enact different structural motifs, rather than changing only family labels.
        if i == 2:
            sources = {"faulty_lesson": [0], "edited_source": [0], "synthesis": [0, 1],
                       "regression": [1], "cross_deployment": [], "stale_dependency": [],
                       "external_effect": [0], "benign": [1], "adversarial": [0, 1]}[config.family]
            dependencies = [0] if config.family in {"cross_deployment", "stale_dependency"} else []
        elif i == 3:
            sources = [] if config.family in {"faulty_lesson", "stale_dependency", "cross_deployment"} else [2]
            dependencies = [2] if config.family != "benign" else []
        elif i == 4 and config.family == "faulty_lesson":
            sources, dependencies = [3], []
        inherited = 0
        affected = 0
        exposure: set[str] = set()
        for j in sources:
            inherited |= ancestry[j] | (1 << j)
            exposure.update(origins[j])
        for j in set(sources + dependencies):
            affected |= influence[j] | (1 << j)
        if not sources:
            exposure.add("e" + str(i))
        if sources and rng.random() >= config.paraphrase:
            text = artifacts[sources[0]].text + " procedure"
        else:
            # Deliberately controlled lexical decoupling, not an LLM paraphrase claim.
            text = rng.choice(vocab) + " " + format(rng.getrandbits(48), "x")
        if i == 2:
            text += " " + config.family
        if config.family == "edited_source" and i > 1 and sources:
            path = artifacts[sources[0]].path
        else:
            path = "harness/" + str(i) + ".txt"
        kind = ("memory", "skill", "prompt", "workflow", "tool", "agent", "executable")[i % 7]
        item = Artifact("a" + str(i), kind, text, tuple("a" + str(j) for j in sources),
                        tuple("a" + str(j) for j in dependencies),
                        ("e" + str(i),) if not sources else (), False,
                        "merge" if len(sources) > 1 else "transform",
                        Contract(("cap",) if dependencies else (), ("cap",)), path)
        artifacts.append(item)
        ancestry.append(inherited)
        influence.append(affected)
        origins.append(exposure)
        levels.append(1 + max((levels[j] for j in sources), default=-1))
    # Active subsets model superseded revisions; dependencies are closed downward.
    active = {i for i in range(config.artifacts) if rng.random() >= config.edit_frequency}
    def close_dependencies(indices):
        todo = list(indices)
        while todo:
            for dep in artifacts[todo.pop()].dependencies:
                idx = int(dep[1:])
                if idx not in indices:
                    indices.add(idx)
                    todo.append(idx)
        return indices
    active = close_dependencies(active)
    deploy = {"d0": sorted("a" + str(i) for i in active)}
    for d in range(1, config.deployments):
        membership = close_dependencies({i for i in range(config.artifacts) if (i+d) % 3 != 0})
        deploy["d" + str(d)] = sorted("a" + str(i) for i in membership)
    root = 2 if config.family == "regression" else 0
    target = config.artifacts - 1
    truth = {
        "descendants": ["a" + str(i) for i in range(config.artifacts) if ancestry[i] & (1 << root)],
        "impact": sorted("a" + str(i) for i in active
                         if i == root or influence[i] & (1 << root)),
        "deployment_impact": sorted(d + ":" + aid for d, members in deploy.items()
                                    for aid in members if int(aid[1:]) == root or
                                    influence[int(aid[1:])] & (1 << root)),
        "origins": sorted(origins[target]),
        "root": "a" + str(root), "target": "a" + str(target),
        "fault": config.family != "benign",
        "culprit_revision": root + 1 if config.family == "regression" else None,
        "external_effects": ["sent-message"] if config.family == "external_effect" else [],
        "challenge": {
            "faulty_lesson": "withdraw source and contain its derivatives",
            "edited_source": "retain old source identity after file edit",
            "synthesis": "trace sources despite controlled lexical decoupling",
            "regression": "locate first installation (not establish causation)",
            "cross_deployment": "suspend affected copies in multiple deployments",
            "stale_dependency": "reject replacement removing required capability",
            "external_effect": "restore snapshot without claiming message reversal",
            "benign": "admit clean evolution without invariant alarms",
            "adversarial": "reject cycles, stale bases and validated-content drift",
        }[config.family],
    }
    return {"benchmark": "EvoTraceBench-1.1", "config": asdict(config),
            "artifacts": [asdict(a) for a in artifacts], "active": sorted("a" + str(i) for i in active),
            "deployments": deploy, "truth": truth,
            "realized": {"source_edges": sum(len(a.sources) for a in artifacts),
                         "dependency_only_edges": sum(len(set(a.dependencies)-set(a.sources)) for a in artifacts),
                         "max_sources": max(len(a.sources) for a in artifacts),
                         "max_depth": max(levels),
                         "deployment_memberships": sum(len(m) for m in deploy.values()),
                         "deployment_only": sorted({a for m in deploy.values() for a in m} -
                                                   {"a" + str(i) for i in active})}}
