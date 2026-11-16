"""Verification script: runs ruff, pytest, build_readme --offline --check, and check_links --offline.

Halts immediately on the first failure.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run_step(name: str, cmd: list[str]) -> None:
    """Execute a verification command, halting on non-zero exit code."""
    print(f"\n[VERIFY STEP] === {name} ===")
    print(f"Command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT), check=False)
    if result.returncode != 0:
        print(f"\n[VERIFY FAILED] Step '{name}' failed with exit code {result.returncode}.", file=sys.stderr)
        sys.exit(result.returncode)
    print(f"[VERIFY PASSED] {name}")


def main() -> None:
    py = sys.executable

    # 1. Ruff linting
    run_step("Ruff Lint", [py, "-m", "ruff", "check", "."])

    # 2. Pytest suite
    run_step("Pytest Suite", [py, "-m", "pytest", "tests"])

    # 3. Build README check
    run_step(
        "Build README (--offline --check)",
        [py, "scripts/build_readme.py", "--offline", "--check"],
    )

    # 4. Link check (offline)
    run_step("Link Check (--offline)", [py, "scripts/check_links.py", "--offline"])

    print("\n" + "=" * 50)
    print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
