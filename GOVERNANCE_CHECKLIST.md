# AI governance checklist

Personal checklist for the churn model in this repo, mapped to the NIST AI Risk Management Framework functions Govern, Map, Measure, and Manage. This is a personal framework, not an employer policy.

If a later project used personal data of people in Kenya, the statute to read is the Kenya Data Protection Act 2019. This page names that Act. It does not interpret it, and it does not claim compliance.

## Govern

- [x] The model card names the artifact, the commit, and the person whose portfolio this is.
- [x] The README states that the pack is not an employer policy and uses the public IBM sample only.
- [x] Kenya Data Protection Act 2019 is named, with no section numbers and no compliance claim.
- [ ] A real deployment still needs an accountable owner inside the organisation that would act on a score. This repo cannot appoint one.

## Map

- [x] Intended use and out-of-scope use are written in `MODEL_CARD.md` and `MODEL_CARD_MULTIHEAD.md`.
- [x] The churn training table is identified by the upstream metrics file and by the CSV SHA-256 in `upstream.lock.json`.
- [x] `gender` and `SeniorCitizen` are documented as model inputs, and as the only group fields this pack measures.
- [x] The multi-head card says when the source repo does not document data or quality.

## Measure

- [x] Held-out ROC-AUC, PR-AUC, and top-decile lift are recomputed in `reports/metrics_recomputed.json` from the saved models.
- [x] TreeSHAP global and local plots are in `reports/shap/`, with numbers in `reports/shap_summary.json`.
- [x] Fairlearn selection rate, true positive rate, false positive rate, and ROC-AUC by gender and SeniorCitizen are in `reports/fairness.json`, with demographic parity and equalized odds differences.
- [x] PSI on the pinned split is in `reports/drift_psi.json`. That file says the split is not a time comparison.

## Manage

- [x] `gates.yaml` holds floors under the recomputed churn metrics. `scripts/check_gates.py` recomputes them and fails if one is below its floor. GitHub Actions runs that script.
- [x] `MONITORING.md` says what a later batch would compare, and what this repo does not watch.
- [x] `INCIDENT_RUNBOOK.md` covers detection, triage, rollback, communication, and a postmortem when a gated metric is below its floor.
- [ ] Fairness gaps are reported and are not a CI floor. A disparity budget needs an owner this repo does not have.
- [ ] The multi-head emergency-recall smoke floor stays in that other repo. This pack does not gate it, because the weights and gold labels are not there.
