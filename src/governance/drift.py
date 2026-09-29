"""Population stability index between the training split and the held-out split.

The two slices are one stratified draw, not two dates. The function is what a
later batch would call, with the training split kept as the reference.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from governance.holdout import Holdout, load_holdout
from governance.paths import DRIFT_PATH
from governance.serialize import dumps_rounded

PSI_REVIEW_TRIGGER = 0.25
CLIP_FLOOR = 1e-6
NUMERIC_BINS = 10
NUMERIC_FEATURES = ("tenure", "MonthlyCharges", "TotalCharges")
CATEGORICAL_FEATURES = (
    "Contract",
    "InternetService",
    "PaymentMethod",
    "gender",
    "SeniorCitizen",
)


def population_stability_index(reference_counts, current_counts, clip_floor: float = CLIP_FLOOR) -> float:
    """PSI from two count vectors. Shares below clip_floor are raised, then re-normalized."""
    reference = np.asarray(reference_counts, dtype=float)
    current = np.asarray(current_counts, dtype=float)
    if reference.shape != current.shape or reference.ndim != 1 or reference.size == 0:
        raise ValueError("counts must be non-empty 1-d arrays of the same length")
    if np.any(reference < 0) or np.any(current < 0):
        raise ValueError("counts must be non-negative")
    if reference.sum() <= 0 or current.sum() <= 0:
        raise ValueError("counts must have a positive total")
    reference = reference / reference.sum()
    current = current / current.sum()
    reference = np.clip(reference, clip_floor, None)
    current = np.clip(current, clip_floor, None)
    reference = reference / reference.sum()
    current = current / current.sum()
    return float(np.sum((current - reference) * np.log(current / reference)))


def _numeric_counts(reference: pd.Series, current: pd.Series, n_bins: int):
    ref = pd.to_numeric(reference, errors="coerce").to_numpy(dtype=float)
    cur = pd.to_numeric(current, errors="coerce").to_numpy(dtype=float)
    observed = ref[np.isfinite(ref)]
    if observed.size == 0:
        raise ValueError("reference column has no numeric values")
    edges = np.unique(np.quantile(observed, np.linspace(0.0, 1.0, n_bins + 1)))
    if edges.size < 2:
        edges = np.array([observed[0], observed[0] + 1.0])

    def pack(values: np.ndarray):
        missing = ~np.isfinite(values)
        kept = values[~missing]
        histogram, _ = np.histogram(kept, bins=edges)
        counts = histogram.astype(int).tolist() + [int(missing.sum())]
        return counts

    return edges, pack(ref), pack(cur)


def _categorical_counts(reference: pd.Series, current: pd.Series):
    ref = reference.astype(str)
    cur = current.astype(str)
    levels = sorted(set(ref.unique()) | set(cur.unique()))
    ref_counts = ref.value_counts().reindex(levels, fill_value=0)
    cur_counts = cur.value_counts().reindex(levels, fill_value=0)
    return levels, [int(value) for value in ref_counts.to_numpy()], [int(value) for value in cur_counts.to_numpy()]


def build_drift_report(holdout: Holdout | None = None) -> dict:
    holdout = holdout or load_holdout()
    features = []
    for name in NUMERIC_FEATURES:
        edges, ref_counts, cur_counts = _numeric_counts(
            holdout.train[name], holdout.test[name], NUMERIC_BINS
        )
        psi = population_stability_index(ref_counts, cur_counts)
        features.append(
            {
                "name": name,
                "kind": "numeric",
                "edges": [float(edge) for edge in edges],
                "missing_bin": "last count is non-finite values, including blank TotalCharges",
                "reference_counts": ref_counts,
                "current_counts": cur_counts,
                "psi": psi,
                "above_trigger": bool(psi >= PSI_REVIEW_TRIGGER),
            }
        )
    for name in CATEGORICAL_FEATURES:
        levels, ref_counts, cur_counts = _categorical_counts(holdout.train[name], holdout.test[name])
        psi = population_stability_index(ref_counts, cur_counts)
        features.append(
            {
                "name": name,
                "kind": "categorical",
                "levels": levels,
                "reference_counts": ref_counts,
                "current_counts": cur_counts,
                "psi": psi,
                "above_trigger": bool(psi >= PSI_REVIEW_TRIGGER),
            }
        )
    return {
        "reference": "training rows from telco_nba.pipeline.split_customers",
        "current": "held-out rows from the same split",
        "comparison_note": (
            "The two slices are a stratified random split of one public table, not two time periods. "
            "A small PSI here checks the function. A production monitor would keep this training split "
            "as the reference and pass a later batch as the current sample."
        ),
        "psi_review_trigger": PSI_REVIEW_TRIGGER,
        "clip_floor": CLIP_FLOOR,
        "requested_numeric_bins": NUMERIC_BINS,
        "n_train": int(len(holdout.train)),
        "n_test": int(len(holdout.test)),
        "n_above_trigger": int(sum(feature["above_trigger"] for feature in features)),
        "features": features,
    }


def write_drift_report(path=None) -> dict:
    report = build_drift_report()
    destination = path or DRIFT_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(dumps_rounded(report))
    return report
