import json

from app.telemetry import write_event


def test_telemetry_has_no_question_or_answer(tmp_path):
    path = tmp_path / "events.jsonl"
    write_event(path, question_length=12, retrieved_chunk_count=2, model_id="model-v1")
    event = json.loads(path.read_text())
    assert set(event) == {"question_length", "retrieved_chunk_count", "model_id"}
