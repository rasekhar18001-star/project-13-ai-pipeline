"""Privacy-minimal JSONL telemetry."""

from __future__ import annotations

import json
from pathlib import Path


def write_event(path: Path, *, question_length: int, retrieved_chunk_count: int, model_id: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {"question_length": question_length, "retrieved_chunk_count": retrieved_chunk_count, "model_id": model_id}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
