/**
 * CWX-M1 — presentation helpers only.
 * Layout level from existing status / priority / SLA signals.
 * No invented repeat engine (Level 2 reserved until M2 data exists).
 */

export type CwxLayoutLevel = 1 | 2 | 3 | 4;

export type CwxContextLevelInput = {
  /** Foundation complaint status or Aggregate case status string */
  status: string;
  priority: string;
  /** True when overall SLA is BREACHED (Foundation). */
  slaBreached?: boolean;
};

export function deriveContextLevel(input: CwxContextLevelInput): CwxLayoutLevel {
  const priority = input.priority.toUpperCase();
  const status = input.status.toUpperCase();

  if (input.slaBreached || priority === "CRITICAL") {
    return 4;
  }
  if (status === "ESCALATED") {
    return 3;
  }
  // Level 2 (repeat) requires a real repeat signal — not invented in M1.
  return 1;
}
