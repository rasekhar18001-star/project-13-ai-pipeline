import pytest

from app.config import load_settings, validate_model_id


def test_defaults_are_pinned():
    settings = load_settings({})
    assert settings.rag_model_id == "gpt-oss:120b-cloud"
    assert "latest" not in settings.judge_model_id


def test_latest_rejected():
    with pytest.raises(ValueError, match="latest"):
        validate_model_id("model-latest")


def test_invalid_top_k():
    with pytest.raises(ValueError):
        load_settings({"RAG_TOP_K": "0"})
