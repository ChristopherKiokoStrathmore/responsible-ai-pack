"""The interactive demo's holdout rows must reproduce the committed fairness report."""

import json

from governance.demo_scores import PUBLISHED_CUTOFF, assert_matches_published_fairness
from governance.paths import FAIRNESS_PATH, METRICS_PATH, ROOT

SCORES_PATH = ROOT / "web" / "data" / "holdout_scores.json"
DEMO_URL = "https://responsible-ai-pack.vercel.app/demo"


def test_holdout_scores_match_fairness_at_the_published_cutoff():
    table = json.loads(SCORES_PATH.read_text())
    fairness = json.loads(FAIRNESS_PATH.read_text())
    metrics = json.loads(METRICS_PATH.read_text())
    assert table["published_cutoff"] == PUBLISHED_CUTOFF
    assert table["n"] == fairness["overall"]["n"]
    assert table["scoring_model"] == fairness["scoring_model"]
    assert table["upstream_commit"] == metrics["upstream_commit"]
    assert table["test_customer_id_sha256"] == metrics["split"]["test_customer_id_sha256"]
    assert_matches_published_fairness(table, fairness, PUBLISHED_CUTOFF)


def test_readme_points_at_the_interactive_demo():
    readme = (ROOT / "README.md").read_text()
    assert DEMO_URL in readme
    assert "placeholder" not in readme.split("## Live demo", 1)[1].split("##", 1)[0].lower()
