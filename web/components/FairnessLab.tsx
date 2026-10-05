"use client";

import { useId, useState } from "react";
import scores from "@/data/holdout_scores.json";
import { fairnessAtCutoff, sameSix, type ScoreTable } from "@/lib/demoMath";
import { count, six } from "@/lib/format";
import { fairness } from "@/lib/published";

const table = scores as ScoreTable & { published_cutoff: number };

function groupLabel(field: "gender" | "SeniorCitizen", key: string): string {
  return field === "SeniorCitizen" ? `SeniorCitizen ${key}` : key;
}

function rateText(value: number | null): string {
  return value === null ? "undefined" : six(value);
}

export function FairnessLab() {
  const cutoffId = useId();
  const [field, setField] = useState<"gender" | "SeniorCitizen">("SeniorCitizen");
  const [cutoff, setCutoff] = useState(table.published_cutoff);
  const result = fairnessAtCutoff(table, cutoff, field);
  const published = fairness.fields.find((item) => item.id === field);
  const atPublished = Math.abs(cutoff - table.published_cutoff) < 1e-9;
  const matchesReport =
    atPublished &&
    published !== undefined &&
    sameSix(result.demographicParityDifference, published.demographicParityDifference) &&
    sameSix(result.equalizedOddsDifference, published.equalizedOddsDifference) &&
    result.groups.every((group) => {
      const expected = published.groups.find((item) => item.key === group.key);
      return (
        expected !== undefined &&
        sameSix(group.selectionRate, expected.selectionRate) &&
        sameSix(group.truePositiveRate, expected.truePositiveRate) &&
        sameSix(group.falsePositiveRate, expected.falsePositiveRate)
      );
    });

  return (
    <div>
      <div className="choice-grid" role="group" aria-label="Group field">
        {fairness.fields.map((item) => {
          const live = fairnessAtCutoff(table, cutoff, item.id);
          return (
            <button
              key={item.id}
              type="button"
              className="choice"
              aria-pressed={item.id === field}
              onClick={() => setField(item.id)}
            >
              <span className="choice-kicker">{item.title}</span>
              <span className="choice-value">{six(live.demographicParityDifference)}</span>
              <span className="choice-note">Demographic parity difference at this cutoff</span>
            </button>
          );
        })}
      </div>

      <div className="slider-block">
        <div className="slider-meta">
          <label htmlFor={cutoffId}>Positive when P(Churn=Yes) is above this cutoff</label>
          <span>{cutoff.toFixed(2)}</span>
        </div>
        <input
          id={cutoffId}
          type="range"
          min={0}
          max={1}
          step={0.01}
          value={cutoff}
          onChange={(event) => setCutoff(Number(event.target.value))}
        />
        <div className="button-row">
          <button type="button" className="reset" onClick={() => setCutoff(table.published_cutoff)}>
            Published cutoff
          </button>
          <button type="button" className="reset" onClick={() => setCutoff(0.3)}>
            0.30
          </button>
          <button type="button" className="reset" onClick={() => setCutoff(0.7)}>
            0.70
          </button>
        </div>
        <p className="source">
          The mark in the write-up is the saved pipeline rule: positive when P(Churn=Yes) &gt;{" "}
          {table.published_cutoff.toFixed(1)}. An exact tie stays negative.
        </p>
      </div>

      <div className="live-grid" aria-live="polite">
        <div className="readout">
          <span className="choice-kicker">Demographic parity difference</span>
          <span className="choice-value">{six(result.demographicParityDifference)}</span>
          <span className="choice-note">Absolute gap between group selection rates</span>
        </div>
        <div className="readout">
          <span className="choice-kicker">Equalized odds difference</span>
          <span className="choice-value">{rateText(result.equalizedOddsDifference)}</span>
          <span className="choice-note">Larger of the true-positive-rate gap and the false-positive-rate gap</span>
        </div>
        <div className="readout">
          <span className="choice-kicker">Selected</span>
          <span className="choice-value">
            {count(result.nSelected)}
            <span className="choice-unit">/{count(result.n)}</span>
          </span>
          <span className="choice-note">Selection rate {six(result.selectionRate)}</span>
        </div>
      </div>

      <div className="demo-columns">
        {result.groups.map((group) => (
          <div className="group-block" key={group.key}>
            <h3>
              {groupLabel(field, group.key)}{" "}
              <span className="quiet">
                n={count(group.n)}, positives {count(group.nPositive)}
              </span>
            </h3>
            {(
              [
                ["Selection rate", group.selectionRate],
                ["True positive rate", group.truePositiveRate],
                ["False positive rate", group.falsePositiveRate],
              ] as const
            ).map(([name, value]) => (
              <div className="metric-line" key={name}>
                <span className="metric-name">{name}</span>
                <span className="rate-track" aria-hidden="true">
                  <span
                    className="rate-bar"
                    style={{ width: `${Math.max(0, Math.min(1, value ?? 0)) * 100}%` }}
                  />
                </span>
                <span className="bar-num">{rateText(value)}</span>
              </div>
            ))}
          </div>
        ))}
      </div>

      <p>
        {matchesReport
          ? "These six-decimal rates match reports/fairness.json. ROC-AUC does not use the cutoff, so it stays in the write-up."
          : atPublished
            ? "Recomputed on the exported holdout rows."
            : `Recomputed on the exported holdout rows. The write-up uses the published cutoff, where ${field} demographic parity difference is ${published ? six(published.demographicParityDifference) : ""}.`}
      </p>
      <p className="source">
        Source: web/data/holdout_scores.json, checked against reports/fairness.json.{" "}
        <a href="/fairness">Fairness write-up</a>
      </p>
    </div>
  );
}
