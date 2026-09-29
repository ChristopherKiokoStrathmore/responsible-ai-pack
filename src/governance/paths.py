"""Repository paths."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VENDOR = ROOT / "vendor"
REPORTS = ROOT / "reports"
SHAP_DIR = REPORTS / "shap"
LOCK_PATH = ROOT / "upstream.lock.json"
GATES_PATH = ROOT / "gates.yaml"
METRICS_PATH = REPORTS / "metrics_recomputed.json"
FAIRNESS_PATH = REPORTS / "fairness.json"
SHAP_JSON_PATH = REPORTS / "shap_summary.json"
DRIFT_PATH = REPORTS / "drift_psi.json"
GATE_CHECK_PATH = REPORTS / "gate_check.json"
