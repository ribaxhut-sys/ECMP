/**
 * Frontend UI batch gate (WF-001-R1 + WF-001-R2).
 * B0 = Application shell
 * B1 = Supervisor Assign loop (mock)
 * B2 = Officer Queue + Handle (mock)
 * B3 = Intake — SCR-WS-01 + SCR-WS-02 (mock)
 * B4 = Submit — SCR-WS-05 (mock)
 * B5 = Approval close — SCR-Q-02 pending + SCR-WS-10 (mock)
 * B6 = Queue Supervisor priority — SCR-Q-02 escalation + SLA + unassigned (mock)
 * R2B1 = Reject Continuity — SCR-WS-06 + SCR-HX-01 embedded (mock)
 * R2B2 = Reopen Chain — SCR-WS-03 → SCR-WS-12 (+ HX-02) → SCR-WS-07 (+ HX-01) (mock)
 * R2B3 = Escalation Continuity — SCR-WS-11 (+ HX-02) → optional SCR-WS-08 (mock)
 */

export type UiBatchId =
  | "B0"
  | "B1"
  | "B2"
  | "B3"
  | "B4"
  | "B5"
  | "B6"
  | "R2B1"
  | "R2B2"
  | "R2B3";

export type ShellBatchOverlineKey =
  | "batchOverline"
  | "batchOverlineB1"
  | "batchOverlineB2"
  | "batchOverlineB3"
  | "batchOverlineB4"
  | "batchOverlineB5"
  | "batchOverlineB6"
  | "batchOverlineR2B1"
  | "batchOverlineR2B2"
  | "batchOverlineR2B3";

const BATCH_ORDER: Record<UiBatchId, number> = {
  B0: 0,
  B1: 1,
  B2: 2,
  B3: 3,
  B4: 4,
  B5: 5,
  B6: 6,
  R2B1: 7,
  R2B2: 8,
  R2B3: 9,
};

export function getUiBatch(): string | undefined {
  return process.env.NEXT_PUBLIC_ECMP_UI_BATCH;
}

export function isBatchB0(): boolean {
  return getUiBatch() === "B0";
}

export function isBatchB1(): boolean {
  return getUiBatch() === "B1";
}

export function isBatchB2(): boolean {
  return getUiBatch() === "B2";
}

export function isBatchB3(): boolean {
  return getUiBatch() === "B3";
}

export function isBatchB4(): boolean {
  return getUiBatch() === "B4";
}

export function isBatchB5(): boolean {
  return getUiBatch() === "B5";
}

export function isBatchB6(): boolean {
  return getUiBatch() === "B6";
}

export function isBatchR2B1(): boolean {
  return getUiBatch() === "R2B1";
}

export function isBatchR2B2(): boolean {
  return getUiBatch() === "R2B2";
}

export function isBatchR2B3(): boolean {
  return getUiBatch() === "R2B3";
}

/** True when current UI batch is `min` or a later shell batch. */
export function isBatchAtLeast(min: UiBatchId): boolean {
  const current = getUiBatch();
  if (!current || !(current in BATCH_ORDER)) return false;
  return BATCH_ORDER[current as UiBatchId] >= BATCH_ORDER[min];
}

/**
 * Shell UI batches (closed nav + mock auth).
 * Later batches include prior shell behaviour.
 */
export function isShellUiBatch(): boolean {
  return isBatchAtLeast("B0");
}

/** Mock auth without backend — on for shell batches; optional otherwise. */
export function isMockAuthEnabled(): boolean {
  return (
    isShellUiBatch() || process.env.NEXT_PUBLIC_ECMP_MOCK_AUTH === "true"
  );
}

/** i18n key for shell batch overline (highest active shell batch). */
export function getShellBatchOverlineKey(): ShellBatchOverlineKey {
  if (isBatchAtLeast("R2B3")) return "batchOverlineR2B3";
  if (isBatchAtLeast("R2B2")) return "batchOverlineR2B2";
  if (isBatchAtLeast("R2B1")) return "batchOverlineR2B1";
  if (isBatchAtLeast("B6")) return "batchOverlineB6";
  if (isBatchAtLeast("B5")) return "batchOverlineB5";
  if (isBatchAtLeast("B4")) return "batchOverlineB4";
  if (isBatchAtLeast("B3")) return "batchOverlineB3";
  if (isBatchAtLeast("B2")) return "batchOverlineB2";
  if (isBatchAtLeast("B1")) return "batchOverlineB1";
  return "batchOverline";
}
