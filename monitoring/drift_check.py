"""Check question-length drift between two windows."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from sre.psi import calculate_psi, read_values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("current", type=Path)
    parser.add_argument("--buckets", type=int, default=10)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = calculate_psi(read_values(args.reference), read_values(args.current), args.buckets)
    print(f"PSI = {result.score:.4f} -> {result.verdict.upper()}")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
    return 1 if result.verdict == "alert" else 0


if __name__ == "__main__":
    sys.exit(main())
