"""Run the same quality gates used by CI."""

import subprocess
import sys

COMMANDS = (
    (sys.executable, "-m", "ruff", "format", "--check", "."),
    (sys.executable, "-m", "ruff", "check", "."),
    (sys.executable, "-m", "mypy"),
    (sys.executable, "-m", "pyright"),
    (sys.executable, "-m", "pytest"),
)


def main() -> None:
    for command in COMMANDS:
        print(f"+ {' '.join(command)}", flush=True)
        result = subprocess.run(command, check=False)
        if result.returncode:
            raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
