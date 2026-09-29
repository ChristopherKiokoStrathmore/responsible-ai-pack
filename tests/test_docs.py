"""Numbers in the write-up must appear in a report or a pinned source file."""

import json
import re
from pathlib import Path

from governance.docs import ACT_NAME, PERSONAL_FRAMEWORK
from governance.paths import LOCK_PATH, REPORTS, ROOT
from governance.upstream import ensure_upstream, load_lock

DOCS = (
    "README.md",
    "MODEL_CARD.md",
    "MODEL_CARD_MULTIHEAD.md",
    "GOVERNANCE_CHECKLIST.md",
    "MONITORING.md",
    "INCIDENT_RUNBOOK.md",
)
# The year is part of the Act's name. It is not a measured result.
ALLOWED_EXTRA = {"2019"}


def _corpus() -> str:
    roots = ensure_upstream()
    parts = []
    for path in REPORTS.rglob("*.json"):
        parts.append(path.read_text())
    for relative in (
        "gates.yaml",
        "upstream.lock.json",
        "requirements.txt",
        ".github/workflows/ci.yml",
    ):
        parts.append((ROOT / relative).read_text())
    lock = load_lock(LOCK_PATH)
    parts.append((roots["telco"] / "reports" / "metrics.json").read_text())
    for relative in lock["multihead"]["files"]:
        parts.append((roots["multihead"] / relative).read_text())
    return "\n".join(parts)


def _numbers(text: str) -> list[str]:
    flattened = re.sub(r"(?<=\d),(?=\d)", "", text)
    return re.findall(r"\d+(?:\.\d+)?", flattened)


def test_writeup_numbers_come_from_source_files():
    allowed = _corpus()
    missing = {}
    for name in DOCS:
        found = sorted(
            {
                number
                for number in _numbers((ROOT / name).read_text())
                if number not in allowed and number not in ALLOWED_EXTRA
            }
        )
        if found:
            missing[name] = found
    assert missing == {}


def test_personal_framework_is_stated():
    for name in DOCS:
        assert PERSONAL_FRAMEWORK in (ROOT / name).read_text()


def test_churn_card_has_the_required_sections():
    text = (ROOT / "MODEL_CARD.md").read_text()
    for heading in (
        "Intended use",
        "Out-of-scope use",
        "Data",
        "Metrics",
        "Limitations",
        "Human review",
    ):
        assert f"## {heading}" in text


def test_multihead_card_marks_gaps_and_links_sources():
    text = (ROOT / "MODEL_CARD_MULTIHEAD.md").read_text()
    assert "not documented in source repo" in text
    assert "809bccd61077898849c428f37521fa198f7c7bf6" in text
    assert "eval/gates.smoke.json" in text
    assert "lib/trust.ts" in text
    for heading in (
        "Intended use",
        "Out-of-scope use",
        "Data",
        "Metrics",
        "Limitations",
        "Human review",
    ):
        assert f"## {heading}" in text


def test_governance_checklist_names_the_act_and_the_four_functions():
    text = (ROOT / "GOVERNANCE_CHECKLIST.md").read_text()
    assert ACT_NAME in text
    for name in ("Govern", "Map", "Measure", "Manage"):
        assert f"## {name}" in text
    assert re.search(r"section\s+\d+", text, flags=re.IGNORECASE) is None


def test_readme_quotes_the_recomputed_scoring_metrics():
    report = json.loads((REPORTS / "metrics_recomputed.json").read_text())
    fairness = json.loads((REPORTS / "fairness.json").read_text())
    readme = (ROOT / "README.md").read_text()
    block = report["churn_models"]["gradient_boosting"]
    for key in ("roc_auc", "pr_auc", "top_decile_lift"):
        assert f"{block[key]:.6f}" in readme
    for field in ("gender", "SeniorCitizen"):
        groups = fairness["by_field"][field]
        assert f"{groups['demographic_parity_difference']:.6f}" in readme
        assert f"{groups['equalized_odds_difference']:.6f}" in readme
        for group in groups["groups"].values():
            for key in (
                "selection_rate",
                "true_positive_rate",
                "false_positive_rate",
                "roc_auc",
            ):
                assert f"{group[key]:.6f}" in readme


def test_upstream_lock_points_at_the_churn_commit():
    lock = json.loads(Path(LOCK_PATH).read_text())
    assert lock["telco"]["commit"] == "21f6115931f4358ebc7cc87d9ba1f4d87fd015aa"
