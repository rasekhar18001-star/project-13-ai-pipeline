"""Cross-platform local deterministic check runner."""

import subprocess
import sys


def main() -> None:
    for command in (
        [sys.executable, "-m", "ruff", "check", "."],
        [sys.executable, "-m", "pytest", "tests/unit", "-q"],
        [sys.executable, "-m", "compileall", "-q", "app", "evals", "sre", "monitoring", "rollout", "scripts"],
    ):
        subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
