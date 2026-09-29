"""Recompute held-out metrics for the saved churn models."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from governance.holdout import write_metrics_report
from governance.paths import METRICS_PATH


def main() -> None:
    report = write_metrics_report()
    print(f"Wrote {METRICS_PATH}")
    print(f"matches upstream at six decimals: {report['matches_upstream_metrics_at_six_decimals']}")


if __name__ == "__main__":
    main()
