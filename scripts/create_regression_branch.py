"""Create a reversible regression-demo branch without touching main."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=check)


def main() -> None:
    if git("status", "--porcelain").stdout.strip():
        raise SystemExit("Refusing: working tree is dirty.")
    if git("branch", "--show-current").stdout.strip() != "main":
        raise SystemExit("Refusing: current branch must be main.")
    if git("show-ref", "--verify", "--quiet", "refs/heads/regression-demo", check=False).returncode == 0:
        raise SystemExit("Refusing: regression-demo already exists.")
    git("switch", "-c", "regression-demo")
    path = ROOT / "app/rag.py"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("regression: bool = False", "regression: bool = True"), encoding="utf-8")
    identity = (
        git("config", "user.email", check=False).stdout.strip()
        and git("config", "user.name", check=False).stdout.strip()
    )
    if identity:
        git("add", "app/rag.py")
        git("commit", "-m", "demo: enable deliberate unsupported claim")
    else:
        print("Git identity is not configured; change was not committed.")
    print("Push with: git push -u origin regression-demo")
    print("Return with: git switch main")


if __name__ == "__main__":
    main()
