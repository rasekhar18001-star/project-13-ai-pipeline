"""Metric-driven challenger promotion."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from app.config import load_reliability

ROOT = Path(__file__).resolve().parents[1]


def can_promote(metrics: dict[str, object], threshold: float, minimum_cases: int) -> tuple[bool, str]:
    champion = metrics.get("champion", {})
    challenger = metrics.get("challenger", {})
    if not isinstance(champion, dict) or not isinstance(challenger, dict):
        return False, "evaluation is incomplete"
    if champion.get("completed_cases", 0) < minimum_cases or challenger.get("completed_cases", 0) < minimum_cases:
        return False, "evaluation is incomplete"
    challenger_rate = float(challenger.get("groundedness", -1))
    champion_rate = float(champion.get("groundedness", -1))
    if challenger_rate < threshold:
        return False, "challenger is below the groundedness threshold"
    if challenger_rate < champion_rate:
        return False, "challenger is worse than champion"
    return True, "promotion criteria met"


def promote(
    state: dict[str, object], metrics: dict[str, object], threshold: float, minimum_cases: int
) -> tuple[dict[str, object], str]:
    allowed, reason = can_promote(metrics, threshold, minimum_cases)
    if not allowed:
        return state, reason
    return {
        "champion": state["challenger"],
        "challenger": state["champion"],
        "previous_champion": state["champion"],
    }, reason


def main() -> int:
    metrics_path = ROOT / "artifacts/shadow-results.json"
    if not metrics_path.exists():
        print("REFUSED: artifacts/shadow-results.json is missing; run a complete shadow evaluation first.")
        return 1
    state_path = ROOT / "deploy/current.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    updated, reason = promote(state, metrics, load_reliability()["eval_groundedness_threshold"], 8)
    if updated is state:
        print(f"REFUSED: {reason}")
        return 1
    state_path.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
    with (ROOT / "deploy/history.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps({"timestamp": datetime.now(UTC).isoformat(), "action": "promote", "state": updated})
            + "\n"
        )
    print("Promoted challenger based on complete metrics.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
