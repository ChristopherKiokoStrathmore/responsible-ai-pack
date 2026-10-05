"use client";

import { useState } from "react";
import Image from "next/image";
import { six } from "@/lib/format";
import type { LocalCustomer } from "@/lib/published";

export function ExplanationExplorer({ customers }: { customers: LocalCustomer[] }) {
  const [id, setId] = useState(customers[0]?.customerId ?? "");
  const customer = customers.find((item) => item.customerId === id) ?? customers[0];
  if (!customer) return null;

  const max = Math.max(...customer.top.map((feature) => Math.abs(feature.shap)), 0);

  return (
    <div>
      <div className="customer-grid" role="group" aria-label="Held-out customers">
        {customers.map((item) => (
          <button
            key={item.customerId}
            type="button"
            className="customer-btn"
            aria-pressed={item.customerId === customer.customerId}
            onClick={() => setId(item.customerId)}
          >
            <span className="choice-kicker">{item.reason}</span>
            <span className="choice-value">{six(item.churnProbability)}</span>
            <span className="choice-note">
              {item.customerId} · historical Churn {item.historicalChurn}
            </span>
          </button>
        ))}
      </div>

      <div className="detail" aria-live="polite">
        <h2>{customer.customerId}</h2>
        <p>
          P(Churn=Yes) {six(customer.churnProbability)}. Historical Churn {customer.historicalChurn}.
          Decision function {six(customer.decisionFunction)}. SHAP base value{" "}
          {six(customer.shapBaseValue)}. SHAP sum {six(customer.shapSum)}.
        </p>
        <ul className="bar-list">
          {customer.top.map((feature) => {
            const width = max === 0 ? 0 : (Math.abs(feature.shap) / max) * 100;
            const positive = feature.shap > 0;
            return (
              <li key={feature.feature} className="bar-row">
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
                <span className="bar-num">{six(feature.shap)}</span>
              </li>
            );
          })}
        </ul>
        <p className="legend">
          <span>
            <i className="swatch signal" aria-hidden="true" />
            Positive SHAP raises the model&apos;s log-odds of churn.
          </span>
          <span>
            <i className="swatch ink" aria-hidden="true" />
            Negative SHAP lowers them. The bar is not a cause.
          </span>
        </p>
        <figure className="figure">
          <Image
            src={customer.plot}
            alt={`Local TreeSHAP plot for customer ${customer.customerId}. Signed values are summed back to original fields.`}
            width={customer.width}
            height={customer.height}
            sizes="(max-width: 1120px) 100vw, 1120px"
            style={{ width: "100%", height: "auto" }}
          />
          <figcaption>
            Local plot for {customer.customerId}. The plotted bar is not a causal effect.
            <cite>{customer.plot.replace("/figures/shap/", "reports/shap/")}</cite>
          </figcaption>
        </figure>
      </div>
    </div>
  );
}
