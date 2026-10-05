"""Write web/data/holdout_scores.json from the pinned churn model.

Run after scripts/fetch_upstream.py. The committed JSON is what the demo loads.
tests/test_demo_scores.py checks it against reports/fairness.json.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from governance.demo_scores import (
    assert_matches_published_fairness,
    build_score_table,
    write_score_table,
)
from governance.holdout import load_holdout
from governance.paths import FAIRNESS_PATH, ROOT


def main() -> None:
    destination = ROOT / "web" / "data" / "holdout_scores.json"
    table = build_score_table(load_holdout())
    fairness = json.loads(FAIRNESS_PATH.read_text())
    assert_matches_published_fairness(table, fairness)
    write_score_table(table, destination)
    print(f"wrote {destination} ({table['n']} rows)")


if __name__ == "__main__":
    main()
