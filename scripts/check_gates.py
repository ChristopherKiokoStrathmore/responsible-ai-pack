"""Recompute held-out metrics and exit 1 if any metric is below its gate."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from governance.gates import format_gate_check, write_gate_check
from governance.paths import GATE_CHECK_PATH


def main() -> None:
    result = write_gate_check()
    print(format_gate_check(result))
    print(f"Wrote {GATE_CHECK_PATH}")
    if not result["passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
