"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Scope" },
  { href: "/fairness", label: "Fairness" },
  { href: "/explanations", label: "Explanations" },
  { href: "/governance", label: "Governance" },
];

export function SiteHeader() {
  const pathname = usePathname();

  return (
    <header className="mast wrap">
      <Link href="/" className="brand">
        <span className="brand-mark" aria-hidden="true" />
        <span>
          <strong>Responsible AI pack</strong>
          <em>IBM telco holdout</em>
        </span>
      </Link>
      <nav aria-label="Pages">
        <ul className="nav">
          {LINKS.map((link) => {
            const current = link.href === "/" ? pathname === "/" : pathname.startsWith(link.href);
            return (
              <li key={link.href}>
                <Link href={link.href} aria-current={current ? "page" : undefined}>
                  {link.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </header>
  );
}
