"""Run and save genuine error-budget examples."""

import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sre.error_budget import calculate  # noqa: E402


def main() -> None:
    results = {
        "healthy": calculate(0.99, 1000, 2),
        "high_burn": calculate(0.99, 1000, 8),
        "exhausted": calculate(0.99, 1000, 12),
    }
    for name, result in results.items():
        print(f"{name}: {result.verdict} (burn={result.burn_ratio:.2f})")
    (ROOT / "artifacts").mkdir(exist_ok=True)
    (ROOT / "artifacts/error_budget_demo.json").write_text(
        json.dumps({k: asdict(v) for k, v in results.items()}, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
