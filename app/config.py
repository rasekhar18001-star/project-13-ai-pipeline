"""Validated configuration loading with pinned model defaults."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate_model_id(model_id: str) -> str:
    if not model_id.strip():
        raise ValueError("model ID must not be empty")
    if "latest" in model_id.casefold():
        raise ValueError("model ID must be pinned and must not contain 'latest'")
    return model_id


@dataclass(frozen=True)
class Settings:
    base_url: str
    api_key: str
    rag_model_id: str
    judge_model_id: str
    top_k: int = 3
    telemetry_path: Path | None = None


def load_settings(environ: dict[str, str] | None = None) -> Settings:
    env = os.environ if environ is None else environ
    data = tomllib.loads((ROOT / "config/models.toml").read_text(encoding="utf-8"))["local"]
    top_k = int(env.get("RAG_TOP_K", "3"))
    if top_k < 1:
        raise ValueError("RAG_TOP_K must be at least 1")
    telemetry = env.get("TELEMETRY_PATH")
    return Settings(
        base_url=env.get("OPENAI_BASE_URL", data["base_url"]),
        api_key=env.get("OPENAI_API_KEY", "ollama"),
        rag_model_id=validate_model_id(env.get("RAG_MODEL_ID", data["rag_model_id"])),
        judge_model_id=validate_model_id(env.get("JUDGE_MODEL_ID", data["judge_model_id"])),
        top_k=top_k,
        telemetry_path=Path(telemetry) if telemetry else None,
    )


def load_reliability() -> dict[str, float]:
    return tomllib.loads((ROOT / "config/reliability.toml").read_text(encoding="utf-8"))["reliability"]
