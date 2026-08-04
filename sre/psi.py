"""PSI detects feature/data drift, not concept drift."""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PSIResult:
    score: float
    verdict: str
    buckets_used: int


def calculate_psi(
    reference: list[float], current: list[float], buckets: int = 10, moderate: float = 0.10, alert: float = 0.20
) -> PSIResult:
    if not reference or not current:
        raise ValueError("reference and current inputs must not be empty")
    if buckets < 2:
        raise ValueError("buckets must be at least 2")
    if not all(math.isfinite(x) for x in reference + current):
        raise ValueError("inputs must contain only finite numbers")
    ref = sorted(reference)
    cuts = sorted(set(ref[min(len(ref) - 1, int(len(ref) * q / buckets))] for q in range(1, buckets)))
    edges = [-math.inf, *cuts, math.inf]

    def fractions(values: list[float]) -> list[float]:
        counts = [0] * (len(edges) - 1)
        for value in values:
            for index in range(len(counts)):
                if edges[index] < value <= edges[index + 1]:
                    counts[index] += 1
                    break
        raw = [max(count / len(values), 1e-6) for count in counts]
        scale = sum(raw)
        return [value / scale for value in raw]

    rfrac, cfrac = fractions(reference), fractions(current)
    score = sum((cur - ref_) * math.log(cur / ref_) for ref_, cur in zip(rfrac, cfrac, strict=False))
    verdict = "calm" if score < moderate else "moderate" if score < alert else "alert"
    return PSIResult(score, verdict, len(edges) - 1)


def read_values(path: Path) -> list[float]:
    try:
        return [float(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except ValueError as exc:
        raise ValueError(f"{path} contains a nonnumeric value") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="PSI detects feature/data drift, not concept drift.")
    parser.add_argument("reference", type=Path)
    parser.add_argument("current", type=Path)
    parser.add_argument("--buckets", type=int, default=10)
    args = parser.parse_args()
    result = calculate_psi(read_values(args.reference), read_values(args.current), args.buckets)
    print(f"PSI = {result.score:.4f} -> {result.verdict.upper()} ({result.buckets_used} buckets)")


if __name__ == "__main__":
    main()
