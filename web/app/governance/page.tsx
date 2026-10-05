import type { Metadata } from "next";
import { Checklist } from "@/components/Checklist";
import { checklist, checklistIntro } from "@/lib/checklist";
import { count, six } from "@/lib/format";
import { drift, gateCheck, links } from "@/lib/published";

export const metadata: Metadata = {
  title: "Governance",
  description:
    "NIST AI RMF checklist highlights and the held-out metric floors from gates.yaml and reports/gate_check.json.",
};

export default function GovernancePage() {
  return (
    <>
      <header className="page-intro wrap">
        <p className="kicker">GOVERNANCE_CHECKLIST.md</p>
        <h1>Govern, map, measure, manage.</h1>
        <p className="lede">{checklistIntro.frame}</p>
        <p className="disclaimer">{checklistIntro.act}</p>
      </header>

      <section className="wrap" aria-labelledby="gates">
        <h2 id="gates">Metric floors</h2>
        <p>
          <code>minimum = floor_to_decimals(recomputed_value - margin, 2)</code>. The margin is there
          so six-decimal noise does not fail CI, and a broken artifact or a real drop does. These
          floors are not confidence intervals. Fairness gaps are not floors.
        </p>
        <div className="table-wrap">
          <table>
            <caption>
              gates.yaml writes the floors as{" "}
              {gateCheck.metrics.map((row) => row.floorAsWritten).join(", ")}. gate_check.json stores
              them at six decimals. passed: {gateCheck.passed ? "true" : "false"}. failures:{" "}
              {gateCheck.failures.length === 0 ? "none" : gateCheck.failures.join(", ")}.
            </caption>
            <thead>
              <tr>
                <th>Metric</th>
                <th className="num">Recomputed</th>
                <th className="num">Margin</th>
                <th className="num">Floor in the check</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              {gateCheck.metrics.map((row) => (
                <tr key={row.metric}>
                  <td>{row.label}</td>
                  <td className="num">{six(row.value)}</td>
                  <td className="num">{row.marginAsWritten}</td>
                  <td className="num">{six(row.gate)}</td>
                  <td>{row.passed ? "passed" : "failed"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p>
          Drift is watched, not gated. Review trigger {six(drift.trigger)}. n_above_trigger{" "}
          {count(drift.nAboveTrigger)}. A feature at or above the trigger is a reason to read the
          batch. It does not by itself fail gates.yaml.
        </p>
        <p>
          <a href={links.gates}>gates.yaml</a> · <a href={links.monitoring}>MONITORING.md</a> ·{" "}
          <a href={links.runbook}>INCIDENT_RUNBOOK.md</a>
        </p>
      </section>

      <div className="wrap">
        <p className="section-label">Checklist</p>
        <Checklist items={checklist} />
        <p className="source">
          Source: <a href={links.checklist}>GOVERNANCE_CHECKLIST.md</a>
        </p>
      </div>
    </>
  );
}
