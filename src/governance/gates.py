"""Compare recomputed held-out metrics with the floors in gates.yaml."""

from __future__ import annotations

import math

import yaml

from governance.holdout import build_metrics_report
from governance.paths import GATE_CHECK_PATH, GATES_PATH
from governance.serialize import dumps_rounded

GATED_METRICS = ("roc_auc", "pr_auc", "top_decile_lift")


def load_gates(path=None) -> dict:
    return yaml.safe_load((path or GATES_PATH).read_text())


def floor_to_decimals(value: float, decimals: int) -> float:
    factor = 10 ** decimals
    return math.floor((value * factor) + 1e-9) / factor


def scoring_metrics(report: dict) -> dict[str, float]:
    block = report["churn_models"][report["scoring_model"]]
    return {name: float(block[name]) for name in GATED_METRICS}


def evaluate_gates(values: dict[str, float], document: dict) -> dict:
    floors = document["gates"]
    failures = []
    rows = []
    for name in GATED_METRICS:
        value = float(values[name])
        floor = float(floors[name])
        passed = value >= floor
        rows.append({"metric": name, "value": value, "gate": floor, "passed": passed})
        if not passed:
            failures.append(name)
    return {"passed": not failures, "failures": failures, "metrics": rows}


def build_gate_check() -> dict:
    document = load_gates()
    report = build_metrics_report()
    if report["scoring_model"] != document["scoring_model"]:
        raise RuntimeError("gates.yaml scoring_model does not match the recomputed report")
    if report["upstream_commit"] != document["upstream_commit"]:
        raise RuntimeError("gates.yaml commit does not match the recomputed report")
    values = scoring_metrics(report)
    result = evaluate_gates(values, document)
    result["upstream_commit"] = report["upstream_commit"]
    result["scoring_model"] = report["scoring_model"]
    result["matches_upstream_metrics_at_six_decimals"] = report["matches_upstream_metrics_at_six_decimals"]
    return result


def write_gate_check(path=None) -> dict:
    result = build_gate_check()
    destination = path or GATE_CHECK_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(dumps_rounded(result))
    return result


def format_gate_check(result: dict) -> str:
    lines = []
    for row in result["metrics"]:
        status = "PASS" if row["passed"] else "FAIL"
        lines.append(
            f"{status} {row['metric']}: value {row['value']:.6f} gate {row['gate']:.2f}"
        )
    if result["passed"]:
        lines.append("All gated metrics are at or above their floors.")
    else:
        lines.append("Failed: " + ", ".join(result["failures"]))
    return "\n".join(lines)
