"""Load the pinned churn model and the seed-42 stratified split.

The split function is telco_nba.pipeline.split_customers from the pinned commit.
This module does not fit a new model.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from governance.paths import METRICS_PATH
from governance.serialize import dumps_rounded
from governance.upstream import ensure_upstream, load_lock


@dataclass
class Holdout:
    telco_root: str
    train: pd.DataFrame
    test: pd.DataFrame
    scoring_model: Pipeline
    schema: dict
    churn_models: dict[str, Pipeline]
    features: pd.DataFrame
    labels: np.ndarray
    proba: np.ndarray


def load_holdout() -> Holdout:
    roots = ensure_upstream()
    from telco_nba.data import TARGET_COLUMN, binary_label, load_telco
    from telco_nba.model_io import load_bundle, load_churn_model
    from telco_nba.pipeline import feature_frame, positive_proba, split_customers

    telco = roots["telco"]
    frame = load_telco(telco / "data" / "Telco-Customer-Churn.csv")
    train, test = split_customers(frame)
    model, schema = load_churn_model(
        telco / "artifacts" / "churn_model.joblib",
        telco / "artifacts" / "feature_schema.json",
    )
    bundle = load_bundle(telco / "artifacts" / "scoring_bundle.joblib")
    features = feature_frame(test)
    labels = binary_label(test[TARGET_COLUMN]).to_numpy()
    proba = positive_proba(model, features)
    return Holdout(
        telco_root=str(telco),
        train=train,
        test=test,
        scoring_model=model,
        schema=schema,
        churn_models=bundle["churn_models"],
        features=features,
        labels=labels,
        proba=proba,
    )


def test_customer_id_sha256(test: pd.DataFrame) -> str:
    payload = "\n".join(test["customerID"].astype(str)).encode()
    return hashlib.sha256(payload).hexdigest()


def example_customer(test: pd.DataFrame) -> pd.Series:
    """Same row the churn repo uses as its API example."""
    return test.loc[test["TotalCharges"].notna()].iloc[0]


def _metric_strings(block: dict) -> dict[str, str]:
    keys = (
        "roc_auc",
        "pr_auc",
        "top_decile_lift",
        "top_decile_positive_rate",
        "base_rate",
    )
    return {key: f"{float(block[key]):.6f}" for key in keys}


def build_metrics_report(holdout: Holdout | None = None) -> dict:
    holdout = holdout or load_holdout()
    from telco_nba.data import TARGET_COLUMN
    from telco_nba.metrics import classification_metrics
    from telco_nba.pipeline import SCORING_MODEL, SEED, TEST_SIZE, feature_frame, positive_proba
    lock = load_lock()["telco"]
    upstream = json.loads(upstream_metrics_path(holdout).read_text())
    scored = {}
    for name, pipeline in holdout.churn_models.items():
        scores = positive_proba(pipeline, feature_frame(holdout.test))
        scored[name] = classification_metrics(holdout.labels, scores)
    comparisons = {}
    match = True
    for name, block in scored.items():
        got = _metric_strings(block)
        expected = _metric_strings(upstream["churn"]["models"][name])
        comparisons[name] = {"recomputed": got, "upstream": expected, "equal": got == expected}
        match = match and got == expected
    example = example_customer(holdout.test)
    train_rate = float((holdout.train[TARGET_COLUMN] == "Yes").mean())
    test_rate = float((holdout.test[TARGET_COLUMN] == "Yes").mean())
    return {
        "upstream_repository": lock["repository"],
        "upstream_commit": lock["commit"],
        "upstream_metrics_file": "reports/metrics.json",
        "upstream_metrics_sha256": lock["files"]["reports/metrics.json"],
        "scoring_model_file": "artifacts/churn_model.joblib",
        "scoring_model_sha256": lock["files"]["artifacts/churn_model.joblib"],
        "split_function": "telco_nba.pipeline.split_customers",
        "split": {
            "seed": SEED,
            "test_size": TEST_SIZE,
            "stratify": TARGET_COLUMN,
            "n_train": int(len(holdout.train)),
            "n_test": int(len(holdout.test)),
            "train_churn_rate": train_rate,
            "test_churn_rate": test_rate,
            "train_churn_yes": int((holdout.train[TARGET_COLUMN] == "Yes").sum()),
            "test_churn_yes": int((holdout.test[TARGET_COLUMN] == "Yes").sum()),
            "example_customer_id": str(example["customerID"]),
            "example_customer_historical_churn": str(example[TARGET_COLUMN]),
            "example_customer_rule": "first held-out row whose TotalCharges is numeric",
            "test_customer_id_sha256": test_customer_id_sha256(holdout.test),
        },
        "scoring_model": SCORING_MODEL,
        "positive_label": "Yes",
        "label_column_excluded_from_features": True,
        "feature_order": list(holdout.schema["feature_order"]),
        "inputs_include_gender": "gender" in holdout.schema["feature_order"],
        "inputs_include_SeniorCitizen": "SeniorCitizen" in holdout.schema["feature_order"],
        "churn_models": scored,
        "upstream_comparison": comparisons,
        "matches_upstream_metrics_at_six_decimals": match,
        "dataset_fields_source": "copied from upstream reports/metrics.json dataset",
        "dataset_sha256": upstream["dataset"]["sha256"],
        "dataset_n_rows": upstream["dataset"]["n_rows"],
        "dataset_churn_rate": upstream["dataset"]["churn_rate"],
    }


def upstream_metrics_path(holdout: Holdout) -> Path:
    return Path(holdout.telco_root) / "reports" / "metrics.json"


def write_metrics_report(path=None) -> dict:
    report = build_metrics_report()
    destination = path or METRICS_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(dumps_rounded(report))
    return report
