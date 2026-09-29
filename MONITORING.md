# Monitoring

What to watch if the pinned churn model were scored on a later batch of the same columns. This is a personal framework, not an employer policy. The numbers below are the committed baseline on the IBM sample, not a live feed.

## Performance

Recompute the same three metrics the gate uses, with `telco_nba.metrics.classification_metrics` on labeled rows the model did not train on:

| Metric | Floor in `gates.yaml` | Recomputed on the pinned split |
| --- | ---: | ---: |
| ROC-AUC | 0.82 | 0.846001 |
| PR-AUC | 0.63 | 0.656070 |
| Top-decile lift | 2.60 | 2.806733 |

`python scripts/check_gates.py` loads the saved models, rebuilds the seed-42 split, and exits non-zero if any value is below its floor. The floors sit under the recomputed figures by the margins in `gates.yaml` (0.02, 0.02, and 0.20), then rounded down to 2 decimal places. They are not confidence intervals.

A later labeled batch should use the same metric functions. It should not reuse this test split's score as if it were the new batch. Group rates in `reports/fairness.json` are part of the review pack. They are not floors. This repo does not set a disparity budget.

The multi-head repo's smoke file can fail a live call when emergency recall on its synthetic file collapses. That check is not run here. Gold emergency recall for that model is not documented in source repo.

## Drift

`python scripts/run_drift.py` writes `reports/drift_psi.json`. Population stability index compares a reference sample with a current sample. Shares below the clip floor 0.000001 are raised to that floor and re-normalized. The review trigger in that file is 0.250000. A feature at or above the trigger is a reason to read the batch before promoting an artifact. It does not by itself fail `gates.yaml`.

The reference implemented today is the training half of `telco_nba.pipeline.split_customers`. The current sample is the held-out half of that same draw. The report says this is not two time periods. On that comparison, `n_above_trigger` is 0.

| Feature | PSI |
| --- | ---: |
| tenure | 0.005914 |
| MonthlyCharges | 0.012474 |
| TotalCharges | 0.008491 |
| Contract | 0.000040 |
| InternetService | 0.000007 |
| PaymentMethod | 0.000700 |
| gender | 0.000191 |
| SeniorCitizen | 0.000001 |

Numeric columns ask for 10 quantile bins taken from the reference, plus a missing bin. The edges actually used are stored in the JSON. Categorical columns use the sorted union of levels.

For a real monitor, keep this training split as the reference and pass the new batch as the current sample, with the same column names. Do not refit the quantile edges on the new batch.

## What this repo does not monitor

- Latency or errors of the upstream `POST /score` service.
- Movement in the upstream next-best-action cutoffs.
- Feature nulls other than the missing bin inside PSI.
- Any multi-head quality metric. The weights are not in that repo.
