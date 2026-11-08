"""Declared approximations to history and lexical recovery; no external tools claimed."""

from __future__ import annotations

import random
import re
from dataclasses import replace

from heartness.graph import Graph
from heartness.model import Artifact


def capture(artifacts: list[Artifact], fraction: float, seed: int) -> list[Artifact]:
    rng = random.Random(seed + 8912)
    return [replace(a, sources=tuple(s for s in a.sources if rng.random() < fraction))
            for a in artifacts]


def file_history(artifacts: list[Artifact]) -> list[Artifact]:
    """B0: within-path revisions only, intentionally excludes Git copy detection."""
    previous: dict[str, str] = {}
    result = []
    for a in artifacts:
        sources = (previous[a.path],) if a.path in previous else ()
        result.append(replace(a, sources=sources, dependencies=()))
        previous[a.path] = a.id
    return result


def similarity(artifacts: list[Artifact], threshold: float = .2) -> list[Artifact]:
    """B1: chronological token Jaccard at a protocol-fixed threshold."""
    tokens = [set(re.findall(r"[a-z]+", a.text.lower())) for a in artifacts]
    recovered = []
    for i, a in enumerate(artifacts):
        sources = tuple(artifacts[j].id for j in range(i)
                        if len(tokens[i] & tokens[j]) / max(1, len(tokens[i] | tokens[j])) >= threshold)
        recovered.append(replace(a, sources=sources, dependencies=()))
    return recovered


def query(artifacts: list[Artifact], root: str, target: str, active: list[str],
          deployments: dict[str, list[str]] | None = None) -> dict[str, list[str]]:
    graph = Graph({a.id: a for a in artifacts})
    result = {"descendants": sorted(graph.descendants(root)), "origins": sorted(graph.origins(target)),
              "impact": sorted(graph.impact(root, active))}
    if deployments is not None:
        result["deployment_impact"] = sorted(d+":"+a for d, members in deployments.items()
                                             for a in graph.impact(root, members))
    return result


def linter(artifacts: list[Artifact], active: set[str], withdrawn: set[str]) -> set[str]:
    """B3: direct-edge checks; no transitive propagation or prospective search."""
    return {a.id for a in artifacts if a.id in active and
            (a.id in withdrawn or bool(set(a.sources + a.dependencies) & withdrawn))}
