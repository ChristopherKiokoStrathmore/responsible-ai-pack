"""Fairlearn group metrics on the held-out split.

Hard labels are the saved pipeline's predict() output: class 1 only when
P(Churn=Yes) is strictly greater than 0.5. ROC-AUC uses the probabilities.
"""

from __future__ import annotations

import numpy as np
from fairlearn.metrics import (
    MetricFrame,
    demographic_parity_difference,
    equalized_odds_difference,
    false_positive_rate,
    selection_rate,
    true_positive_rate,
)
from sklearn.metrics import roc_auc_score

from governance.holdout import Holdout, load_holdout
from governance.paths import FAIRNESS_PATH
from governance.serialize import dumps_rounded

HARD_LABEL_RULE = (
    "Positive when the saved pipeline's predict() returns class 1, "
    "which is when P(Churn=Yes) > 0.5. An exact tie stays class 0."
)
SENSITIVE_FIELDS = ("gender", "SeniorCitizen")


def _roc_auc(y_true, y_score) -> float:
    if len(np.unique(y_true)) < 2:
        return float("nan")
    return float(roc_auc_score(y_true, y_score))


def _group_table(y_true, y_pred, y_score, sensitive: np.ndarray) -> dict:
    frame = MetricFrame(
        metrics={
            "selection_rate": selection_rate,
            "true_positive_rate": true_positive_rate,
            "false_positive_rate": false_positive_rate,
        },
        y_true=y_true,
        y_pred=y_pred,
        sensitive_features=sensitive,
    )
    auc_frame = MetricFrame(
        metrics={"roc_auc": _roc_auc},
        y_true=y_true,
        y_pred=y_score,
        sensitive_features=sensitive,
    )
    groups = {}
    for key in frame.by_group.index:
        mask = sensitive == key
        label = str(key)
        groups[label] = {
            "n": int(mask.sum()),
            "n_positive": int(y_true[mask].sum()),
            "positive_rate": float(y_true[mask].mean()),
            "selection_rate": float(frame.by_group.loc[key, "selection_rate"]),
            "true_positive_rate": float(frame.by_group.loc[key, "true_positive_rate"]),
            "false_positive_rate": float(frame.by_group.loc[key, "false_positive_rate"]),
            "roc_auc": float(auc_frame.by_group.loc[key, "roc_auc"]),
        }
    return {
        "groups": groups,
        "demographic_parity_difference": float(
            demographic_parity_difference(y_true, y_pred, sensitive_features=sensitive)
        ),
        "equalized_odds_difference": float(
            equalized_odds_difference(y_true, y_pred, sensitive_features=sensitive)
        ),
    }


def build_fairness_report(holdout: Holdout | None = None) -> dict:
    holdout = holdout or load_holdout()
    y_pred = holdout.scoring_model.predict(holdout.features)
    fields = {}
    for column in SENSITIVE_FIELDS:
        sensitive = holdout.test[column].astype(str).to_numpy()
        fields[column] = _group_table(holdout.labels, y_pred, holdout.proba, sensitive)
    return {
        "scoring_model": "gradient_boosting",
        "split": "telco_nba.pipeline.split_customers seed 42 test_size 0.25 stratify Churn",
        "n_test": int(len(holdout.test)),
        "hard_label_rule": HARD_LABEL_RULE,
        "roc_auc_input": "P(Churn=Yes) from predict_proba, not the hard label",
        "demographic_parity_difference": (
            "Absolute difference between the largest and smallest group selection rates, "
            "as returned by fairlearn.metrics.demographic_parity_difference."
        ),
        "equalized_odds_difference": (
            "The larger of the absolute true-positive-rate gap and the absolute "
            "false-positive-rate gap across groups, as returned by "
            "fairlearn.metrics.equalized_odds_difference."
        ),
        "fields_are_model_inputs": {
            "gender": True,
            "SeniorCitizen": True,
        },
        "attributes_not_in_the_table": (
            "The IBM CSV has no race, ethnicity, region, language, or disability column. "
            "This check does not cover them."
        ),
        "by_field": fields,
        "overall": {
            "n": int(len(holdout.labels)),
            "n_positive": int(holdout.labels.sum()),
            "positive_rate": float(holdout.labels.mean()),
            "selection_rate": float(np.mean(y_pred == 1)),
        },
    }


def write_fairness_report(path=None) -> dict:
    report = build_fairness_report()
    destination = path or FAIRNESS_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(dumps_rounded(report))
    return report
