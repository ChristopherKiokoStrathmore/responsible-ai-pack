"""SHAP values for the pinned gradient-boosting churn model.

TreeSHAP is taken on the preprocessed columns, in the units of the model's
decision_function (log-odds). Global plots use those columns. Local plots add
the one-hot pieces back into the original field so a reviewer can read them.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from governance.holdout import Holdout, example_customer, load_holdout
from governance.paths import SHAP_DIR, SHAP_JSON_PATH
from governance.serialize import dumps_rounded

GLOBAL_MAX_DISPLAY = 12
LOCAL_MAX_DISPLAY = 10
LOCAL_TOP_FEATURES = 5


def _explanation(model, features):
    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["classifier"]
    transformed = np.asarray(preprocessor.transform(features), dtype=float)
    names = list(preprocessor.get_feature_names_out())
    explainer = shap.TreeExplainer(classifier)
    values = np.asarray(explainer.shap_values(transformed), dtype=float)
    if values.ndim != 2:
        raise RuntimeError(f"Expected a 2-d SHAP array, found shape {values.shape}")
    base = float(np.ravel(explainer.expected_value)[0])
    decisions = np.asarray(model.decision_function(features), dtype=float).reshape(-1)
    reconstructed = base + values.sum(axis=1)
    error = float(np.max(np.abs(reconstructed - decisions)))
    encoded = shap.Explanation(
        values=values,
        base_values=np.full(len(values), base),
        data=transformed,
        feature_names=names,
    )
    return {
        "values": values,
        "base": base,
        "names": names,
        "decisions": decisions,
        "max_abs_reconstruction_error": error,
        "encoded": encoded,
    }


def _mean_abs_encoded(values: np.ndarray, names: list[str]) -> list[dict]:
    means = np.mean(np.abs(values), axis=0)
    order = np.argsort(-means)
    return [{"feature": names[int(index)], "mean_abs_shap": float(means[int(index)])} for index in order]


def _mean_abs_original(values: np.ndarray, names: list[str], columns: list[str]) -> list[dict]:
    from telco_nba.explain import original_feature

    totals = {column: 0.0 for column in columns}
    means = np.mean(np.abs(values), axis=0)
    for index, name in enumerate(names):
        totals[original_feature(name, columns)] += float(means[index])
    ranked = sorted(totals, key=lambda column: (-totals[column], column))
    return [{"feature": column, "mean_abs_shap": totals[column]} for column in ranked]


def _local_original(shap_row: np.ndarray, names: list[str], columns: list[str], raw_row) -> list[dict]:
    from telco_nba.explain import original_feature

    totals = {column: 0.0 for column in columns}
    for value, name in zip(shap_row, names):
        totals[original_feature(name, columns)] += float(value)
    ranked = sorted(totals, key=lambda column: (-abs(totals[column]), column))
    rows = []
    for column in ranked[:LOCAL_TOP_FEATURES]:
        rows.append({"feature": column, "value": _display_value(raw_row[column]), "shap": totals[column]})
    return rows


def _select_rows(test, proba: np.ndarray) -> list[tuple[int, str]]:
    example_index = int(np.flatnonzero(test["TotalCharges"].notna().to_numpy())[0])
    chosen = [(example_index, "first_held_out_row_with_numeric_TotalCharges")]
    used = {example_index}
    for index in np.argsort(-proba):
        index = int(index)
        if index not in used:
            chosen.append((index, "highest_held_out_churn_probability"))
            used.add(index)
            break
    for index in np.argsort(proba):
        index = int(index)
        if index not in used:
            chosen.append((index, "lowest_held_out_churn_probability"))
            used.add(index)
            break
    return chosen


def _display_value(raw) -> str:
    if raw is None or pd.isna(raw):
        return "missing"
    return str(raw)


def _grouped_explanation(shap_row, names, columns, raw_row, base: float):
    from telco_nba.explain import original_feature

    totals = np.zeros(len(columns), dtype=float)
    index_of = {column: index for index, column in enumerate(columns)}
    for value, name in zip(shap_row, names):
        totals[index_of[original_feature(name, columns)]] += float(value)
    display = [_display_value(raw_row[column]) for column in columns]
    return shap.Explanation(
        values=totals,
        base_values=base,
        data=np.zeros(len(columns)),
        display_data=np.array(display, dtype=object),
        feature_names=list(columns),
    )


def _save_current(path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.gcf().savefig(path, dpi=120, bbox_inches="tight")
    plt.close("all")


def build_shap_report(holdout: Holdout | None = None, write_plots: bool = False) -> dict:
    holdout = holdout or load_holdout()
    packed = _explanation(holdout.scoring_model, holdout.features)
    columns = list(holdout.features.columns)
    encoded = _mean_abs_encoded(packed["values"], packed["names"])
    original = _mean_abs_original(packed["values"], packed["names"], columns)
    locals_ = []
    for index, reason in _select_rows(holdout.test, holdout.proba):
        row = holdout.test.iloc[index]
        customer_id = str(row["customerID"])
        shap_row = packed["values"][index]
        probability = float(holdout.proba[index])
        plot_name = f"local_{customer_id}.png"
        locals_.append(
            {
                "customer_id": customer_id,
                "row_index": int(index),
                "selection_reason": reason,
                "historical_churn": str(row["Churn"]),
                "churn_probability": probability,
                "decision_function": float(packed["decisions"][index]),
                "shap_base_value": packed["base"],
                "shap_sum": float(shap_row.sum()),
                "top_original_features": _local_original(shap_row, packed["names"], columns, row),
                "plot": f"reports/shap/{plot_name}",
            }
        )
        if write_plots:
            grouped = _grouped_explanation(shap_row, packed["names"], columns, row, packed["base"])
            shap.plots.waterfall(grouped, max_display=LOCAL_MAX_DISPLAY, show=False)
            plt.title(f"{customer_id}  P(Churn=Yes)={probability:.6f}")
            _save_current(SHAP_DIR / plot_name)
    if write_plots:
        shap.plots.beeswarm(packed["encoded"], max_display=GLOBAL_MAX_DISPLAY, show=False)
        plt.title("Held-out TreeSHAP, encoded columns")
        _save_current(SHAP_DIR / "global_summary.png")
        shap.plots.bar(packed["encoded"], max_display=GLOBAL_MAX_DISPLAY, show=False)
        plt.title("Mean absolute TreeSHAP, encoded columns")
        _save_current(SHAP_DIR / "global_bar.png")
    example = example_customer(holdout.test)
    return {
        "method": "shap.TreeExplainer on the gradient-boosting classifier inside the saved pipeline",
        "output_units": "decision_function log-odds of P(Churn=Yes)",
        "n_explained": int(len(holdout.test)),
        "n_encoded_features": int(len(packed["names"])),
        "base_value": packed["base"],
        "max_abs_reconstruction_error": packed["max_abs_reconstruction_error"],
        "global_summary_plot": "reports/shap/global_summary.png",
        "global_bar_plot": "reports/shap/global_bar.png",
        "global_plot_space": "one-hot and scaled columns seen by the booster",
        "local_plot_space": (
            "Signed SHAP values summed within each original field. "
            "The plot label is field=raw value. The plotted bar is not a causal effect."
        ),
        "original_feature_aggregation": (
            "Mean absolute SHAP of an original field is the sum of the mean absolute "
            "SHAP of its encoded columns."
        ),
        "mean_abs_shap_encoded": encoded,
        "mean_abs_shap_by_original_feature": original,
        "local_customers": locals_,
        "example_customer_id_from_split": str(example["customerID"]),
    }


def write_shap_report(path=None) -> dict:
    report = build_shap_report(write_plots=True)
    destination = path or SHAP_JSON_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(dumps_rounded(report))
    return report
