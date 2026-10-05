/** Same definitions the fairness report and the PSI script use. */

export type ScoreTable = {
  gender: readonly string[];
  senior: readonly number[];
  label: readonly number[];
  probability: readonly number[];
};

export type GroupRate = {
  key: string;
  n: number;
  nPositive: number;
  nSelected: number;
  selectionRate: number;
  truePositiveRate: number | null;
  falsePositiveRate: number | null;
};

export type FieldFairness = {
  groups: GroupRate[];
  demographicParityDifference: number;
  equalizedOddsDifference: number | null;
  n: number;
  nSelected: number;
  selectionRate: number;
};

const GENDER_KEYS = ["Female", "Male"] as const;
const SENIOR_KEYS = ["0", "1"] as const;

export function sameSix(computed: number | null, published: number): boolean {
  if (computed === null || Number.isNaN(computed)) return false;
  return computed.toFixed(6) === published.toFixed(6);
}

export function logistic(logOdds: number): number {
  if (logOdds >= 0) {
    return 1 / (1 + Math.exp(-logOdds));
  }
  const z = Math.exp(logOdds);
  return z / (1 + z);
}

export function populationStabilityIndex(
  referenceCounts: readonly number[],
  currentCounts: readonly number[],
  clipFloor = 0.000001,
): number {
  if (referenceCounts.length !== currentCounts.length || referenceCounts.length === 0) {
    throw new Error("counts must be non-empty and the same length");
  }
  const share = (counts: readonly number[]) => {
    const total = counts.reduce((sum, value) => sum + value, 0);
    if (total <= 0) throw new Error("counts must have a positive total");
    const clipped = counts.map((value) => {
      if (value < 0) throw new Error("counts must be non-negative");
      return Math.max(value / total, clipFloor);
    });
    const clippedTotal = clipped.reduce((sum, value) => sum + value, 0);
    return clipped.map((value) => value / clippedTotal);
  };
  const reference = share(referenceCounts);
  const current = share(currentCounts);
  let psi = 0;
  for (let i = 0; i < reference.length; i += 1) {
    psi += (current[i] - reference[i]) * Math.log(current[i] / reference[i]);
  }
  return psi;
}

/** Move `amount` of the current mass into `focus`, keeping the total. amount 0 returns a copy. */
export function shiftCounts(current: readonly number[], focus: number, amount: number): number[] {
  if (focus < 0 || focus >= current.length) throw new Error("focus bin is out of range");
  if (amount <= 0) return current.slice();
  const total = current.reduce((sum, value) => sum + value, 0);
  if (amount >= 1) return current.map((_, index) => (index === focus ? total : 0));
  return current.map((count, index) => count * (1 - amount) + (index === focus ? total : 0) * amount);
}

function groupRate(
  key: string,
  indexes: number[],
  label: readonly number[],
  selected: boolean[],
): GroupRate {
  const n = indexes.length;
  let nPositive = 0;
  let nSelected = 0;
  let truePositive = 0;
  let falsePositive = 0;
  for (const index of indexes) {
    const positive = label[index] === 1;
    if (positive) nPositive += 1;
    if (selected[index]) {
      nSelected += 1;
      if (positive) truePositive += 1;
      else falsePositive += 1;
    }
  }
  const nNegative = n - nPositive;
  return {
    key,
    n,
    nPositive,
    nSelected,
    selectionRate: n === 0 ? 0 : nSelected / n,
    truePositiveRate: nPositive === 0 ? null : truePositive / nPositive,
    falsePositiveRate: nNegative === 0 ? null : falsePositive / nNegative,
  };
}

export function fairnessAtCutoff(
  table: ScoreTable,
  cutoff: number,
  field: "gender" | "SeniorCitizen",
): FieldFairness {
  const n = table.probability.length;
  const selected = table.probability.map((value) => value > cutoff);
  const keys = field === "gender" ? GENDER_KEYS : SENIOR_KEYS;
  const groups = keys.map((key) => {
    const indexes: number[] = [];
    for (let i = 0; i < n; i += 1) {
      const rowKey = field === "gender" ? table.gender[i] : String(table.senior[i]);
      if (rowKey === key) indexes.push(i);
    }
    return groupRate(key, indexes, table.label, selected);
  });
  const selections = groups.map((group) => group.selectionRate);
  const demographicParityDifference = Math.abs(Math.max(...selections) - Math.min(...selections));
  const ratesReady = groups.every(
    (group) => group.truePositiveRate !== null && group.falsePositiveRate !== null,
  );
  let equalizedOddsDifference: number | null = null;
  if (ratesReady && groups.length >= 2) {
    const tprGap = Math.abs((groups[0].truePositiveRate ?? 0) - (groups[1].truePositiveRate ?? 0));
    const fprGap = Math.abs((groups[0].falsePositiveRate ?? 0) - (groups[1].falsePositiveRate ?? 0));
    equalizedOddsDifference = Math.max(tprGap, fprGap);
  }
  const nSelected = selected.reduce((sum, value) => sum + (value ? 1 : 0), 0);
  return {
    groups,
    demographicParityDifference,
    equalizedOddsDifference,
    n,
    nSelected,
    selectionRate: n === 0 ? 0 : nSelected / n,
  };
}
