import type { BranchHealthBarKey } from "./dashboardUtils";

/**
 * Fixed order (never reordered) — validated via the dataviz skill's palette
 * validator for adjacent-pair CVD separation, light + dark.
 * Matches BRANCH_HEALTH_BAR_KEYS: caseTotal, caseClosed, escalated.
 */
export const BRANCH_HEALTH_BAR_COLOR_CLASS: Record<BranchHealthBarKey, string> = {
  caseTotal: "bg-ecmp-chart-series-3",
  caseClosed: "bg-ecmp-chart-series-1",
  escalated: "bg-ecmp-chart-series-2",
};

export const BRANCH_HEALTH_BAR_LABEL_KEY: Record<
  BranchHealthBarKey,
  "branchHealthLegendCaseTotal" | "branchHealthLegendResolvedAtBranch" | "branchHealthLegendEscalated"
> = {
  caseTotal: "branchHealthLegendCaseTotal",
  caseClosed: "branchHealthLegendResolvedAtBranch",
  escalated: "branchHealthLegendEscalated",
};
