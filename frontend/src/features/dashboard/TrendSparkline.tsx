"use client";

import { useMemo } from "react";
import type { DashboardTrendItem } from "@/lib/api/types";

const WIDTH = 96;
const HEIGHT = 28;

function buildPath(values: number[]): { line: string; area: string } {
  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);
  const range = max - min || 1;
  const stepX = values.length > 1 ? WIDTH / (values.length - 1) : 0;

  const points = values.map((value, index) => {
    const x = index * stepX;
    const y = HEIGHT - ((value - min) / range) * HEIGHT;
    return [x, y] as const;
  });

  const line = points
    .map(([x, y], index) => `${index === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`)
    .join(" ");

  const area = `${line} L${WIDTH.toFixed(1)},${HEIGHT} L0,${HEIGHT} Z`;

  return { line, area };
}

/**
 * Inline 30-day open-complaint trend. Foundation-scoped (DEC-020) — see
 * loadDashboardData.ts DashboardData.trend for the coexistence caveat.
 */
export function TrendSparkline({
  items,
  label,
  hint,
}: {
  items: DashboardTrendItem[];
  label: string;
  /** Optional tooltip — use to disclose data-source scope (e.g. DEC-020). */
  hint?: string;
}) {
  const { line, area, latest, direction } = useMemo(() => {
    const values = items.map((item) => item.count);
    // All-zero (e.g. foundation table empty under Aggregate-only intake,
    // DEC-020) draws a flat line pinned to the bottom edge — visually a
    // near-invisible sliver, and worse, it *asserts* "zero every day" when
    // the honest state is "no foundation data to measure at all". Hide
    // instead of drawing a claim we can't back up.
    const hasSignal = values.length > 1 && values.some((v) => v > 0);
    if (!hasSignal) {
      return { line: "", area: "", latest: values[0] ?? 0, direction: "flat" as const };
    }
    const { line, area } = buildPath(values);
    const first = values[0];
    const last = values[values.length - 1];
    const direction: "up" | "down" | "flat" =
      last > first ? "up" : last < first ? "down" : "flat";
    return { line, area, latest: last, direction };
  }, [items]);

  if (!line) return null;

  const toneClass =
    direction === "up"
      ? "text-ecmp-warning"
      : direction === "down"
        ? "text-ecmp-success"
        : "text-ecmp-text-secondary";

  return (
    <span title={hint} className="inline-flex">
      <svg
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        className={`h-7 w-24 shrink-0 ${toneClass}`}
        role="img"
        aria-label={hint ? `${label}: ${latest}. ${hint}` : `${label}: ${latest}`}
        preserveAspectRatio="none"
      >
        <path d={area} fill="currentColor" opacity="0.12" stroke="none" />
        <path
          d={line}
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </span>
  );
}
