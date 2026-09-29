"""Write SHAP plots and the summary JSON for the pinned churn model."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from governance.paths import SHAP_JSON_PATH
from governance.shap_report import write_shap_report


def main() -> None:
    report = write_shap_report()
    print(f"Wrote {SHAP_JSON_PATH}")
    print(f"max reconstruction error {report['max_abs_reconstruction_error']:.6f}")
    for row in report["local_customers"]:
        print(row["customer_id"], row["selection_reason"], f"{row['churn_probability']:.6f}")


if __name__ == "__main__":
    main()
