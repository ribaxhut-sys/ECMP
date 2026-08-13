/** Compat: old `/complaints/cm` bookmarks keep query on the CM list (DEC-025). */

export function cmCompatListRedirectHref(
  raw: Record<string, string | string[] | undefined>,
): string {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(raw)) {
    if (Array.isArray(value)) {
      for (const item of value) params.append(key, item);
    } else if (value) {
      params.set(key, value);
    }
  }
  const qs = params.toString();
  return qs ? `/complaints?${qs}` : "/complaints";
}
