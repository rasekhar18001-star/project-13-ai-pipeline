from pathlib import Path

from app.config import Settings
from app.rag import ABSTENTION, SYSTEM_PROMPT, RAGService
from app.retrieval import Document, LexicalRetriever


class FakeLLM:
    def complete(self, **kwargs):
        return "Use Forgot password."


def settings():
    return Settings("http://local/v1", "fake", "pinned-model", "pinned-judge", 1)


def test_grounded_generation_uses_fake():
    docs = [Document("password_reset", "Use Forgot password.", Path("fake"))]
    result = RAGService(settings(), LexicalRetriever(docs), FakeLLM()).answer("password reset")
    assert result["answer"] == "Use Forgot password."
    assert "guarantees resolution within five minutes" not in result["answer"]
    assert result["retrieved_document_ids"] == ["password_reset"]


def test_abstention_when_retrieval_empty():
    docs = [Document("policy", "unrelated content", Path("fake"))]
    result = RAGService(settings(), LexicalRetriever(docs), FakeLLM()).answer("xyzzy")
    assert result["answer"] == ABSTENTION
    assert result["answer"] == "I cannot answer that from the provided policy context."


def test_deliberate_regression_adds_unsupported_claim():
    docs = [Document("password_reset", "Use Forgot password.", Path("fake"))]
    result = RAGService(settings(), LexicalRetriever(docs), FakeLLM()).answer("password reset", regression=True)
    assert "guarantees resolution within five minutes" in result["answer"]
    assert "five minutes" not in result["retrieved_context"]


def test_deliberate_regression_environment_flag(monkeypatch):
    docs = [Document("password_reset", "Use Forgot password.", Path("fake"))]
    monkeypatch.setenv("DELIBERATE_REGRESSION", "1")
    result = RAGService(settings(), LexicalRetriever(docs), FakeLLM()).answer("password reset")
    assert result["answer"].endswith("The help desk guarantees resolution within five minutes.")
    assert "five minutes" not in result["retrieved_context"]


def test_temporal_claim_must_be_explicitly_supported():
    class TemporalAnswerLLM:
        def complete(self, **kwargs):
            return "Email-based attendance instructions from before 2026 are no longer current; use the family portal."

    result = RAGService(settings(), llm=TemporalAnswerLLM()).answer(
        "Should I use last year's attendance email process?"
    )
    assert result["retrieved_document_ids"][0] == "attendance"
    assert "no longer current" in result["answer"]
    assert "Email-based attendance instructions from before 2026 are no longer current" in result["retrieved_context"]
    assert "Do not infer that an older method was discontinued unless the context explicitly says so" in SYSTEM_PROMPT
