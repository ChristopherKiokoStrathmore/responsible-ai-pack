export type NistFunction = "Govern" | "Map" | "Measure" | "Manage";

export type ChecklistItem = {
  id: string;
  fn: NistFunction;
  done: boolean;
  text: string;
};

/**
 * Transcribed from GOVERNANCE_CHECKLIST.md.
 * Open items are the unchecked boxes in that file.
 */
export const checklistIntro = {
  frame:
    "Checklist for the churn model in this repo, mapped to the NIST AI Risk Management Framework functions Govern, Map, Measure, and Manage. Independent portfolio project built on public data.",
  act: "If a later project used personal data of people in Kenya, the statute to read is the Kenya Data Protection Act 2019. This page names that Act. It does not interpret it, and it does not claim compliance.",
};

export const checklist: ChecklistItem[] = [
  {
    id: "govern-card",
    fn: "Govern",
    done: true,
    text: "The model card names the artifact, the commit, and the person whose portfolio this is.",
  },
  {
    id: "govern-readme",
    fn: "Govern",
    done: true,
    text: "The README states the data and scope and that the pack uses the public IBM sample only.",
  },
  {
    id: "govern-act",
    fn: "Govern",
    done: true,
    text: "Kenya Data Protection Act 2019 is named, with no section numbers and no compliance claim.",
  },
  {
    id: "govern-owner",
    fn: "Govern",
    done: false,
    text: "A real deployment still needs an accountable owner inside the organisation that would act on a score. This repo cannot appoint one.",
  },
  {
    id: "map-use",
    fn: "Map",
    done: true,
    text: "Intended use and out-of-scope use are written in MODEL_CARD.md and MODEL_CARD_MULTIHEAD.md.",
  },
  {
    id: "map-table",
    fn: "Map",
    done: true,
    text: "The churn training table is identified by the upstream metrics file and by the CSV SHA-256 in upstream.lock.json.",
  },
  {
    id: "map-groups",
    fn: "Map",
    done: true,
    text: "gender and SeniorCitizen are documented as model inputs, and as the only group fields this pack measures.",
  },
  {
    id: "map-multihead",
    fn: "Map",
    done: true,
    text: "The multi-head card says when the source repo does not document data or quality.",
  },
  {
    id: "measure-metrics",
    fn: "Measure",
    done: true,
    text: "Held-out ROC-AUC, PR-AUC, and top-decile lift are recomputed in reports/metrics_recomputed.json from the saved models.",
  },
  {
    id: "measure-shap",
    fn: "Measure",
    done: true,
    text: "TreeSHAP global and local plots are in reports/shap/, with numbers in reports/shap_summary.json.",
  },
  {
    id: "measure-fairness",
    fn: "Measure",
    done: true,
    text: "Fairlearn selection rate, true positive rate, false positive rate, and ROC-AUC by gender and SeniorCitizen are in reports/fairness.json, with demographic parity and equalized odds differences.",
  },
  {
    id: "measure-psi",
    fn: "Measure",
    done: true,
    text: "PSI on the pinned split is in reports/drift_psi.json. That file says the split is not a time comparison.",
  },
  {
    id: "manage-gates",
    fn: "Manage",
    done: true,
    text: "gates.yaml holds floors under the recomputed churn metrics. scripts/check_gates.py recomputes them and fails if one is below its floor. GitHub Actions runs that script.",
  },
  {
    id: "manage-monitoring",
    fn: "Manage",
    done: true,
    text: "MONITORING.md says what a later batch would compare, and what this repo does not watch.",
  },
  {
    id: "manage-runbook",
    fn: "Manage",
    done: true,
    text: "INCIDENT_RUNBOOK.md covers detection, triage, rollback, communication, and a postmortem when a gated metric is below its floor.",
  },
  {
    id: "manage-fairness",
    fn: "Manage",
    done: false,
    text: "Fairness gaps are reported and are not a CI floor. A disparity budget needs an owner this repo does not have.",
  },
  {
    id: "manage-multihead",
    fn: "Manage",
    done: false,
    text: "The multi-head emergency-recall smoke floor stays in that other repo. This pack does not gate it, because the weights and gold labels are not there.",
  },
];

export const nistFunctions: NistFunction[] = ["Govern", "Map", "Measure", "Manage"];
