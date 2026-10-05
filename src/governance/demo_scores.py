"""Held-out scores for the interactive demo.

The web demo recomputes selection rate, true positive rate, false positive rate,
demographic parity difference, and equalized odds difference at a cutoff the
visitor moves. At the published cutoff those figures must match
reports/fairness.json. This module does not train a model and does not add a
fairness floor.
"""

from __future__ import annotations

import json
from pathlib import Path

PUBLISHED_CUTOFF = 0.5
GENDER_KEYS = ("Female", "Male")
SENIOR_KEYS = ("0", "1")


def six(value: float) -> str:
    return f"{float(value):.6f}"


def _rates(indexes: list[int], label: list[int], selected: list[bool]) -> dict[str, float | int]:
    n = len(indexes)
    if n == 0:
        raise ValueError("group is empty")
    n_positive = sum(1 for i in indexes if label[i] == 1)
    n_negative = n - n_positive
    if n_positive == 0 or n_negative == 0:
        raise ValueError("group is missing a class")
    n_selected = sum(1 for i in indexes if selected[i])
    true_positive = sum(1 for i in indexes if selected[i] and label[i] == 1)
    false_positive = sum(1 for i in indexes if selected[i] and label[i] == 0)
    return {
        "n": n,
        "n_positive": n_positive,
        "selection_rate": n_selected / n,
        "true_positive_rate": true_positive / n_positive,
        "false_positive_rate": false_positive / n_negative,
    }


def _field_metrics(
    keys: tuple[str, ...],
    row_keys: list[str],
    label: list[int],
    probability: list[float],
    cutoff: float,
) -> dict:
    selected = [value > cutoff for value in probability]
    groups = {}
    for key in keys:
        indexes = [i for i, value in enumerate(row_keys) if value == key]
        groups[key] = _rates(indexes, label, selected)
    selections = [groups[key]["selection_rate"] for key in keys]
    true_positive_rates = [groups[key]["true_positive_rate"] for key in keys]
    false_positive_rates = [groups[key]["false_positive_rate"] for key in keys]
    return {
        "groups": groups,
        "demographic_parity_difference": abs(max(selections) - min(selections)),
        "equalized_odds_difference": max(
            abs(true_positive_rates[0] - true_positive_rates[1]),
            abs(false_positive_rates[0] - false_positive_rates[1]),
        ),
        "n_selected": sum(selected),
    }


def fairness_from_table(table: dict, cutoff: float = PUBLISHED_CUTOFF) -> dict:
    """Group rates for gender and SeniorCitizen, plus the overall selection rate."""
    label = [int(value) for value in table["label"]]
    probability = [float(value) for value in table["probability"]]
    gender = [str(value) for value in table["gender"]]
    senior = [str(int(value)) for value in table["senior"]]
    n = len(probability)
    if not (len(label) == len(gender) == len(senior) == n):
        raise ValueError("score columns have different lengths")
    selected = [value > cutoff for value in probability]
    return {
        "n": n,
        "n_selected": sum(selected),
        "selection_rate": sum(selected) / n,
        "gender": _field_metrics(GENDER_KEYS, gender, label, probability, cutoff),
        "SeniorCitizen": _field_metrics(SENIOR_KEYS, senior, label, probability, cutoff),
    }


def assert_matches_published_fairness(table: dict, fairness: dict, cutoff: float = PUBLISHED_CUTOFF) -> None:
    """Raise AssertionError unless cutoff rates match the committed fairness report at six decimals."""
    got = fairness_from_table(table, cutoff)
    if got["n"] != int(fairness["overall"]["n"]):
        raise AssertionError(f"n {got['n']} != {fairness['overall']['n']}")
    if six(got["selection_rate"]) != six(fairness["overall"]["selection_rate"]):
        raise AssertionError(
            f"overall selection {six(got['selection_rate'])} != {six(fairness['overall']['selection_rate'])}"
        )
    for field in ("gender", "SeniorCitizen"):
        published = fairness["by_field"][field]
        recomputed = got[field]
        if six(recomputed["demographic_parity_difference"]) != six(published["demographic_parity_difference"]):
            raise AssertionError(
                f"{field} demographic parity {six(recomputed['demographic_parity_difference'])} "
                f"!= {six(published['demographic_parity_difference'])}"
            )
        if six(recomputed["equalized_odds_difference"]) != six(published["equalized_odds_difference"]):
            raise AssertionError(
                f"{field} equalized odds {six(recomputed['equalized_odds_difference'])} "
                f"!= {six(published['equalized_odds_difference'])}"
            )
        for key, group in published["groups"].items():
            rates = recomputed["groups"][key]
            if rates["n"] != int(group["n"]) or rates["n_positive"] != int(group["n_positive"]):
                raise AssertionError(f"{field} {key} counts do not match the fairness report")
            for metric in ("selection_rate", "true_positive_rate", "false_positive_rate"):
                if six(rates[metric]) != six(group[metric]):
                    raise AssertionError(
                        f"{field} {key} {metric} {six(rates[metric])} != {six(group[metric])}"
                    )


def build_score_table(holdout) -> dict:
    """gender, SeniorCitizen, label, and P(Churn=Yes) for each held-out row."""
    from governance.holdout import test_customer_id_sha256
    from governance.upstream import load_lock

    gender = [str(value) for value in holdout.test["gender"].tolist()]
    senior = [int(value) for value in holdout.test["SeniorCitizen"].tolist()]
    label = [int(value) for value in holdout.labels.tolist()]
    probability = [float(value) for value in holdout.proba.tolist()]
    if not (len(gender) == len(senior) == len(label) == len(probability)):
        raise ValueError("holdout columns have different lengths")
    lock = load_lock()["telco"]
    return {
        "scoring_model": "gradient_boosting",
        "upstream_commit": lock["commit"],
        "split": "telco_nba.pipeline.split_customers seed 42 test_size 0.25 stratify Churn",
        "positive_label": "Yes",
        "published_cutoff": PUBLISHED_CUTOFF,
        "positive_rule": (
            "A row is positive when probability is strictly greater than the cutoff. "
            "An exact tie stays negative, matching the saved pipeline predict() rule at 0.5."
        ),
        "test_customer_id_sha256": test_customer_id_sha256(holdout.test),
        "note": (
            "Public IBM telco holdout. Probabilities are the pinned gradient-boosting pipeline. "
            "The demo recomputes rates from these rows. This file is not a new metric and not a fairness certificate."
        ),
        "n": len(probability),
        "gender": gender,
        "senior": senior,
        "label": label,
        "probability": probability,
    }


def write_score_table(table: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(table, indent=2) + "\n")
