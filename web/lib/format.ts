/** Six-decimal text, matching the committed reports. */
export function six(value: number): string {
  return value.toFixed(6);
}

export function count(value: number): string {
  return String(value);
}
