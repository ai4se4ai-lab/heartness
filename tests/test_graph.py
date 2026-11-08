from dataclasses import replace

from benchmark.generate import Config, FAMILIES, generate
from heartness.baselines import capture, file_history, linter, query, similarity
from heartness.graph import Graph
from heartness.model import Artifact, canonical


def test_hand_computed_closures():
    a = Artifact("m", "memory", "lesson", experiences=("e",))
    b = Artifact("s", "skill", "procedure", sources=("m",))
    c = Artifact("a", "agent", "consumer", dependencies=("s",), authorized_seed=True)
    g = Graph({x.id: x for x in (a, b, c)})
    assert g.descendants("m") == {"s"}
    assert g.impact("m", {"m", "s", "a"}) == {"m", "s", "a"}
    assert g.origins("s") == {"e"}
    assert g.origins("a") == {"seed:a"}
    assert g.acyclic()
    assert not Graph({"s": b}).acyclic()
    assert not Graph({"m": replace(a, sources=("m",))}).acyclic()
    assert linter([a, b, c], {"m", "s", "a"}, {"m"}) == {"m", "s"}


def test_benchmark_truth_and_determinism():
    for family in FAMILIES:
        for seed in range(10):
            cfg = Config(family=family, seed=seed, artifacts=32)
            scenario = generate(cfg)
            assert canonical(scenario) == canonical(generate(cfg))
            artifacts = [Artifact.from_dict(a) for a in scenario["artifacts"]]
            truth = scenario["truth"]
            result = query(artifacts, truth["root"], truth["target"], scenario["active"])
            assert all(result[key] == sorted(truth[key]) for key in result)
            assert query(capture(artifacts, 1, seed), truth["root"], truth["target"],
                         scenario["active"]) == result
            assert all(not a.sources for a in capture(artifacts, 0, seed))
            assert len(file_history(artifacts)) == len(artifacts)
            assert len(similarity(artifacts)) == len(artifacts)


def test_generator_rejects():
    import pytest
    for cfg in (Config(family="absent"), Config(artifacts=1), Config(capture=-1), Config(fanout=0)):
        with pytest.raises(ValueError):
            generate(cfg)
