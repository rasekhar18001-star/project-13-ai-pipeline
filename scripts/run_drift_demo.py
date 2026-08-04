"""Generate sample windows and save genuine calm and alert PSI results."""

import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from monitoring.generate_demo_windows import main as generate  # noqa: E402
from sre.psi import calculate_psi, read_values  # noqa: E402


def main() -> None:
    generate()
    base = ROOT / "monitoring"
    reference = read_values(base / "reference_question_length.txt")
    results = {
        "calm": calculate_psi(reference, read_values(base / "current_calm.txt")),
        "alert": calculate_psi(reference, read_values(base / "current_alert.txt")),
    }
    for name, result in results.items():
        print(f"{name}: PSI={result.score:.4f} -> {result.verdict}")
    (ROOT / "artifacts").mkdir(exist_ok=True)
    (ROOT / "artifacts/drift_demo.json").write_text(
        json.dumps({k: asdict(v) for k, v in results.items()}, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
