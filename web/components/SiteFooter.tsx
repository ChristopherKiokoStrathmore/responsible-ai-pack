import { holdout, links } from "@/lib/published";

export function SiteFooter() {
  return (
    <footer className="site-footer wrap">
      <p>
        Independent portfolio project built on public data. The model card names {holdout.author}{" "}
        as the author of the portfolio. This demo uses the same IBM holdout as{" "}
        <a href={links.sibling}>telco-churn-nba-engine</a>.
      </p>
      <ul>
        <li>
          <a href={links.pack}>responsible-ai-pack</a>
        </li>
        <li>
          <a href={links.sibling}>telco-churn-nba-engine</a>
        </li>
        <li>
          <a href={links.siblingCommit}>Pinned commit {holdout.commit.slice(0, 7)}</a>
        </li>
        <li>
          <a href={links.modelCard}>MODEL_CARD.md</a>
        </li>
      </ul>
    </footer>
  );
}
