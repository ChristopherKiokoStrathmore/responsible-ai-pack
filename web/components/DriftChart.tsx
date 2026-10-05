"use client";

import { useState } from "react";
import { six } from "@/lib/format";

type DriftFeature = {
  name: string;
  kind: string;
  psi: number;
  aboveTrigger: boolean;
};

export function DriftChart({
  features,
  trigger,
}: {
  features: DriftFeature[];
  trigger: number;
}) {
  const opening = features.reduce((best, feature) => (feature.psi >= best.psi ? feature : best));
  const [name, setName] = useState(opening.name);
  const selected = features.find((feature) => feature.name === name) ?? opening;

  return (
    <div>
      <ul className="psi-list">
        {features.map((feature) => {
          const width = Math.min(100, (feature.psi / trigger) * 100);
          const pressed = feature.name === selected.name;
          return (
            <li key={feature.name}>
              <button
                type="button"
                className="psi-btn"
                aria-pressed={pressed}
                onClick={() => setName(feature.name)}
              >
                <span className="psi-name">{feature.name}</span>
                <span className="psi-track" aria-hidden="true">
                  <span className="psi-bar" style={{ width: `${width}%` }} />
                </span>
                <span className="psi-val">{six(feature.psi)}</span>
              </button>
            </li>
          );
        })}
      </ul>
      <p aria-live="polite">
        {selected.name} is {selected.kind}. PSI {six(selected.psi)}. above_trigger:{" "}
        {selected.aboveTrigger ? "true" : "false"}. The red mark at the right of each track is the
        review trigger {six(trigger)}.
      </p>
    </div>
  );
}
