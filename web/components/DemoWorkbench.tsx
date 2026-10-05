"use client";

import { DriftLab } from "@/components/DriftLab";
import { ExplanationLab } from "@/components/ExplanationLab";
import { FairnessLab } from "@/components/FairnessLab";

export function DemoWorkbench() {
  return (
    <>
      <section className="wrap" id="fairness" aria-labelledby="demo-fairness">
        <p className="section-label">Fairness</p>
        <div className="tool-head">
          <h2 id="demo-fairness">Move the cutoff.</h2>
        </div>
        <p>
          Hard labels on the held-out rows follow the cutoff. Demographic parity difference and
          equalized odds difference use the same definitions as the Fairlearn report. Gender and
          SeniorCitizen are model inputs.
        </p>
        <FairnessLab />
      </section>

      <section className="wrap" id="explanations" aria-labelledby="demo-explanations">
        <p className="section-label">Explanations</p>
        <div className="tool-head">
          <h2 id="demo-explanations">Turn a contribution off.</h2>
        </div>
        <p>
          Each control is one published local SHAP value on a held-out customer. The probability is
          the logistic of the decision function after that value is removed. It is an explanation
          arithmetic, not a cause of churn.
        </p>
        <ExplanationLab />
      </section>

      <section className="wrap" id="drift" aria-labelledby="demo-drift">
        <p className="section-label">Drift</p>
        <div className="tool-head">
          <h2 id="demo-drift">Shift one batch.</h2>
        </div>
        <p>
          The reference counts stay the training split. The slider moves mass in the current counts,
          then PSI is recomputed. At zero, the figure is the committed baseline. Nothing here is a
          later month of operator data.
        </p>
        <DriftLab />
      </section>
    </>
  );
}
