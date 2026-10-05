"""The Next.js demo vendors committed reports. The copies must stay byte-identical."""

from governance.paths import ROOT

PAIRS = (
    ("reports/fairness.json", "web/data/fairness.json"),
    ("reports/metrics_recomputed.json", "web/data/metrics_recomputed.json"),
    ("reports/shap_summary.json", "web/data/shap_summary.json"),
    ("reports/drift_psi.json", "web/data/drift_psi.json"),
    ("reports/gate_check.json", "web/data/gate_check.json"),
    ("assets/hero.png", "web/public/figures/hero.png"),
    ("assets/fairness_rates.png", "web/public/figures/fairness_rates.png"),
    ("assets/model_metrics.png", "web/public/figures/model_metrics.png"),
    ("assets/drift_psi.png", "web/public/figures/drift_psi.png"),
    ("assets/social-preview.png", "web/public/figures/social-preview.png"),
    ("reports/shap/global_bar.png", "web/public/figures/shap/global_bar.png"),
    ("reports/shap/global_summary.png", "web/public/figures/shap/global_summary.png"),
    ("reports/shap/local_5343-SGUBI.png", "web/public/figures/shap/local_5343-SGUBI.png"),
    ("reports/shap/local_0295-PPHDO.png", "web/public/figures/shap/local_0295-PPHDO.png"),
    ("reports/shap/local_5787-KXGIY.png", "web/public/figures/shap/local_5787-KXGIY.png"),
)


def test_web_demo_copies_match_committed_sources():
    for source, copy in PAIRS:
        assert (ROOT / copy).read_bytes() == (ROOT / source).read_bytes(), copy
