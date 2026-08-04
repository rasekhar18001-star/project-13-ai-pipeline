"""One-command rollback to the recorded prior champion."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rollback_state(state: dict[str, object]) -> dict[str, object]:
    if "previous_champion" not in state:
        raise ValueError("no previous champion is recorded; rollback is not required")
    return {"champion": state["previous_champion"], "challenger": state["champion"]}


def main() -> int:
    state_path = ROOT / "deploy/current.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    try:
        updated = rollback_state(state)
    except ValueError as exc:
        print(f"REFUSED: {exc}")
        return 1
    state_path.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
    with (ROOT / "deploy/history.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps({"timestamp": datetime.now(UTC).isoformat(), "action": "rollback", "state": updated})
            + "\n"
        )
    print("Rollback complete: recorded champion restored.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
