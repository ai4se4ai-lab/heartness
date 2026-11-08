from experiments.run import property_challenge
from heartness.properties import PROPERTY_IDS


def test_targeted_properties():
    for prop in PROPERTY_IDS:
        full = property_challenge(prop, False)
        removed = property_challenge(prop, True)
        if full["intervention"] == "guard":
            if prop not in {"P2", "P8"}:
                assert full["rejected"], (prop, full)
            assert not removed["rejected"], (prop, removed)
            assert removed["target_alarm"], (prop, removed)
        else:
            assert full["target_alarm"], (prop, full)
            assert not removed["target_alarm"], (prop, removed)
