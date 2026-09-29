"""Regenerate every committed report from the pinned model."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from governance.drift import write_drift_report
from governance.fairness import write_fairness_report
from governance.gates import write_gate_check
from governance.holdout import write_metrics_report
from governance.shap_report import write_shap_report
from governance.upstream import ensure_upstream


def main() -> None:
    ensure_upstream()
    write_metrics_report()
    write_fairness_report()
    write_shap_report()
    write_drift_report()
    result = write_gate_check()
    if not result["passed"]:
        sys.exit(1)
    print("Wrote reports.")


if __name__ == "__main__":
    main()
