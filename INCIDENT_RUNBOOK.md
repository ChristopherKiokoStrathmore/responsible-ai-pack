# Incident runbook

Use this when a gated churn metric is below its floor. The floors are ROC-AUC 0.82, PR-AUC 0.63, and top-decile lift 2.60, from `gates.yaml`. Independent portfolio project built on public data. This repo has no live queue and no on-call rota.

## Detection

`python scripts/check_gates.py` recomputes the three metrics on the pinned model and the seed-42 split. It prints `FAIL`, the metric, the value, and the gate, and exits non-zero. GitHub Actions runs that command after the tests. A red run of the job `Recompute held-out metrics and apply gates` is the detection signal in CI.

The committed baseline in `reports/gate_check.json` passed: ROC-AUC 0.846001, PR-AUC 0.656070, top-decile lift 2.806733.

A PSI value at or above 0.250000 is a review event in `MONITORING.md`. It is not this incident. Open this runbook when a metric in `gates.yaml` fails.

## Triage

Do not train a new model inside the incident.

1. Read the script output and name the metric that failed.
2. Check `upstream.lock.json`. A changed commit or a failed SHA-256 means the artifact or the split code is not the pinned one.
3. If the lock still matches and the frozen split fails, the metric code in this repo changed, or the saved file no longer matches its hash. The hash check should already have stopped the fetch.
4. If the failure is on a future labeled batch rather than this frozen split, record the batch's row count and the metric values before changing any threshold.

The last green baseline is the table in `reports/metrics_recomputed.json`. Compare the failed value with that table and with the floor, not with a recollection of the number.

## Rollback

Stop using the failed artifact as an input to a customer action. Nobody in this portfolio is scored in production; say that explicitly if the failed run is this repo's CI.

The model to keep is the gradient-boosting file at the commit whose `check_gates.py` passed. In this repo that commit is `21f6115931f4358ebc7cc87d9ba1f4d87fd015aa`, loaded by `telco_nba.model_io.load_churn_model`. Do not point the loader at a replacement file until a recompute is at or above every floor.

If a change in this repo caused the failure, revert that change. Lowering a floor so the same failed value passes is not a rollback.

## Communication

Tell the person who would act on a score that scoring is paused, which metric failed, the value, and the gate. This repo has no customer notification list. Do not invent one, and do not describe the pause as an operator incident.

State whether any decision used the failed artifact. For a failure of this CI job, the answer is that the job scores the public holdout only.

## Postmortem

Write a short note after the metric is back above its floor, or after the decision to keep the model paused:

- When the failure was detected, and the command or CI run that showed it.
- The metric, the value, and the gate.
- Cause: wrong artifact, broken split, changed metric code, or a real drop on a new batch.
- Whether anyone acted on a score from the failed artifact.
- What would have caught it sooner.
- Whether any document needs a correction. Do not move a gate down to match a worse number without a new measurement written into `reports/`.
