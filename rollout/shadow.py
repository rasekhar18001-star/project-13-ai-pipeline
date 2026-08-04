"""Replay cases to champion and challenger without serving challenger output."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def compare(
    evaluator: Callable[[dict[str, object]], dict[str, object]],
    champion: dict[str, object],
    challenger: dict[str, object],
) -> dict[str, object]:
    return {
        "champion": evaluator(champion),
        "challenger": evaluator(challenger),
        "served_configuration": champion["name"],
        "challenger_served": False,
    }


def main() -> None:
    state = json.loads((ROOT / "deploy/current.json").read_text(encoding="utf-8"))
    print(
        json.dumps(
            {
                "status": "cloud evaluation required",
                "champion": state["champion"],
                "challenger": state["challenger"],
                "challenger_served": False,
            },
            indent=2,
        )
    )
    print("Run the configured cloud evaluation before promotion; no challenger answer was served.")


if __name__ == "__main__":
    main()
