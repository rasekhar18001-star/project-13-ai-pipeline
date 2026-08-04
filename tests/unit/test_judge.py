
import pytest

from app.rag import ABSTENTION
from evals.judge import judge_answer, parse_verdict, run_evaluation


class SequenceClient:
    def __init__(self, values):
        self.values = iter(values)
        self.calls = 0

    def complete(self, **kwargs):
        self.calls += 1
        return next(self.values)


def test_plain_and_fenced_json():
    assert parse_verdict(' {"grounded": true, "reason": "supported"} ')["grounded"]
    assert not parse_verdict('```json\n{"grounded": false, "reason": "invented"}\n```')["grounded"]


def test_retry_after_malformed():
    client = SequenceClient(["bad", '{"grounded": true, "reason": "ok"}'])
    assert judge_answer(client, "judge-v1", "ctx", "answer")["grounded"]
    assert client.calls == 2


def test_persistent_malformed_fails():
    with pytest.raises(ValueError, match="malformed"):
        judge_answer(SequenceClient(["bad", "bad", "bad"]), "judge-v1", "ctx", "answer")


class FakeRAG:
    def answer(self, question):
        return {"answer": question, "retrieved_context": "context"}


def test_threshold_rate_can_fail():
    client = SequenceClient(['{"grounded": true, "reason": "ok"}', '{"grounded": false, "reason": "fabricated"}'])
    rate, results = run_evaluation(
        [{"id": "a", "question": "a"}, {"id": "b", "question": "b"}], FakeRAG(), client, "judge-v1"
    )
    assert rate == 0.5
    assert rate < 0.9
    assert not results[1].grounded


class AbstentionRuleClient:
    def complete(self, **kwargs):
        assert "GROUNDED ABSTENTION EXAMPLE" in kwargs["messages"][0]["content"]
        assert "UNGROUNDED ABSTENTION EXAMPLE" in kwargs["messages"][0]["content"]
        answer = kwargs["messages"][1]["content"].split("ANSWER:\n", 1)[1]
        grounded = answer == "I cannot answer that from the provided policy context."
        return '{"grounded": ' + str(grounded).lower() + ', "reason": "rubric applied"}'


def test_valid_pure_abstention_passes():
    verdict = judge_answer(AbstentionRuleClient(), "judge-v1", "Account access requires a ticket.", ABSTENTION)
    assert verdict["grounded"] is True


@pytest.mark.parametrize(
    "answer",
    [
        "I cannot answer from the context, but school lunch is pizza on Friday.",
        "School lunch is pizza on Friday.",
    ],
)
def test_invented_policy_claims_fail_even_with_or_without_abstention(answer):
    verdict = judge_answer(AbstentionRuleClient(), "judge-v1", "Account access requires a ticket.", answer)
    assert verdict["grounded"] is False
