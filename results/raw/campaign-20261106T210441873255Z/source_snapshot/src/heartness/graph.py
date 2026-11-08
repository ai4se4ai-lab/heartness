"""Recorded provenance queries. Absent links never become invented evidence."""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterable, Mapping

from heartness.model import Artifact


class Graph:
    def __init__(self, artifacts: Mapping[str, Artifact]) -> None:
        self.artifacts = artifacts
        self.children: dict[str, set[str]] = defaultdict(set)
        self.consumers: dict[str, set[str]] = defaultdict(set)
        for item in artifacts.values():
            for source in item.sources:
                self.children[source].add(item.id)
            for producer in item.dependencies:
                self.consumers[producer].add(item.id)

    def closure(self, sources: Iterable[str], *, dependencies: bool = False) -> set[str]:
        """Least fixed point; optional consumers can themselves have derivatives."""
        seen = set(sources)
        todo = deque(sorted(seen))
        while todo:
            node = todo.popleft()
            next_nodes = self.children.get(node, set())
            if dependencies:
                next_nodes = next_nodes | self.consumers.get(node, set())
            for child in sorted(next_nodes - seen):
                seen.add(child)
                todo.append(child)
        return seen

    def descendants(self, source: str) -> set[str]:
        return self.closure([source]) - {source}

    def origins(self, target: str) -> set[str]:
        """Return recorded experience IDs and explicit seed anchors."""
        result: set[str] = set()
        todo = [target]
        seen: set[str] = set()
        while todo:
            node = todo.pop()
            if node in seen:
                continue
            seen.add(node)
            item = self.artifacts[node]
            result.update(item.experiences)
            if item.authorized_seed:
                result.add("seed:" + node)
            todo.extend(item.sources)
        return result

    def impact(self, source: str, active: Iterable[str]) -> set[str]:
        return self.closure([source], dependencies=True) & set(active)

    def acyclic(self) -> bool:
        """Kahn check also rejects unknown source endpoints."""
        degree = {key: len(set(a.sources)) for key, a in self.artifacts.items()}
        if any(source not in degree for a in self.artifacts.values() for source in a.sources):
            return False
        todo = deque(key for key, count in degree.items() if count == 0)
        removed = 0
        while todo:
            key = todo.popleft()
            removed += 1
            for child in self.children.get(key, set()):
                degree[child] -= 1
                if degree[child] == 0:
                    todo.append(child)
        return removed == len(degree)
