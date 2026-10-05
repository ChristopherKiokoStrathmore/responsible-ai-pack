import type { Metadata } from "next";
import { FairnessExplorer } from "@/components/FairnessExplorer";
import { Figure } from "@/components/Figure";
import { count, six } from "@/lib/format";
import { fairness } from "@/lib/published";

export const metadata: Metadata = {
  title: "Fairness",
  description:
    "Demographic parity and equalized odds on the pinned IBM telco holdout, copied from reports/fairness.json.",
};

export default function FairnessPage() {
  const rows = fairness.fields.flatMap((field) =>
    field.groups.map((group) => ({ field: field.title, ...group })),
  );

  return (
    <>
      <header className="page-intro wrap">
        <p className="kicker">reports/fairness.json</p>
        <h1>A measurement, not a certificate.</h1>
        <p className="lede">
          Demographic parity difference is{" "}
          {six(
            fairness.fields.find((field) => field.id === "SeniorCitizen")
              ?.demographicParityDifference ?? Number.NaN,
          )}{" "}
          for SeniorCitizen and{" "}
          {six(
            fairness.fields.find((field) => field.id === "gender")?.demographicParityDifference ??
              Number.NaN,
          )}{" "}
          for gender. Both fields are model inputs. This is one split and one cutoff.
        </p>
        <p className="stamp">Not a fairness certificate</p>
        <p>
          <a href="/demo#fairness">Move this cutoff in the demo</a>. The tables below stay on the
          published threshold.
        </p>
      </header>

      <section className="wrap" aria-labelledby="gaps">
        <h2 id="gaps">Published differences</h2>
        <p>{fairness.demographicParityDefinition}</p>
        <p>{fairness.equalizedOddsDefinition}</p>
        <FairnessExplorer fields={fairness.fields} />
        <p className="source">
          Source: reports/fairness.json and the mean absolute SHAP rows in reports/shap_summary.json
        </p>
      </section>

      <section className="wrap" aria-labelledby="rates">
        <h2 id="rates">Group rates</h2>
        <p>
          Overall, {count(fairness.overall.nPositive)} of {count(fairness.overall.n)} held-out rows
          are positive (rate {six(fairness.overall.positiveRate)}). The selection rate at this cutoff
          is {six(fairness.overall.selectionRate)}.
        </p>
        <p>{fairness.hardLabelRule}</p>
        <p>{fairness.rocAucInput}.</p>
        <div className="table-wrap">
          <table>
            <caption>
              {fairness.attributesNotInTable} gender is a model input:{" "}
              {fairness.fieldsAreModelInputs.gender ? "true" : "false"}. SeniorCitizen is a model
              input: {fairness.fieldsAreModelInputs.SeniorCitizen ? "true" : "false"}.
            </caption>
            <thead>
              <tr>
                <th>Group</th>
                <th className="num">n</th>
                <th className="num">Label rate</th>
                <th className="num">Selection rate</th>
                <th className="num">TPR</th>
                <th className="num">FPR</th>
                <th className="num">ROC-AUC</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.label}>
                  <td>{row.label}</td>
                  <td className="num">{count(row.n)}</td>
                  <td className="num">{six(row.positiveRate)}</td>
                  <td className="num">{six(row.selectionRate)}</td>
                  <td className="num">{six(row.truePositiveRate)}</td>
                  <td className="num">{six(row.falsePositiveRate)}</td>
                  <td className="num">{six(row.rocAuc)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <Figure
          src="/figures/fairness_rates.png"
          alt="Selection rate and false positive rate by gender and by SeniorCitizen on the held-out split."
          width={1625}
          height={790}
          caption="Selection rate and false positive rate on the held-out split, from reports/fairness.json. Hard labels use P(Churn=Yes) > 0.5."
          source="assets/fairness_rates.png"
        />
      </section>
    </>
  );
}
