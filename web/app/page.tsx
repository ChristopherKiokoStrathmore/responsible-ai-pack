import { DriftChart } from "@/components/DriftChart";
import { Figure } from "@/components/Figure";
import { count, six } from "@/lib/format";
import { drift, fairness, gateCheck, holdout, largestDrift, links, models } from "@/lib/published";

export default function HomePage() {
  const scoring = models.find((model) => model.scoring);

  return (
    <>
      <header className="hero wrap">
        <p className="kicker">Same IBM holdout as telco-churn-nba-engine</p>
        <h1>
          Read the score <em>before anyone acts.</em>
        </h1>
        <p className="lede">
          This is a reading of the gradient-boosting churn model pinned from telco-churn-nba-engine.
          The pack does not train a replacement. Nothing below was measured again for this page.
        </p>
        <div className="disclaimer">
          <p>
            Independent portfolio project built on public data. The holdout is{" "}
            <code>{holdout.splitFunction}</code>, seed {count(holdout.seed)}, test size{" "}
            {six(holdout.testSize)}, stratified on {holdout.stratify}: {count(holdout.nTrain)}{" "}
            training rows and {count(holdout.nTest)} test rows. The table is the public IBM Telco
            Customer Churn sample, {count(holdout.datasetRows)} rows, churn rate{" "}
            {six(holdout.datasetChurnRate)}. It is not an operator extract and it is not Kenyan
            network performance.
          </p>
          <p>
            A group gap on this page is a measurement, not a certificate. SHAP describes the model.
            It is not a cause of churn.
          </p>
        </div>
        <ul className="link-row">
          <li>
            <a href={links.pack}>responsible-ai-pack</a>
          </li>
          <li>
            <a href={links.sibling}>telco-churn-nba-engine</a>
          </li>
          <li>
            <a href={links.siblingCommit}>Commit {holdout.commit.slice(0, 12)}</a>
          </li>
        </ul>
      </header>

      <div className="wrap">
        <Figure
          src="/figures/hero.png"
          alt="Poster: a churn score flags senior customers more often. The pack explains scores, measures group rates, checks drift, and gates the held-out metrics."
          width={1600}
          height={800}
          priority
          caption="A churn score flags senior customers more often. This pack explains scores, measures group rates, checks drift, and gates the held-out metrics."
          source="assets/hero.png"
        />
      </div>

      <section className="wrap" aria-labelledby="findings">
        <p className="section-label" id="findings">
          Findings at a glance
        </p>
        <h2>Two published gaps, one split, one cutoff.</h2>
        <div className="stat-grid">
          {fairness.fields.map((field) => (
            <a className="stat" href="/fairness" key={field.id}>
              <span className="stat-kicker">{field.title}</span>
              <span className="stat-value">{six(field.demographicParityDifference)}</span>
              <span className="stat-note">
                {field.id === "SeniorCitizen"
                  ? "Demographic parity difference. Flagged for review. Not a CI floor."
                  : "Demographic parity difference. The groups are close."}
              </span>
            </a>
          ))}
        </div>
        <p>
          The README flags these two differences for review. They are not a CI floor, and they are
          not a fairness certificate.
        </p>
        <p className="source">Source: reports/fairness.json</p>
      </section>

      <section className="wrap" aria-labelledby="scope">
        <p className="section-label" id="scope">
          Model card
        </p>
        <h2>What the pinned model is for.</h2>
        <div className="split">
          <div>
            <h3>Intended use</h3>
            <ul>
              <li>
                Rank customers in the IBM telco sample by the model&apos;s estimate of P(Churn=Yes).
              </li>
              <li>Show the TreeSHAP contributions behind one score so a person can read the model.</li>
              <li>The intended user of this pack is someone reviewing that public model.</li>
            </ul>
          </div>
          <div>
            <h3>Out of scope</h3>
            <ul>
              <li>Any live operator&apos;s customers, including customers in Kenya.</li>
              <li>Deciding credit, disconnection, eligibility, or a penalty.</li>
              <li>Sending an offer or placing a call with no person in the loop.</li>
              <li>Treating a SHAP value as a cause of churn.</li>
              <li>Treating logistic regression or the add-on models as this scoring model.</li>
              <li>Claiming a fairness pass.</li>
            </ul>
          </div>
        </div>
        <p className="source">Source: MODEL_CARD.md</p>
      </section>

      <section className="wrap" aria-labelledby="metrics">
        <p className="section-label" id="metrics">
          Held-out metrics
        </p>
        <h2>Gradient boosting stays the scoring file.</h2>
        <p>
          Recomputed with the saved pipelines on the {count(holdout.nTest)} held-out rows.{" "}
          {scoring
            ? `Top-decile k is ${count(scoring.topDecileK)}. The test base rate is ${six(scoring.baseRate)}.`
            : null}{" "}
          matches_upstream_metrics_at_six_decimals: {holdout.matchesUpstream ? "true" : "false"}.
        </p>
        <div className="table-wrap">
          <table>
            <caption>
              Logistic regression is higher on ROC-AUC. Gradient boosting is higher on PR-AUC and on
              top-decile lift. The scoring artifact remains gradient boosting.
            </caption>
            <thead>
              <tr>
                <th>Model</th>
                <th>Role</th>
                <th className="num">ROC-AUC</th>
                <th className="num">PR-AUC</th>
                <th className="num">Top-decile lift</th>
              </tr>
            </thead>
            <tbody>
              {models.map((model) => (
                <tr key={model.id} className={model.scoring ? "scoring" : undefined}>
                  <td>{model.label}</td>
                  <td>{model.scoring ? "Scoring model" : "Comparison"}</td>
                  <td className="num">{six(model.rocAuc)}</td>
                  <td className="num">{six(model.prAuc)}</td>
                  <td className="num">{six(model.topDecileLift)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p>
          CI floors in gates.yaml are ROC-AUC {gateCheck.metrics[0]?.floorAsWritten}, PR-AUC{" "}
          {gateCheck.metrics[1]?.floorAsWritten}, and top-decile lift{" "}
          {gateCheck.metrics[2]?.floorAsWritten}. The last gate check passed:{" "}
          {gateCheck.passed ? "true" : "false"}.
        </p>
        <Figure
          src="/figures/model_metrics.png"
          alt="Held-out ROC-AUC, PR-AUC, and top-decile lift for the dummy prior, logistic regression, and gradient boosting. Gold lines mark the gates.yaml floors."
          width={1652}
          height={753}
          caption="Held-out ROC-AUC, PR-AUC, and top-decile lift for the dummy prior, logistic regression, and gradient boosting. The gold lines are the floors in gates.yaml. Deep green is the scoring model."
          source="assets/model_metrics.png · reports/metrics_recomputed.json"
        />
      </section>

      <section className="wrap" id="drift" aria-labelledby="drift-heading">
        <p className="section-label" id="drift-heading">
          Drift baseline
        </p>
        <h2>PSI on one split is not a later month.</h2>
        <p>{drift.note}</p>
        <p>
          Reference: {drift.reference}. Current: {drift.current}. n_train {count(drift.nTrain)},
          n_test {count(drift.nTest)}. Review trigger {six(drift.trigger)}. n_above_trigger{" "}
          {count(drift.nAboveTrigger)}. The largest value is {largestDrift.name} at{" "}
          {six(largestDrift.psi)}. Numeric columns ask for {count(drift.requestedNumericBins)}{" "}
          quantile bins. Shares below the clip floor {six(drift.clipFloor)} are raised to that floor.
        </p>
        <DriftChart features={drift.features} trigger={drift.trigger} />
        <Figure
          src="/figures/drift_psi.png"
          alt="PSI by feature between the training split and the held-out split. A gold line marks the review trigger."
          width={1652}
          height={780}
          caption="Each bar is a feature PSI from reports/drift_psi.json. The gold line is the review trigger."
          source="assets/drift_psi.png"
        />
      </section>

      <section className="wrap" aria-labelledby="limits">
        <p className="section-label" id="limits">
          Limitations
        </p>
        <h2>What this holdout cannot say.</h2>
        <ul className="plain-list">
          <li>
            The table is IBM&apos;s public US sample, {count(holdout.datasetRows)} rows. These
            metrics are not local performance for any network.
          </li>
          <li>
            gender and SeniorCitizen are inputs. The file has no race, ethnicity, region, language,
            or disability column.
          </li>
          <li>There is one stratified holdout. The model card does not report a confidence interval.</li>
          <li>Hard-label rates use P(Churn=Yes) &gt; 0.5. They are not the upstream policy cutoffs.</li>
          <li>Low PSI here compares two halves of one random split.</li>
        </ul>
      </section>

      <section className="wrap" aria-labelledby="index">
        <p className="section-label" id="index">
          In this demo
        </p>
        <h2>Continue the reading.</h2>
        <ul className="index-list">
          <li>
            <a href="/fairness">
              <span className="index-no">01</span>
              <span>
                <strong>Fairness</strong>
                Selection rate, true positive rate, false positive rate, and ROC-AUC by gender and
                SeniorCitizen.
              </span>
            </a>
          </li>
          <li>
            <a href="/explanations">
              <span className="index-no">02</span>
              <span>
                <strong>Explanations</strong>
                TreeSHAP on the held-out rows, including the three local customer plots.
              </span>
            </a>
          </li>
          <li>
            <a href="/governance">
              <span className="index-no">03</span>
              <span>
                <strong>Governance</strong>
                NIST checklist, the three metric floors, and the items this repo leaves open.
              </span>
            </a>
          </li>
        </ul>
        <details>
          <summary>Provenance</summary>
          <p>
            Upstream commit <span className="hash">{holdout.commit}</span>
          </p>
          <p>
            Scoring artifact SHA-256 <span className="hash">{holdout.scoringModelSha256}</span>
          </p>
          <p>
            CSV SHA-256 <span className="hash">{holdout.datasetSha256}</span>
          </p>
          <p>
            Example customer {holdout.exampleCustomerId}. Scoring model {holdout.scoringModel}.
            Positive label {holdout.positiveLabel}. gender is an input:{" "}
            {holdout.inputsIncludeGender ? "true" : "false"}. SeniorCitizen is an input:{" "}
            {holdout.inputsIncludeSeniorCitizen ? "true" : "false"}.
          </p>
        </details>
      </section>
    </>
  );
}
