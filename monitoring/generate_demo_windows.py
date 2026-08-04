"""Deterministically regenerate the sample question-length windows."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
REFERENCE = [20, 22, 24, 25, 27, 29, 30, 32, 34, 36] * 10
CALM = [20, 22, 24, 25, 27, 29, 30, 32, 34, 36] * 10
ALERT = [70, 72, 75, 78, 80, 82, 85, 88, 90, 95] * 10


def main() -> None:
    for name, values in {
        "reference_question_length.txt": REFERENCE,
        "current_calm.txt": CALM,
        "current_alert.txt": ALERT,
    }.items():
        (ROOT / name).write_text("\n".join(map(str, values)) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
