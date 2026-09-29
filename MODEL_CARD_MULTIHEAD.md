---
language:
- en
tags:
- text-classification
---

# Model card: multi-head customer-care classifier

This card covers the model behind [MULTI-HEAD-](https://github.com/ChristopherKiokoStrathmore/MULTI-HEAD-) at commit `809bccd61077898849c428f37521fa198f7c7bf6`. Every figure below is copied from a file at that commit. If the repo does not state a fact, this card says so.

This is a personal framework, not an employer policy. This pack does not host the weights and did not score the live API.

## Model details

- Source repo: [ChristopherKiokoStrathmore/MULTI-HEAD-](https://github.com/ChristopherKiokoStrathmore/MULTI-HEAD-). The pinned commit is the default-branch head read for this card.
- What that repo contains: a Next.js frontend and a live-API eval harness. [`package.json`](https://github.com/ChristopherKiokoStrathmore/MULTI-HEAD-/blob/809bccd61077898849c428f37521fa198f7c7bf6/package.json) names the package `care-message-classifier-ui`, version 1.0.0.
- The README describes a remote three-head classifier with outputs Issue, Sentiment, and Urgency. The browser calls `POST /predict` and `POST /predict_batch` on the base URL in `NEXT_PUBLIC_API_URL`.
- The README gives this deployed base URL: `https://thechriskioko--threehead-serve-server-fastapi-app.modal.run`.
- Weights, architecture, parameter count, loss, and training code: not documented in source repo. [`eval/README.md`](https://github.com/ChristopherKiokoStrathmore/MULTI-HEAD-/blob/809bccd61077898849c428f37521fa198f7c7bf6/eval/README.md) says training code is not in the repo.
- [`lib/types.ts`](https://github.com/ChristopherKiokoStrathmore/MULTI-HEAD-/blob/809bccd61077898849c428f37521fa198f7c7bf6/lib/types.ts) types a prediction as `issue`, `sentiment`, `urgency`, optional `urgency_score`, and optional confidence for issue and sentiment.

## Intended use

The README's intended use is a demo UI: one message, or a CSV batch, labeled on issue, sentiment, and urgency.

[`lib/trust.ts`](https://github.com/ChristopherKiokoStrathmore/MULTI-HEAD-/blob/809bccd61077898849c428f37521fa198f7c7bf6/lib/trust.ts) sets `ISSUE_ABSTAIN_THRESHOLD` to 0.6. The comparison is strict `<`, so a score of exactly 0.6 is accepted. Below 0.6 the UI shows needs review / do not auto-route, and still shows the top issue guess. The README states the same rule.

The intended user, in that repo's words, is someone running the demo or the eval harness. A production auto-router is outside what the abstain copy allows.

## Out-of-scope use

- Treating a pass of `eval/gates.smoke.json` as model quality. That file's own note says the floors are harness-health thresholds for the synthetic smoke CSV, not model-quality claims.
- Auto-routing an issue when confidence is below 0.6.
- Quoting smoke-fixture scores as quality. `eval/README.md` says not to.
- Assuming this responsible-ai-pack repo measured the live model. It did not.

## Data

- Training set size, source, license, language mix, and collection window: not documented in source repo.
- A real labeled held-out file: not in the repo. `eval/README.md` tells the reader to keep human-gold outside git and not to commit customer messages.
- `eval/synthetic-heldout.smoke.csv` is described as synthetic smoke data, not production gold and not a real held-out set. This card does not quote scores on it, because the repo does not commit a scored report.
- Labels the eval README says were observed from the live API, 10 issue classes: `Airtel_Money_Reversal`, `Airtel_Money_Transfer`, `App_Rewards`, `Complaint_General`, `Data_Bundle_Problems`, `Network_Issues`, `Non_Actionable`, `Product_Enquiry`, `Router_WiFi_5G`, `SIM_Line_Services`. Sentiment labels: `negative`, `not_negative`. Urgency labels: `low`, `medium`, `emergency`.
- Who those class names were trained on: not documented in source repo.

## Metrics

Held-out accuracy, macro-F1, emergency recall, false-emergency rate, and quadratic-weighted kappa on gold labels: not documented in source repo. The harness in `eval/urgency-ops.mjs` defines the urgency metrics. The repo does not commit the JSON a gold run would write.

The numeric thresholds that are in the repo:

| Item | Value | File |
| --- | ---: | --- |
| Issue abstain threshold | 0.6 | [`lib/trust.ts`](https://github.com/ChristopherKiokoStrathmore/MULTI-HEAD-/blob/809bccd61077898849c428f37521fa198f7c7bf6/lib/trust.ts) |
| Smoke `minEmergencyRecall` | 0.01 | [`eval/gates.smoke.json`](https://github.com/ChristopherKiokoStrathmore/MULTI-HEAD-/blob/809bccd61077898849c428f37521fa198f7c7bf6/eval/gates.smoke.json) |
| Smoke `maxFalseEmergencyRate` | 0.99 | same file |
| Smoke `minScoredRows` | 1 | same file |

`eval/README.md` also says the abstain sweep it prints uses thresholds 0.40–0.80, and that on a 10-class issue head a top softmax around 0.5 is often not enough to trust. Those are instructions and a caution, not measured quality.

The same README says smoke floors fail on a dead API, an incomplete score, or a total urgency collapse. `minEmergencyRecall` 0.01 fails only if gold emergencies exist and recall is 0. That is not a quality bar this card can adopt.

Operational figures the root README does state, as product behavior rather than accuracy: CSV rows go out in chunks of 20; timeouts are 120s for `/predict` and 180s for a `/predict_batch` chunk; a cold start is described as 20–40 seconds in the root README and about 40–120 seconds in the eval README's CI note.

Calibration, slice metrics, and confusion counts on gold data: not documented in source repo.

## Limitations

- There is no model file in the source repo, so this pack cannot recompute a metric or draw SHAP for it.
- The smoke gates would still pass a weak model. The file says so.
- The issue vocabulary includes Airtel Money label strings. The training population for those labels is not documented in source repo. This card does not turn those strings into a claim about any operator's customers.
- The live API does not return a second-best issue, per `eval/README.md`, so top-2 accuracy is not available without a backend change.
- Fairness by language, gender, region, or any other attribute: not documented in source repo.

## Human review

The documented review control is the issue abstain at 0.6: the UI marks the row needs review / do not auto-route and still shows the top guess. Reviewer role, sample rate, and what happens after the banner: not documented in source repo.

`eval/README.md` says a later private gold file is where a tighter false-emergency floor would belong. Until that file exists in a place this card can quote, emergency-recall quality remains not documented in source repo.
