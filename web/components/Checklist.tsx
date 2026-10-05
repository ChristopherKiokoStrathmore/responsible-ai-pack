"use client";

import { useState } from "react";
import { nistFunctions, type ChecklistItem, type NistFunction } from "@/lib/checklist";

type Filter = "All" | "Open" | NistFunction;

const FILTERS: Filter[] = ["All", "Open", ...nistFunctions];

export function Checklist({ items }: { items: ChecklistItem[] }) {
  const [filter, setFilter] = useState<Filter>("All");
  const openCount = items.filter((item) => !item.done).length;
  const visible = items.filter((item) => {
    if (filter === "All") return true;
    if (filter === "Open") return !item.done;
    return item.fn === filter;
  });

  return (
    <div>
      <div className="filters" role="group" aria-label="Checklist filter">
        {FILTERS.map((item) => (
          <button
            key={item}
            type="button"
            className="filter"
            aria-pressed={filter === item}
            onClick={() => setFilter(item)}
          >
            {item === "Open" ? `Open (${openCount})` : item}
          </button>
        ))}
      </div>
      {nistFunctions.map((fn) => {
        const group = visible.filter((item) => item.fn === fn);
        if (group.length === 0) return null;
        return (
          <section key={fn} className="check-group" aria-labelledby={`fn-${fn}`}>
            <h2 id={`fn-${fn}`}>{fn}</h2>
            <ul className="check-list">
              {group.map((item) => (
                <li key={item.id} className="item">
                  <span className={item.done ? "mark" : "mark open"}>{item.done ? "Done" : "Open"}</span>
                  <p>{item.text}</p>
                </li>
              ))}
            </ul>
          </section>
        );
      })}
    </div>
  );
}
