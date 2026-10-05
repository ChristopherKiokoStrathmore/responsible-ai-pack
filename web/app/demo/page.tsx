import type { Metadata } from "next";
import { DemoWorkbench } from "@/components/DemoWorkbench";

export const metadata: Metadata = {
  title: "Demo",
  description:
    "Move the fairness cutoff, local TreeSHAP contributions, and a drift bin on the public IBM telco holdout.",
};

export default function DemoPage() {
  return (
    <>
      <header className="page-intro wrap">
        <p className="kicker">Interactive holdout</p>
        <h1>Move a control. Read the same definitions.</h1>
        <p className="lede">
          Fairness rates, local TreeSHAP contributions, and PSI are loaded from the committed
          holdout. A control recomputes those definitions. Reset puts the published figures back.
        </p>
        <p className="disclaimer">
          This is the public IBM telco sample. A gap on a cutoff you chose is still one split, and
          it is still not a fairness certificate. Subtracting a SHAP value does not rescore the
          model and does not cause a customer to stay. A PSI change here is a shift applied to the
          published bin counts.
        </p>
        <ul className="link-row">
          <li>
            <a href="/">Write-up</a>
          </li>
          <li>
            <a href="/fairness">Fairness article</a>
          </li>
          <li>
            <a href="/explanations">Explanations article</a>
          </li>
          <li>
            <a href="/governance">Governance</a>
          </li>
        </ul>
        <noscript>
          <p className="noscript-note">
            With JavaScript off, the controls stay on the published holdout. The articles linked
            above list those figures in full.
          </p>
        </noscript>
      </header>
      <DemoWorkbench />
    </>
  );
}
