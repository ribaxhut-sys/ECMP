"use client";

import { useEffect, useState } from "react";
import { fetchPublicSettings } from "@/lib/api";

/** A settings value only counts as presets when it is a JSON array of non-empty strings. */
function parsePresetValue(value: string): string[] | null {
  try {
    const parsed: unknown = JSON.parse(value);
    if (
      Array.isArray(parsed) &&
      parsed.every((item) => typeof item === "string" && item.trim() !== "")
    ) {
      return parsed as string[];
    }
  } catch {
    // malformed setting value — treat as "no presets"
  }
  return null;
}

/**
 * Quick-fill presets for free-text fields, read from PUBLIC settings.
 *
 * Returns `{}` until the fetch resolves; a key that is missing or malformed
 * simply stays absent, and ReasonPresetTags renders nothing for an empty list.
 * Pass a module-level constant for `keys` so the fetch runs once per mount.
 */
export function useReasonPresets(
  keys: readonly string[],
): Record<string, string[]> {
  const keysKey = keys.join("|");
  const [presets, setPresets] = useState<Record<string, string[]>>({});

  useEffect(() => {
    const wanted = new Set(keysKey.split("|").filter(Boolean));
    let cancelled = false;
    fetchPublicSettings()
      .then((res) => {
        if (cancelled) return;
        const next: Record<string, string[]> = {};
        for (const setting of res.data ?? []) {
          if (!wanted.has(setting.key)) continue;
          const parsed = parsePresetValue(setting.value);
          if (parsed) next[setting.key] = parsed;
        }
        setPresets(next);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [keysKey]);

  return presets;
}
