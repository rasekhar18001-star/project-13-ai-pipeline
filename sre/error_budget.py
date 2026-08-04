"""Quality SLO error-budget calculator adapted from the starter."""

from __future__ import annotations

import argparse
import sys
from dataclasses import asdict, dataclass

from app.config import load_reliability


@dataclass(frozen=True)
class ErrorBudgetResult:
    slo: float
    total: int
    bad: int
    allowed_bad: float
    remaining: float
    burn_ratio: float
    sli: float
    verdict: str


def calculate(slo: float, total: int, bad: int, high_burn: float = 0.75) -> ErrorBudgetResult:
    if not 0 < slo <= 1:
        raise ValueError("SLO must satisfy 0 < SLO <= 1")
    if total < 0 or bad < 0:
        raise ValueError("total and bad must be nonnegative")
    if bad > total:
        raise ValueError("bad must not exceed total")
    allowed = (1 - slo) * total
    remaining = allowed - bad
    burn = bad / allowed if allowed else (0.0 if bad == 0 else float("inf"))
    sli = 1 - bad / total if total else 1.0
    verdict = "exhausted" if remaining < 0 else "high-burn" if burn >= high_burn else "healthy"
    return ErrorBudgetResult(slo, total, bad, allowed, remaining, burn, sli, verdict)


def render(result: ErrorBudgetResult) -> str:
    return (
        f"SLO target: {result.slo:.3%}\nMeasured SLI: {result.sli:.3%}\n"
        f"Allowed bad: {result.allowed_bad:.2f}\n"
        f"Spent: {result.bad}\n"
        f"Remaining: {result.remaining:.2f}\n"
        f"VERDICT: {result.verdict.upper()}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slo", type=float, default=load_reliability()["quality_slo"])
    parser.add_argument("--total", type=int, required=True)
    parser.add_argument("--bad", type=int, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = calculate(args.slo, args.total, args.bad)
    except ValueError as exc:
        parser.error(str(exc))
    if args.json:
        import json

        print(json.dumps(asdict(result)))
    else:
        print(render(result))
    return {"healthy": 0, "high-burn": 2, "exhausted": 3}[result.verdict]


if __name__ == "__main__":
    sys.exit(main())
