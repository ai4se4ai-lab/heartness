import json
from pathlib import Path

from benchmark.generate import Config, FAMILIES, generate
from heartness.baselines import query
from heartness.model import Artifact, canonical


def test_hand_oracle_cases():
    data = json.loads(Path("benchmark/hand_cases.json").read_text())
    artifacts = [Artifact.from_dict(a) for a in data["artifacts"]]
    for case in data["cases"]:
        observed = query(artifacts, case["root"], case["target"], data["active"], data["deployments"])
        assert observed == {key: case[key] for key in observed}


def test_meaningful_generator_factors():
    by_family = [generate(Config(family=f, seed=5))["artifacts"] for f in FAMILIES]
    assert len({canonical(a) for a in by_family}) == len(FAMILIES)
    low = generate(Config(fanout=1, seed=5))
    high = generate(Config(fanout=6, seed=5))
    assert low["realized"]["max_sources"] < high["realized"]["max_sources"]
    assert high["realized"]["dependency_only_edges"] > 0
    one = generate(Config(deployments=1, seed=5))
    many = generate(Config(deployments=4, seed=5))
    assert len(one["truth"]["deployment_impact"]) < len(many["truth"]["deployment_impact"])
    assert many["realized"]["deployment_only"]


def test_motif_minima_are_explicit_exceptions():
    for family in ("synthesis", "adversarial"):
        scenario = generate(Config(family=family, fanout=1, depth=0, artifacts=16))
        assert scenario["realized"]["max_sources"] == 2
        assert scenario["realized"]["max_depth"] == 2
