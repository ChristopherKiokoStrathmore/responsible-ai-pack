"""Write PSI between the training split and the held-out split."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from governance.drift import write_drift_report
from governance.paths import DRIFT_PATH


def main() -> None:
    report = write_drift_report()
    print(f"Wrote {DRIFT_PATH}")
    for feature in report["features"]:
        print(f"{feature['name']} psi {feature['psi']:.6f} above_trigger {feature['above_trigger']}")


if __name__ == "__main__":
    main()
