import type { Metadata } from "next";
import { ExplanationExplorer } from "@/components/ExplanationExplorer";
import { Figure } from "@/components/Figure";
import { count, six } from "@/lib/format";
import { shap } from "@/lib/published";

export const metadata: Metadata = {
  title: "Explanations",
  description:
    "TreeSHAP global and local figures for the pinned gradient-boosting churn model, from reports/shap_summary.json.",
};

export default function ExplanationsPage() {
  return (
    <>
      <header className="page-intro wrap">
        <p className="kicker">reports/shap_summary.json</p>
        <h1>What the model uses, not why someone left.</h1>
        <p className="lede">
          {shap.method}. Output units: {shap.outputUnits}. On {count(shap.nExplained)} held-out rows
          the values plus the base value {six(shap.baseValue)} rebuild decision_function with max
          absolute error {six(shap.maxAbsReconstructionError)}.
        </p>
      </header>

      <section className="wrap" aria-labelledby="global">
        <h2 id="global">Global</h2>
        <p>
          {shap.globalPlotSpace}. {count(shap.nEncodedFeatures)} encoded columns. {shap.aggregation}
        </p>
        <div className="table-wrap">
          <table>
            <caption>Largest mean absolute SHAP among encoded columns.</caption>
            <thead>
              <tr>
                <th>Encoded column</th>
                <th className="num">Mean absolute SHAP</th>
              </tr>
            </thead>
            <tbody>
              {shap.encodedTop.map((row) => (
                <tr key={row.feature}>
                  <td>{row.feature}</td>
                  <td className="num">{six(row.mean_abs_shap)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="table-wrap">
          <table>
            <caption>
              Original fields. The scale of the ink bars is the largest value in this table,{" "}
              {shap.originalTop[0]?.feature} at {six(shap.originalMax)}.
            </caption>
            <thead>
              <tr>
                <th>Original field</th>
                <th>Mean absolute SHAP</th>
                <th className="num">Value</th>
              </tr>
            </thead>
            <tbody>
              {shap.originalTop.map((row) => (
                <tr key={row.feature}>
                  <td>{row.feature}</td>
                  <td>
                    <span className="psi-track" aria-hidden="true">
                      <span
                        className="psi-bar"
                        style={{ width: `${(row.mean_abs_shap / shap.originalMax) * 100}%` }}
                      />
                    </span>
                  </td>
                  <td className="num">{six(row.mean_abs_shap)}</td>
                </tr>
              ))}
              {shap.groupFields.map((row) => (
                <tr key={row.feature}>
                  <td>{row.feature}</td>
                  <td>
                    <span className="psi-track" aria-hidden="true">
                      <span
                        className="psi-bar"
                        style={{ width: `${(row.mean_abs_shap / shap.originalMax) * 100}%` }}
                      />
                    </span>
                  </td>
                  <td className="num">{six(row.mean_abs_shap)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p>
          gender and SeniorCitizen are listed after the eight largest original fields so their mean
          absolute SHAP can be read on the same scale. They are not a second measurement.
        </p>
        <Figure
          src="/figures/shap/global_bar.png"
          alt="Mean absolute SHAP by encoded column. The longest bar is cat__Contract_Month-to-month."
          width={1203}
          height={799}
          caption="Mean absolute SHAP by encoded column."
          source="reports/shap/global_bar.png"
        />
        <Figure
          src="/figures/shap/global_summary.png"
          alt="Held-out TreeSHAP summary in the encoded column space the booster sees."
          width={1189}
          height={687}
          caption="Held-out TreeSHAP summary."
          source="reports/shap/global_summary.png"
        />
      </section>

      <section className="wrap" aria-labelledby="local">
        <h2 id="local">Three held-out customers</h2>
        <p>{shap.localPlotSpace}</p>
        <ExplanationExplorer customers={shap.customers} />
        <noscript>
          <div className="noscript-note">
            {shap.customers.map((customer) => (
              <figure key={customer.customerId} className="figure">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={customer.plot} alt={`Local TreeSHAP plot for ${customer.customerId}`} />
                <figcaption>
                  {customer.customerId} · P(Churn=Yes) {six(customer.churnProbability)} · historical
                  Churn {customer.historicalChurn}
                </figcaption>
              </figure>
            ))}
          </div>
        </noscript>
        <div className="table-wrap">
          <table>
            <caption>The same three rows, always listed. Plots above follow the selection.</caption>
            <thead>
              <tr>
                <th>Customer</th>
                <th>Why this row</th>
                <th>Historical Churn</th>
                <th className="num">P(Churn=Yes)</th>
                <th>Largest original field</th>
              </tr>
            </thead>
            <tbody>
              {shap.customers.map((customer) => {
                const largest = customer.top[0];
                return (
                  <tr key={customer.customerId}>
                    <td>{customer.customerId}</td>
                    <td>{customer.reason}</td>
                    <td>{customer.historicalChurn}</td>
                    <td className="num">{six(customer.churnProbability)}</td>
                    <td>
                      {largest
                        ? `${largest.feature} = ${largest.value}, ${six(largest.shap)}`
                        : ""}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}
