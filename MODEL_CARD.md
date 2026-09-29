---
language:
- en
library_name: sklearn
tags:
- tabular-classification
- scikit-learn
datasets:
- IBM Telco Customer Churn
---

# Model card: telco churn gradient boosting

Governance write-up for the churn model saved in [telco-churn-nba-engine](https://github.com/ChristopherKiokoStrathmore/telco-churn-nba-engine) at commit `21f6115931f4358ebc7cc87d9ba1f4d87fd015aa`. This repo loads that artifact. It does not train a replacement.

This is a personal framework, not an employer policy.

## Model details

- Author of the portfolio: Chris Nguu.
- Scoring artifact: `artifacts/churn_model.joblib` in the upstream repo. SHA-256 `fe1cd3c3ea69565c133f9964744c9d4f5d55908ef883908cfb380f1fc37d3509`, checked by `upstream.lock.json`.
- Loader: `telco_nba.model_io.load_churn_model`, documented in the upstream file [`src/telco_nba/model_io.py`](https://github.com/ChristopherKiokoStrathmore/telco-churn-nba-engine/blob/21f6115931f4358ebc7cc87d9ba1f4d87fd015aa/src/telco_nba/model_io.py).
- Model: scikit-learn `GradientBoostingClassifier` inside a `Pipeline`. The pipeline's `predict_proba(frame)[:, 1]` is P(Churn=Yes). Classes are `[0, 1]`.
- The upstream [`reports/metrics.json`](https://github.com/ChristopherKiokoStrathmore/telco-churn-nba-engine/blob/21f6115931f4358ebc7cc87d9ba1f4d87fd015aa/reports/metrics.json) records the gradient-boosting parameters as `n_estimators` 100, `learning_rate` 0.100000, `max_depth` 3, `subsample` 1.000000, and `random_state` 42. The same file sets `scoring_model` to `gradient_boosting`.
- That file also records the training environment as Python 3.12.3 and scikit-learn 1.5.2. This pack scores the saved file with scikit-learn 1.5.2.
- The same commit stores a logistic regression and a dummy prior in `artifacts/scoring_bundle.joblib`. They are comparison models. They are not the scoring artifact.

## Intended use

Rank customers in the IBM telco sample by the model's estimate of P(Churn=Yes), and show the TreeSHAP contributions behind one score so a person can read the model.

The intended user of this pack is someone reviewing that public model. A production retention desk could use the same documents as a pattern: a card, a held-out metric gate, a group-metric table, and a local plot before anyone acts on a score.

## Out-of-scope use

- Any live operator's customers, including customers in Kenya. The training table is the IBM US sample.
- Deciding credit, disconnection, eligibility, or a penalty.
- Sending an offer or placing a call with no person in the loop.
- Treating a SHAP value as a cause of churn.
- Treating the logistic regression or the add-on models in the upstream repo as this scoring model. Add-on, CLV, and next-best-action figures stay in the upstream metrics file and are not re-quoted here.
- Claiming a fairness pass. The group table is a measurement, not a certificate.

## Data

Quoted from upstream `reports/metrics.json` at the commit above, unless a row says it was recomputed here.

| Item | Value | Where |
| --- | --- | --- |
| Dataset | IBM Telco Customer Churn | upstream `dataset` |
| Rows | 7043 | upstream `dataset.n_rows`, also `reports/metrics_recomputed.json` |
| Churn = Yes | 1869, rate 0.265370 | upstream `dataset` |
| CSV SHA-256 | `16320c9c1ec72448db59aa0a26a0b95401046bef5d02fd3aeb906448e3055e91` | upstream `dataset.sha256` and `upstream.lock.json` |
| Blank TotalCharges | 11, all 11 at tenure 0 | upstream `dataset` |
| Repository license note | Apache-2.0 on the IBM repository covers that code pattern. The IBM repository does not state a separate license for the CSV. | upstream `dataset` |

The split is `telco_nba.pipeline.split_customers`: seed 42, `test_size` 0.250000, stratified on `Churn`. Recomputed in `reports/metrics_recomputed.json`: 5282 training rows (churn rate 0.265430) and 1761 test rows (churn rate 0.265190, 467 positives). The first held-out row with numeric `TotalCharges` is customer `5343-SGUBI`, historical Churn No. The label is not a feature. `gender` and `SeniorCitizen` are features.

Blank `TotalCharges` cells are missing values. Median imputation sits inside the saved pipeline.

## Metrics

Recomputed on the held-out rows from the saved pipelines, with `telco_nba.metrics.classification_metrics`. The six-decimal values match upstream `reports/metrics.json`. The check is `matches_upstream_metrics_at_six_decimals` in `reports/metrics_recomputed.json`.

Top-decile lift uses the upstream definition in that file: k = floor(n_test / 10), and rows whose scores tie across the cut share it. Here k is 176. The test base rate is 0.265190.

| Model | ROC-AUC | PR-AUC | Top-decile lift |
| --- | ---: | ---: | ---: |
| Dummy prior | 0.500000 | 0.265190 | 1.000000 |
| Logistic regression | 0.846490 | 0.638090 | 2.785308 |
| Gradient boosting (scoring model) | 0.846001 | 0.656070 | 2.806733 |

On this split, logistic regression has the higher ROC-AUC. Gradient boosting has the higher PR-AUC and the higher top-decile lift. The pinned scoring artifact remains gradient boosting.

Hard labels for the group table use the pipeline's `predict()`: positive when P(Churn=Yes) > 0.5. ROC-AUC in that table uses the probability. Full cells are in `reports/fairness.json`.

| Field | Demographic parity difference | Equalized odds difference |
| --- | ---: | ---: |
| gender | 0.030582 | 0.020532 |
| SeniorCitizen | 0.223259 | 0.167878 |

Female (n=863, label rate 0.278100) and Male (n=898, label rate 0.252784) are close on selection rate (0.213210 and 0.182628), true positive rate (0.508333 and 0.488987), false positive rate (0.099518 and 0.078987), and ROC-AUC (0.839811 and 0.851937).

SeniorCitizen 1 (n=286, label rate 0.426573) is not close to SeniorCitizen 0 (n=1475, label rate 0.233898). Selection rates are 0.384615 and 0.161356. True positive rates are 0.622951 and 0.455072. False positive rates are 0.207317 and 0.071681. ROC-AUC is 0.800680 and 0.845995. The higher selection rate sits next to a higher churn rate, and the false-positive rate is higher as well. Both fields are model inputs. This is one split and one cutoff.

TreeSHAP on the 1761 held-out rows reconstructs `decision_function` with max absolute error 0.000000 (`reports/shap_summary.json`). The largest mean absolute SHAP among encoded columns is `cat__Contract_Month-to-month` at 0.643924. Summed back to original fields, the largest is Contract at 0.837003, then tenure at 0.355529. Mean absolute SHAP is 0.019143 for gender and 0.044300 for SeniorCitizen.

## Limitations

- The table is IBM's public US sample, 7043 rows. It is not Kenyan operator data. These metrics are not local performance for any network.
- `gender` and `SeniorCitizen` are inputs. The file has no race, ethnicity, region, language, or disability column. The group check cannot speak to those.
- SeniorCitizen 1 has 286 held-out rows. That is a small group next to 1475 rows with value 0.
- The hard-label rates use one cutoff, P(Churn=Yes) > 0.5. They are not the upstream next-best-action cutoffs.
- There is one stratified holdout. This card does not report a confidence interval.
- SHAP explains the gradient-boosting log-odds. It does not say what would change churn if someone edited a field.
- Logistic regression wins on ROC-AUC on this split. The scoring file is still the gradient-boosting pipeline.

## Human review

Nothing in this pack contacts a customer. A person who uses a score should see the probability and the local plot (`reports/shap/`) before any save call or offer, and should treat the plot as a description of the model.

Customer `5343-SGUBI` has held-out probability 0.122990 and historical Churn No. The largest original-field SHAP on that row is Contract = One year at -0.511087. Customer `0295-PPHDO` has probability 0.924460 and historical Churn Yes. Customer `5787-KXGIY` has probability 0.006431 and historical Churn No. Those three plots are examples of review material, not a decision.

The SeniorCitizen gap is a reason for a person to look at that group before widening use. This repo does not fit a second threshold to close the gap.
