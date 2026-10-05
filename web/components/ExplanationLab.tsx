"use client";

import { useState } from "react";
import { logistic, sameSix } from "@/lib/demoMath";
import { six } from "@/lib/format";
import { shap, type LocalCustomer } from "@/lib/published";

function residualOf(customer: LocalCustomer): number {
  const shown = customer.top.reduce((sum, feature) => sum + feature.shap, 0);
  return customer.shapSum - shown;
}

export function ExplanationLab() {
  const [id, setId] = useState(shap.customers[0]?.customerId ?? "");
  const [disabled, setDisabled] = useState<string[]>([]);
  const customer = shap.customers.find((item) => item.customerId === id) ?? shap.customers[0];
  if (!customer) return null;

  const residual = residualOf(customer);
  const removed = customer.top
    .filter((feature) => disabled.includes(feature.feature))
    .reduce((sum, feature) => sum + feature.shap, 0);
  const logOdds = customer.decisionFunction - removed;
  const probability = logistic(logOdds);
  const untouched = disabled.length === 0;
  const matchesPublished = untouched && sameSix(probability, customer.churnProbability);
  const max = Math.max(...customer.top.map((feature) => Math.abs(feature.shap)), Math.abs(residual), 0);

  function selectCustomer(nextId: string) {
    setId(nextId);
    setDisabled([]);
  }

  function toggle(feature: string) {
    setDisabled((current) =>
      current.includes(feature) ? current.filter((item) => item !== feature) : [...current, feature],
    );
  }

  return (
    <div>
      <div className="customer-grid" role="group" aria-label="Held-out customers">
        {shap.customers.map((item) => (
          <button
            key={item.customerId}
            type="button"
            className="customer-btn"
            aria-pressed={item.customerId === customer.customerId}
            onClick={() => selectCustomer(item.customerId)}
          >
            <span className="choice-kicker">{item.reason}</span>
            <span className="choice-value">{six(item.churnProbability)}</span>
            <span className="choice-note">
              {item.customerId} · historical Churn {item.historicalChurn}
            </span>
          </button>
        ))}
      </div>

      <div className="live-grid" aria-live="polite">
        <div className="readout">
          <span className="choice-kicker">P(Churn=Yes) from the contributions left on</span>
          <span className="choice-value">{six(probability)}</span>
          <span className="choice-note">
            Published probability {six(customer.churnProbability)}. Difference{" "}
            {six(probability - customer.churnProbability)}
          </span>
        </div>
        <div className="readout">
          <span className="choice-kicker">Decision function</span>
          <span className="choice-value">{six(logOdds)}</span>
          <span className="choice-note">
            Published {six(customer.decisionFunction)}. Base value {six(customer.shapBaseValue)}
          </span>
        </div>
        <div className="readout">
          <span className="choice-kicker">Contributions removed</span>
          <span className="choice-value">{six(removed)}</span>
          <span className="choice-note">
            {untouched ? "Every published contribution is included." : "The model was not re-scored."}
          </span>
        </div>
      </div>

      <div className="button-row">
        <button type="button" className="reset" onClick={() => setDisabled([])}>
          Restore contributions
        </button>
      </div>

      <ul className="toggle-list">
        {customer.top.map((feature) => {
          const on = !disabled.includes(feature.feature);
          const width = max === 0 ? 0 : (Math.abs(feature.shap) / max) * 100;
          const positive = feature.shap > 0;
          return (
            <li key={feature.feature}>
              <button
                type="button"
                className="toggle"
                aria-pressed={on}
                onClick={() => toggle(feature.feature)}
              >
                <span className="switch" aria-hidden="true" />
                <span>
                  <span className="bar-label">
                    {feature.feature} = {feature.value}
                  </span>
                  <span className="bar-track" aria-hidden="true">
                    {positive ? (
                      <span className="bar-pos" style={{ width: `${width}%`, gridColumn: "2" }} />
                    ) : (
                      <span className="bar-neg" style={{ width: `${width}%`, gridColumn: "1" }} />
                    )}
                  </span>
                </span>
                <span className="bar-num">{six(feature.shap)}</span>
              </button>
            </li>
          );
        })}
        <li className="bar-row kept-row">
          <span className="bar-label">Other fields, kept</span>
          <span className="bar-track" aria-hidden="true">
            {residual > 0 ? (
              <span
                className="bar-pos"
                style={{
                  width: `${max === 0 ? 0 : (Math.abs(residual) / max) * 100}%`,
                  gridColumn: "2",
                }}
              />
            ) : (
              <span
                className="bar-neg"
                style={{
                  width: `${max === 0 ? 0 : (Math.abs(residual) / max) * 100}%`,
                  gridColumn: "1",
                }}
              />
            )}
          </span>
          <span className="bar-num">{six(residual)}</span>
        </li>
      </ul>
      <p className="legend">
        <span>
          <i className="swatch signal" aria-hidden="true" />
          Positive SHAP raises the model&apos;s log-odds of churn.
        </span>
        <span>
          <i className="swatch ink" aria-hidden="true" />
          Negative SHAP lowers them. A pressed control keeps that contribution.
        </span>
      </p>
      <p>
        {matchesPublished
          ? "With every contribution on, the logistic of the published decision function matches the published probability at six decimals."
          : "Turning a contribution off subtracts that published SHAP value from the decision function. The customer row is not edited, and the model is not run again."}
      </p>
      <p className="source">
        Source: reports/shap_summary.json. <a href="/explanations">Explanations write-up</a>
      </p>
    </div>
  );
}
