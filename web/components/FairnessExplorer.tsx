"use client";

import { useState } from "react";
import { count, six } from "@/lib/format";
import type { FairnessField, FairnessGroup } from "@/lib/published";

function group(field: FairnessField, label: string): FairnessGroup {
  const found = field.groups.find((item) => item.label === label);
  if (!found) {
    throw new Error(`Missing ${label}`);
  }
  return found;
}

function noteFor(field: FairnessField): string {
  if (field.id === "gender") {
    const female = group(field, "Female");
    const male = group(field, "Male");
    return `Female (n=${count(female.n)}, label rate ${six(female.positiveRate)}) and Male (n=${count(male.n)}, label rate ${six(male.positiveRate)}) are close on selection rate (${six(female.selectionRate)} and ${six(male.selectionRate)}), true positive rate (${six(female.truePositiveRate)} and ${six(male.truePositiveRate)}), false positive rate (${six(female.falsePositiveRate)} and ${six(male.falsePositiveRate)}), and ROC-AUC (${six(female.rocAuc)} and ${six(male.rocAuc)}).`;
  }
  const senior = group(field, "SeniorCitizen 1");
  const other = group(field, "SeniorCitizen 0");
  return `SeniorCitizen 1 (n=${count(senior.n)}, label rate ${six(senior.positiveRate)}) is not close to SeniorCitizen 0 (n=${count(other.n)}, label rate ${six(other.positiveRate)}). Selection rates are ${six(senior.selectionRate)} and ${six(other.selectionRate)}. True positive rates are ${six(senior.truePositiveRate)} and ${six(other.truePositiveRate)}. False positive rates are ${six(senior.falsePositiveRate)} and ${six(other.falsePositiveRate)}. ROC-AUC is ${six(senior.rocAuc)} and ${six(other.rocAuc)}. The higher selection rate sits next to a higher churn rate, and the false-positive rate is higher as well.`;
}

export function FairnessExplorer({ fields }: { fields: FairnessField[] }) {
  const [id, setId] = useState(fields[0]?.id ?? "gender");
  const field = fields.find((item) => item.id === id) ?? fields[0];
  if (!field) return null;

  return (
    <div>
      <div className="choice-grid" role="group" aria-label="Group field">
        {fields.map((item) => (
          <button
            key={item.id}
            type="button"
            className="choice"
            aria-pressed={item.id === field.id}
            data-review={item.id === "SeniorCitizen" ? "true" : undefined}
            onClick={() => setId(item.id)}
          >
            <span className="choice-kicker">{item.title}</span>
            <span className="choice-value">{six(item.demographicParityDifference)}</span>
            <span className="choice-note">Demographic parity difference</span>
          </button>
        ))}
      </div>
      <div className="detail" aria-live="polite">
        <h2>{field.title}</h2>
        <p>
          Equalized odds difference {six(field.equalizedOddsDifference)}. Mean absolute SHAP for
          this original field is {six(field.meanAbsShap)}.
        </p>
        <p>{noteFor(field)}</p>
        {field.id === "SeniorCitizen" ? (
          <p>
            The SeniorCitizen gap is a reason for a person to look at that group before widening
            use. This repo does not fit a second threshold to close the gap.
          </p>
        ) : null}
      </div>
    </div>
  );
}
