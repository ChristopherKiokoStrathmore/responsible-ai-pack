import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import {
  fairnessAtCutoff,
  logistic,
  populationStabilityIndex,
  sameSix,
  shiftCounts,
} from "./demoMath.ts";

const here = dirname(fileURLToPath(import.meta.url));

function readJson(name: string) {
  return JSON.parse(readFileSync(join(here, "../data", name), "utf8"));
}

const scores = readJson("holdout_scores.json");
const fairness = readJson("fairness.json");
const drift = readJson("drift_psi.json");
const shap = readJson("shap_summary.json");

test("published cutoff reproduces reports/fairness.json at six decimals", () => {
  for (const field of ["gender", "SeniorCitizen"] as const) {
    const got = fairnessAtCutoff(scores, scores.published_cutoff, field);
    const published = fairness.by_field[field];
    assert.equal(sameSix(got.demographicParityDifference, published.demographic_parity_difference), true);
    assert.equal(sameSix(got.equalizedOddsDifference, published.equalized_odds_difference), true);
    assert.equal(sameSix(got.selectionRate, fairness.overall.selection_rate), true);
    for (const group of got.groups) {
      const expected = published.groups[group.key];
      assert.equal(group.n, expected.n);
      assert.equal(group.nPositive, expected.n_positive);
      assert.equal(sameSix(group.selectionRate, expected.selection_rate), true);
      assert.equal(sameSix(group.truePositiveRate, expected.true_positive_rate), true);
      assert.equal(sameSix(group.falsePositiveRate, expected.false_positive_rate), true);
    }
  }
});

test("moving the cutoff changes who is selected", () => {
  const published = fairnessAtCutoff(scores, 0.5, "SeniorCitizen");
  const lower = fairnessAtCutoff(scores, 0.3, "SeniorCitizen");
  assert.ok(lower.nSelected > published.nSelected);
});

test("PSI on the published bin counts matches reports/drift_psi.json", () => {
  for (const feature of drift.features) {
    const psi = populationStabilityIndex(feature.reference_counts, feature.current_counts, drift.clip_floor);
    assert.equal(sameSix(psi, feature.psi), true, feature.name);
    const shifted = shiftCounts(feature.current_counts, 0, 0);
    const again = populationStabilityIndex(feature.reference_counts, shifted, drift.clip_floor);
    assert.equal(sameSix(again, feature.psi), true, feature.name);
  }
});

test("putting the whole current batch in one bin can cross the review trigger", () => {
  const contract = drift.features.find((feature: { name: string }) => feature.name === "Contract");
  const shifted = shiftCounts(contract.current_counts, 0, 1);
  const psi = populationStabilityIndex(contract.reference_counts, shifted, drift.clip_floor);
  assert.ok(psi >= drift.psi_review_trigger);
});

test("logistic of the published decision function matches the local probability", () => {
  for (const customer of shap.local_customers) {
    assert.equal(sameSix(logistic(customer.decision_function), customer.churn_probability), true);
  }
});
