"use client";

import { useId, useState } from "react";
import driftJson from "@/data/drift_psi.json";
import { populationStabilityIndex, sameSix, shiftCounts } from "@/lib/demoMath";
import { six } from "@/lib/format";

type DriftFeature = {
  name: string;
  kind: string;
  psi: number;
  above_trigger: boolean;
  edges?: number[];
  levels?: string[];
  reference_counts: number[];
  current_counts: number[];
  missing_bin?: string;
};

const features = driftJson.features as DriftFeature[];

const defaultFocus: Record<string, number> = {
  tenure: 0,
  MonthlyCharges: 0,
  TotalCharges: 0,
  Contract: 0,
  InternetService: 1,
  PaymentMethod: 2,
  gender: 0,
  SeniorCitizen: 1,
};

function edgeText(value: number): string {
  return Number.isInteger(value) ? String(value) : String(value);
}

function labelsFor(feature: DriftFeature): string[] {
  if (feature.kind === "categorical" && feature.levels) return feature.levels;
  const edges = feature.edges ?? [];
  const bins = feature.current_counts.length - 1;
  const labels: string[] = [];
  for (let i = 0; i < bins; i += 1) {
    labels.push(`${edgeText(edges[i] ?? 0)}–${edgeText(edges[i + 1] ?? 0)}`);
  }
  labels.push("missing");
  return labels;
}

export function DriftLab() {
  const amountId = useId();
  const focusId = useId();
  const opening = features.find((feature) => feature.name === "Contract") ?? features[0];
  const [name, setName] = useState(opening.name);
  const [focus, setFocus] = useState(defaultFocus[opening.name] ?? 0);
  const [amount, setAmount] = useState(0);
  const feature = features.find((item) => item.name === name) ?? opening;
  const labels = labelsFor(feature);
  const safeFocus = focus >= 0 && focus < feature.current_counts.length ? focus : 0;
  const current = shiftCounts(feature.current_counts, safeFocus, amount);
  const psi = populationStabilityIndex(feature.reference_counts, current, driftJson.clip_floor);
  const above = psi >= driftJson.psi_review_trigger;
  const matchesReport = amount <= 0 && sameSix(psi, feature.psi);
  const referenceTotal = feature.reference_counts.reduce((sum, value) => sum + value, 0);
  const currentTotal = current.reduce((sum, value) => sum + value, 0);

  function selectFeature(next: string) {
    setName(next);
    setFocus(defaultFocus[next] ?? 0);
    setAmount(0);
  }

  return (
    <div>
      <div className="filters" role="group" aria-label="Feature">
        {features.map((item) => (
          <button
            key={item.name}
            type="button"
            className="filter"
            aria-pressed={item.name === feature.name}
            onClick={() => selectFeature(item.name)}
          >
            {item.name}
          </button>
        ))}
      </div>

      <div className="demo-columns">
        <div className="slider-block">
          <label htmlFor={focusId}>Move the current batch toward</label>
          <select
            id={focusId}
            className="bin-select"
            value={String(safeFocus)}
            onChange={(event) => setFocus(Number(event.target.value))}
          >
            {labels.map((label, index) => (
              <option value={index} key={`${label}-${index}`}>
                {label}
              </option>
            ))}
          </select>
          <div className="slider-meta">
            <label htmlFor={amountId}>Portion of the current batch moved into that bin</label>
            <span>{Math.round(amount * 100)}%</span>
          </div>
          <input
            id={amountId}
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={amount}
            onChange={(event) => setAmount(Number(event.target.value))}
          />
          <div className="button-row">
            <button type="button" className="reset" onClick={() => setAmount(0)}>
              Held-out mix
            </button>
            <button type="button" className="reset" onClick={() => setAmount(1)}>
              Entire batch in that bin
            </button>
          </div>
        </div>
        <div className="readout" aria-live="polite">
          <span className="choice-kicker">{feature.name} PSI</span>
          <span className={above ? "choice-value alert" : "choice-value"}>{six(psi)}</span>
          <span className="choice-note">
            Published PSI {six(feature.psi)}. Review trigger {six(driftJson.psi_review_trigger)}. above_trigger:{" "}
            {above ? "true" : "false"}.
          </span>
          <span className="psi-track meter" aria-hidden="true">
            <span
              className={above ? "psi-bar alert-bar" : "psi-bar"}
              style={{ width: `${Math.min(100, (psi / driftJson.psi_review_trigger) * 100)}%` }}
            />
          </span>
        </div>
      </div>

      <ul className="bin-list">
        {labels.map((label, index) => {
          const referenceShare = referenceTotal === 0 ? 0 : feature.reference_counts[index] / referenceTotal;
          const currentShare = currentTotal === 0 ? 0 : current[index] / currentTotal;
          return (
            <li className="metric-line" key={`${label}-${index}`}>
              <span className="metric-name">{label}</span>
              <span className="share-track" aria-hidden="true">
                <span className="share-ref" style={{ width: `${referenceShare * 100}%` }} />
                <span className="share-cur" style={{ width: `${currentShare * 100}%` }} />
              </span>
              <span className="bar-num">{six(currentShare)}</span>
            </li>
          );
        })}
      </ul>
      <p className="legend">
        <span>
          <i className="swatch ink" aria-hidden="true" />
          Training-split share, the reference.
        </span>
        <span>
          <i className="swatch signal" aria-hidden="true" />
          Current-batch share after the shift. The number is that share.
        </span>
      </p>
      <p>
        {matchesReport
          ? "PSI matches reports/drift_psi.json. The red mark on the meter is the review trigger."
          : above
            ? "This shift is at or above the review trigger. That is a reason to read the batch. It does not fail gates.yaml. The other features stay at their published PSI."
            : "PSI is recomputed with the same clip-and-renormalize formula as scripts/run_drift.py. The training counts stay the reference."}
      </p>
      <p className="source">
        Source: reports/drift_psi.json. {feature.kind}.{" "}
        {feature.missing_bin ? `${feature.missing_bin}. ` : null}
        <a href="/#drift">Drift write-up</a>
      </p>
    </div>
  );
}
