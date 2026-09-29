"""Write the Fairlearn group-metric report."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from governance.fairness import write_fairness_report
from governance.paths import FAIRNESS_PATH


def main() -> None:
    write_fairness_report()
    print(f"Wrote {FAIRNESS_PATH}")


if __name__ == "__main__":
    main()
