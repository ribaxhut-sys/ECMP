export type CustomerListLabel = { name: string; number: string | null };

export function looksLikeUuid(value: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
    value.trim(),
  );
}

export function profileText(
  profile: Record<string, unknown> | null | undefined,
  ...keys: string[]
): string | null {
  if (!profile) return null;
  for (const key of keys) {
    const value = profile[key];
    if (typeof value === "string" && value.trim()) return value.trim();
  }
  return null;
}

export function customerListLabel(
  name: string | null | undefined,
  number: string | null | undefined,
): CustomerListLabel | null {
  const displayName = (name || "").trim();
  const displayNumber = (number || "").trim();
  if (!displayName && !displayNumber) return null;
  if (displayName && displayNumber && displayName !== displayNumber) {
    return { name: displayName, number: displayNumber };
  }
  return { name: displayName || displayNumber, number: null };
}

export function putCustomerLabel(
  map: Record<string, CustomerListLabel>,
  keys: Array<string | null | undefined>,
  label: CustomerListLabel | null,
) {
  if (!label) return;
  for (const key of keys) {
    const id = (key || "").trim();
    if (id) map[id] = label;
  }
}

export function customerLabelForId(
  customerId: string | null | undefined,
  labels: Record<string, CustomerListLabel>,
  emDash: string,
): CustomerListLabel {
  const id = (customerId || "").trim();
  if (!id) return { name: emDash, number: null };
  if (labels[id]) return labels[id];
  if (looksLikeUuid(id)) return { name: emDash, number: null };
  return { name: id, number: null };
}
