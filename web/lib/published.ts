import driftJson from "@/data/drift_psi.json";
import fairnessJson from "@/data/fairness.json";
import gateCheckJson from "@/data/gate_check.json";
import metricsJson from "@/data/metrics_recomputed.json";
import shapJson from "@/data/shap_summary.json";

/**
 * Readings of the JSON files in web/data.
 * Those files are byte copies of the committed reports. Do not type a metric here.
 */

export const links = {
  pack: "https://github.com/ChristopherKiokoStrathmore/responsible-ai-pack",
  sibling: "https://github.com/ChristopherKiokoStrathmore/telco-churn-nba-engine",
  siblingCommit: `https://github.com/ChristopherKiokoStrathmore/telco-churn-nba-engine/tree/${metricsJson.upstream_commit}`,
  modelCard:
    "https://github.com/ChristopherKiokoStrathmore/responsible-ai-pack/blob/main/MODEL_CARD.md",
  checklist:
    "https://github.com/ChristopherKiokoStrathmore/responsible-ai-pack/blob/main/GOVERNANCE_CHECKLIST.md",
  gates:
    "https://github.com/ChristopherKiokoStrathmore/responsible-ai-pack/blob/main/gates.yaml",
  monitoring:
    "https://github.com/ChristopherKiokoStrathmore/responsible-ai-pack/blob/main/MONITORING.md",
  runbook:
    "https://github.com/ChristopherKiokoStrathmore/responsible-ai-pack/blob/main/INCIDENT_RUNBOOK.md",
} as const;

export const holdout = {
  author: "Christopher Nguu",
  repository: metricsJson.upstream_repository,
  commit: metricsJson.upstream_commit,
  scoringModel: metricsJson.scoring_model,
  scoringModelSha256: metricsJson.scoring_model_sha256,
  datasetSha256: metricsJson.dataset_sha256,
  datasetRows: metricsJson.dataset_n_rows,
  datasetChurnRate: metricsJson.dataset_churn_rate,
  splitFunction: metricsJson.split_function,
  seed: metricsJson.split.seed,
  testSize: metricsJson.split.test_size,
  stratify: metricsJson.split.stratify,
  nTrain: metricsJson.split.n_train,
  nTest: metricsJson.split.n_test,
  trainChurnRate: metricsJson.split.train_churn_rate,
  testChurnRate: metricsJson.split.test_churn_rate,
  testChurnYes: metricsJson.split.test_churn_yes,
  exampleCustomerId: metricsJson.split.example_customer_id,
  matchesUpstream: metricsJson.matches_upstream_metrics_at_six_decimals,
  positiveLabel: metricsJson.positive_label,
  inputsIncludeGender: metricsJson.inputs_include_gender,
  inputsIncludeSeniorCitizen: metricsJson.inputs_include_SeniorCitizen,
} as const;

const modelOrder = ["dummy_prior", "logistic_regression", "gradient_boosting"] as const;

const modelLabels: Record<(typeof modelOrder)[number], string> = {
  dummy_prior: "Dummy prior",
  logistic_regression: "Logistic regression",
  gradient_boosting: "Gradient boosting",
};

export const models = modelOrder.map((id) => {
  const row = metricsJson.churn_models[id];
  return {
    id,
    label: modelLabels[id],
    scoring: id === metricsJson.scoring_model,
    rocAuc: row.roc_auc,
    prAuc: row.pr_auc,
    topDecileLift: row.top_decile_lift,
    topDecileK: row.top_decile_k,
    baseRate: row.base_rate,
  };
});

export type PublishedModel = (typeof models)[number];

/** Floors as written in gates.yaml. gate_check.json stores the same floors at six decimals. */
export const floorsAsWritten = {
  roc_auc: "0.82",
  pr_auc: "0.63",
  top_decile_lift: "2.60",
} as const;

/** Margins as written in gates.yaml. */
export const marginsAsWritten = {
  roc_auc: "0.02",
  pr_auc: "0.02",
  top_decile_lift: "0.20",
} as const;

export const metricLabels: Record<string, string> = {
  roc_auc: "ROC-AUC",
  pr_auc: "PR-AUC",
  top_decile_lift: "Top-decile lift",
};

export const gateCheck = {
  passed: gateCheckJson.passed,
  failures: gateCheckJson.failures,
  scoringModel: gateCheckJson.scoring_model,
  matchesUpstream: gateCheckJson.matches_upstream_metrics_at_six_decimals,
  metrics: gateCheckJson.metrics.map((row) => ({
    metric: row.metric,
    label: metricLabels[row.metric] ?? row.metric,
    value: row.value,
    gate: row.gate,
    passed: row.passed,
    floorAsWritten: floorsAsWritten[row.metric as keyof typeof floorsAsWritten],
    marginAsWritten: marginsAsWritten[row.metric as keyof typeof marginsAsWritten],
  })),
};

export type FairnessGroup = {
  key: string;
  label: string;
  n: number;
  nPositive: number;
  positiveRate: number;
  selectionRate: number;
  truePositiveRate: number;
  falsePositiveRate: number;
  rocAuc: number;
};

function mapGroups(
  field: "gender" | "SeniorCitizen",
  groups: Record<
    string,
    {
      n: number;
      n_positive: number;
      positive_rate: number;
      selection_rate: number;
      true_positive_rate: number;
      false_positive_rate: number;
      roc_auc: number;
    }
  >,
): FairnessGroup[] {
  return Object.entries(groups).map(([key, group]) => ({
    key,
    label: field === "SeniorCitizen" ? `SeniorCitizen ${key}` : key,
    n: group.n,
    nPositive: group.n_positive,
    positiveRate: group.positive_rate,
    selectionRate: group.selection_rate,
    truePositiveRate: group.true_positive_rate,
    falsePositiveRate: group.false_positive_rate,
    rocAuc: group.roc_auc,
  }));
}

function meanAbs(feature: string): number {
  const row = shapJson.mean_abs_shap_by_original_feature.find((item) => item.feature === feature);
  if (!row) {
    throw new Error(`Missing original-field SHAP for ${feature}`);
  }
  return row.mean_abs_shap;
}

export const fairness = {
  hardLabelRule: fairnessJson.hard_label_rule,
  rocAucInput: fairnessJson.roc_auc_input,
  demographicParityDefinition: fairnessJson.demographic_parity_difference,
  equalizedOddsDefinition: fairnessJson.equalized_odds_difference,
  attributesNotInTable: fairnessJson.attributes_not_in_the_table,
  fieldsAreModelInputs: fairnessJson.fields_are_model_inputs,
  overall: {
    n: fairnessJson.overall.n,
    nPositive: fairnessJson.overall.n_positive,
    positiveRate: fairnessJson.overall.positive_rate,
    selectionRate: fairnessJson.overall.selection_rate,
  },
  fields: [
    {
      id: "gender" as const,
      title: "gender",
      demographicParityDifference: fairnessJson.by_field.gender.demographic_parity_difference,
      equalizedOddsDifference: fairnessJson.by_field.gender.equalized_odds_difference,
      meanAbsShap: meanAbs("gender"),
      groups: mapGroups("gender", fairnessJson.by_field.gender.groups),
    },
    {
      id: "SeniorCitizen" as const,
      title: "SeniorCitizen",
      demographicParityDifference:
        fairnessJson.by_field.SeniorCitizen.demographic_parity_difference,
      equalizedOddsDifference: fairnessJson.by_field.SeniorCitizen.equalized_odds_difference,
      meanAbsShap: meanAbs("SeniorCitizen"),
      groups: mapGroups("SeniorCitizen", fairnessJson.by_field.SeniorCitizen.groups),
    },
  ],
};

export type FairnessField = (typeof fairness.fields)[number];

const localSizes: Record<string, { width: number; height: number }> = {
  "5343-SGUBI": { width: 1129, height: 737 },
  "0295-PPHDO": { width: 1165, height: 737 },
  "5787-KXGIY": { width: 1378, height: 737 },
};

const reasonLabels: Record<string, string> = {
  first_held_out_row_with_numeric_TotalCharges:
    "First held-out row with numeric TotalCharges",
  highest_held_out_churn_probability: "Highest held-out probability",
  lowest_held_out_churn_probability: "Lowest held-out probability",
};

export const shap = {
  method: shapJson.method,
  outputUnits: shapJson.output_units,
  nExplained: shapJson.n_explained,
  nEncodedFeatures: shapJson.n_encoded_features,
  baseValue: shapJson.base_value,
  maxAbsReconstructionError: shapJson.max_abs_reconstruction_error,
  globalPlotSpace: shapJson.global_plot_space,
  localPlotSpace: shapJson.local_plot_space,
  aggregation: shapJson.original_feature_aggregation,
  encodedTop: shapJson.mean_abs_shap_encoded.slice(0, 3),
  originalTop: shapJson.mean_abs_shap_by_original_feature.slice(0, 8),
  originalMax: shapJson.mean_abs_shap_by_original_feature[0]?.mean_abs_shap ?? 0,
  groupFields: shapJson.mean_abs_shap_by_original_feature.filter(
    (row) => row.feature === "gender" || row.feature === "SeniorCitizen",
  ),
  customers: shapJson.local_customers.map((customer) => {
    const size = localSizes[customer.customer_id];
    if (!size) {
      throw new Error(`Missing plot size for ${customer.customer_id}`);
    }
    const file = customer.plot.split("/").pop();
    return {
      customerId: customer.customer_id,
      reason: reasonLabels[customer.selection_reason] ?? customer.selection_reason,
      historicalChurn: customer.historical_churn,
      churnProbability: customer.churn_probability,
      decisionFunction: customer.decision_function,
      shapBaseValue: customer.shap_base_value,
      shapSum: customer.shap_sum,
      top: customer.top_original_features.map((feature) => ({
        feature: feature.feature,
        value: feature.value,
        shap: feature.shap,
      })),
      plot: `/figures/shap/${file}`,
      width: size.width,
      height: size.height,
    };
  }),
};

export type LocalCustomer = (typeof shap.customers)[number];

export const drift = {
  reference: driftJson.reference,
  current: driftJson.current,
  note: driftJson.comparison_note,
  trigger: driftJson.psi_review_trigger,
  clipFloor: driftJson.clip_floor,
  requestedNumericBins: driftJson.requested_numeric_bins,
  nTrain: driftJson.n_train,
  nTest: driftJson.n_test,
  nAboveTrigger: driftJson.n_above_trigger,
  features: driftJson.features.map((feature) => ({
    name: feature.name,
    kind: feature.kind,
    psi: feature.psi,
    aboveTrigger: feature.above_trigger,
  })),
};

export const largestDrift = drift.features.reduce((best, feature) =>
  feature.psi >= best.psi ? feature : best,
);
