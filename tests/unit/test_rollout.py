import pytest

from rollout.promote import can_promote, promote
from rollout.rollback import rollback_state
from rollout.shadow import compare

STATE = {"champion": {"name": "champion"}, "challenger": {"name": "challenger"}}


def metrics(champion=0.9, challenger=0.95, cases=8):
    return {
        "champion": {"groundedness": champion, "completed_cases": cases},
        "challenger": {"groundedness": challenger, "completed_cases": cases},
    }


def test_promotion_rules():
    assert can_promote(metrics(), 0.9, 8)[0]
    assert not can_promote(metrics(challenger=0.8), 0.9, 8)[0]
    assert not can_promote(metrics(champion=1.0, challenger=0.95), 0.9, 8)[0]
    assert not can_promote(metrics(cases=7), 0.9, 8)[0]


def test_promote_then_rollback():
    promoted, _ = promote(STATE, metrics(), 0.9, 8)
    assert promoted["champion"]["name"] == "challenger"
    assert rollback_state(promoted)["champion"]["name"] == "champion"


def test_rollback_without_record_refuses():
    with pytest.raises(ValueError):
        rollback_state(STATE)


def test_shadow_never_serves_challenger():
    result = compare(lambda cfg: {"groundedness": 1.0, "completed_cases": 8}, STATE["champion"], STATE["challenger"])
    assert result["served_configuration"] == "champion"
    assert result["challenger_served"] is False
