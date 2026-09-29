"""Recompute the committed reports from the pinned model."""

import inspect
import json

import pytest

from governance.drift import build_drift_report, population_stability_index
from governance.fairness import build_fairness_report
from governance.gates import (
    build_gate_check,
    evaluate_gates,
    floor_to_decimals,
    load_gates,
    scoring_metrics,
)
from governance.holdout import build_metrics_report
from governance.paths import (
    DRIFT_PATH,
    FAIRNESS_PATH,
    GATE_CHECK_PATH,
    GATES_PATH,
    METRICS_PATH,
    SHAP_DIR,
    SHAP_JSON_PATH,
)
from governance.serialize import dumps_rounded
from governance.shap_report import build_shap_report


def test_split_uses_the_upstream_function(holdout):
    import telco_nba.pipeline as pipeline

    source = inspect.getsource(pipeline.split_customers)
    assert "train_test_split" in source
    assert "stratify" in source
    assert pipeline.SEED == 42
    assert pipeline.TEST_SIZE == 0.25
    report = json.loads(METRICS_PATH.read_text())
    assert report["split"]["n_train"] == 5282
    assert report["split"]["n_test"] == 1761
    assert report["split"]["example_customer_id"] == "5343-SGUBI"
    assert holdout.test.loc[holdout.test["TotalCharges"].notna(), "customerID"].iloc[0] == "5343-SGUBI"
    assert len(holdout.train) == 5282
    assert len(holdout.test) == 1761


def test_metrics_report_matches_committed_file(holdout):
    fresh = dumps_rounded(build_metrics_report(holdout))
    assert fresh == METRICS_PATH.read_text()
    report = json.loads(fresh)
    assert report["matches_upstream_metrics_at_six_decimals"] is True


def test_fairness_report_matches_committed_file(holdout):
    fresh = dumps_rounded(build_fairness_report(holdout))
    assert fresh == FAIRNESS_PATH.read_text()


def test_shap_report_matches_committed_file(holdout):
    fresh = dumps_rounded(build_shap_report(holdout, write_plots=False))
    assert fresh == SHAP_JSON_PATH.read_text()


def test_shap_plots_are_pngs():
    report = json.loads(SHAP_JSON_PATH.read_text())
    names = ["global_summary.png", "global_bar.png"]
    names.extend(row["plot"].rsplit("/", 1)[-1] for row in report["local_customers"])
    assert len(report["local_customers"]) == 3
    for name in names:
        blob = (SHAP_DIR / name).read_bytes()
        assert blob.startswith(b"\x89PNG")
        assert len(blob) > 10000


def test_drift_report_matches_committed_file(holdout):
    fresh = dumps_rounded(build_drift_report(holdout))
    assert fresh == DRIFT_PATH.read_text()
    report = json.loads(fresh)
    assert report["n_above_trigger"] == 0


def test_psi_is_zero_on_identical_counts_and_rises_when_mass_moves():
    assert population_stability_index([40, 60], [40, 60]) == pytest.approx(0.0, abs=1e-12)
    shifted = population_stability_index([40, 60], [90, 10])
    assert shifted > 0.25


def test_gates_match_the_documented_margin(holdout):
    document = load_gates(GATES_PATH)
    values = scoring_metrics(build_metrics_report(holdout))
    decimals = int(document["round_down_decimals"])
    for name, margin in document["margins"].items():
        expected = floor_to_decimals(values[name] - float(margin), decimals)
        assert float(document["gates"][name]) == expected


def test_gate_check_matches_committed_file(holdout):
    fresh = dumps_rounded(build_gate_check())
    assert fresh == GATE_CHECK_PATH.read_text()
    assert json.loads(fresh)["passed"] is True


def test_a_drop_below_the_floor_fails():
    document = load_gates()
    values = {"roc_auc": 0.5, "pr_auc": 0.9, "top_decile_lift": 3.0}
    result = evaluate_gates(values, document)
    assert result["passed"] is False
    assert result["failures"] == ["roc_auc"]
