import Link from "next/link";

export default function NotFound() {
  return (
    <header className="page-intro wrap">
      <p className="kicker">Missing page</p>
      <h1>This page is not in the pack.</h1>
      <p className="lede">
        The demo has four readings: scope, fairness, explanations, and governance.
      </p>
      <p>
        <Link href="/">Back to the holdout</Link>
      </p>
    </header>
  );
}
