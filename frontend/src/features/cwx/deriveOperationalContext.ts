/**
 * CWX-M2 — presentation helpers only.
 * No invented APIs, workflows, repeat engines, or customer-master fields.
 */

export type CwxBadgeKind =
  | "high_priority"
  | "critical_sla"
  | "escalated"
  | "waiting_customer";

export type CwxNextActionKey =
  | "assign"
  | "start_progress"
  | "mark_pending"
  | "resume"
  | "close"
  | "resolve"
  | "review_escalation"
  | "none";

export type CwxBlockingReasonKey = "waiting_customer";

export type CwxSurface = "foundation" | "aggregate";

export type DeriveOperationalContextInput = {
  status: string;
  priority: string;
  /** Dual-SoT surface — affects next-action presentation map only. */
  surface?: CwxSurface;
  /** Foundation SLA overallStatus when present. */
  overallSlaStatus?: string | null;
  /** Foundation SLA escalationStatus when present. */
  escalationSlaStatus?: string | null;
  assignedToLabel?: string | null;
  branchLabel?: string | null;
  lastUpdated?: string | null;
  category?: string | null;
  channel?: string | null;
  createdAt?: string | null;
  customerName?: string | null;
  complaintCount?: number | null;
  customerType?: string | null;
  assignmentDueAt?: string | null;
  resolutionDueAt?: string | null;
  escalationDueAt?: string | null;
  overallDueAt?: string | null;
};

export type OperationalContextFields = {
  status: string;
  assignedTo?: string;
  escalationStatus?: string;
  branch?: string;
  lastUpdated?: string;
};

export type CurrentWorkFields = {
  /** False when status is terminal (CLOSED / CANCELLED). */
  show: boolean;
  responsible?: string;
  dueAt?: string;
  nextActionKey: CwxNextActionKey;
  blockingReasonKey?: CwxBlockingReasonKey;
};

export type CaseSummaryFields = {
  category?: string;
  channel?: string;
  createdAt?: string;
  currentStage: string;
};

export type CustomerSummaryFields = {
  name?: string;
  complaintCount?: number;
  customerType?: string;
};

export type DerivedBadge = {
  kind: CwxBadgeKind;
};

export type DerivedOperationalContext = {
  badges: DerivedBadge[];
  operational: OperationalContextFields;
  currentWork: CurrentWorkFields;
  caseSummary: CaseSummaryFields;
  customerSummary: CustomerSummaryFields;
};

const TERMINAL = new Set(["CLOSED", "CANCELLED"]);

function nonEmpty(value: string | null | undefined): string | undefined {
  const trimmed = value?.trim();
  return trimmed ? trimmed : undefined;
}

function isTerminal(status: string): boolean {
  return TERMINAL.has(status.toUpperCase());
}

/**
 * Badges from existing fields only. Never invent Repeat Complaint.
 * Caller may slice to max-4 + overflow in the UI.
 */
export function deriveContextBadges(input: {
  status: string;
  priority: string;
  overallSlaStatus?: string | null;
}): DerivedBadge[] {
  const status = input.status.toUpperCase();
  const priority = input.priority.toUpperCase();
  const overall = (input.overallSlaStatus ?? "").toUpperCase();
  const badges: DerivedBadge[] = [];

  if (priority === "HIGH") {
    badges.push({ kind: "high_priority" });
  }
  if (overall === "BREACHED") {
    badges.push({ kind: "critical_sla" });
  }
  if (status === "ESCALATED") {
    badges.push({ kind: "escalated" });
  }
  if (status === "PENDING") {
    badges.push({ kind: "waiting_customer" });
  }

  return badges;
}

/**
 * Next expected action — presentation map from status only (no new state machine).
 * Aggregate IN_PROGRESS → resolve (existing Aggregate resolve gate); Foundation → mark_pending.
 */
export function deriveNextActionKey(
  status: string,
  surface: CwxSurface = "foundation",
): CwxNextActionKey {
  switch (status.toUpperCase()) {
    case "NEW":
    case "CREATED":
      return "assign";
    case "ASSIGNED":
      return "start_progress";
    case "IN_PROGRESS":
      return surface === "aggregate" ? "resolve" : "mark_pending";
    case "PENDING":
      return "resume";
    case "ESCALATED":
      return "review_escalation";
    case "RESOLVED":
      return "close";
    case "CLOSED":
    case "CANCELLED":
      return "none";
    default:
      return "none";
  }
}

/**
 * Relevant due date from existing SLA fields by status (omit if absent).
 */
export function deriveRelevantDueAt(input: {
  status: string;
  assignmentDueAt?: string | null;
  resolutionDueAt?: string | null;
  escalationDueAt?: string | null;
  overallDueAt?: string | null;
}): string | undefined {
  const status = input.status.toUpperCase();
  let primary: string | null | undefined;

  if (status === "NEW" || status === "CREATED" || status === "ASSIGNED") {
    primary = input.assignmentDueAt;
  } else if (status === "ESCALATED") {
    primary = input.escalationDueAt ?? input.overallDueAt;
  } else if (
    status === "IN_PROGRESS" ||
    status === "PENDING" ||
    status === "RESOLVED"
  ) {
    primary = input.resolutionDueAt;
  } else {
    primary = input.overallDueAt;
  }

  return (
    nonEmpty(primary) ??
    nonEmpty(input.overallDueAt) ??
    nonEmpty(input.resolutionDueAt) ??
    nonEmpty(input.assignmentDueAt)
  );
}

function deriveEscalationStatus(input: DeriveOperationalContextInput): string | undefined {
  const status = input.status.toUpperCase();
  if (status === "ESCALATED") {
    return "ESCALATED";
  }
  return nonEmpty(input.escalationSlaStatus);
}

/**
 * Full CWX-M2 derivation. Operational fields never include Priority / Owner / SLA / Current Work.
 */
export function deriveOperationalContext(
  input: DeriveOperationalContextInput,
): DerivedOperationalContext {
  const status = input.status;
  const statusUpper = status.toUpperCase();
  const assignedTo = nonEmpty(input.assignedToLabel);
  const terminal = isTerminal(status);

  const operational: OperationalContextFields = {
    status,
  };
  if (assignedTo) operational.assignedTo = assignedTo;
  const escalationStatus = deriveEscalationStatus(input);
  if (escalationStatus) operational.escalationStatus = escalationStatus;
  const branch = nonEmpty(input.branchLabel);
  if (branch) operational.branch = branch;
  const lastUpdated = nonEmpty(input.lastUpdated);
  if (lastUpdated) operational.lastUpdated = lastUpdated;

  const currentWork: CurrentWorkFields = {
    show: !terminal,
    nextActionKey: deriveNextActionKey(status, input.surface ?? "foundation"),
  };
  if (!terminal) {
    if (assignedTo) currentWork.responsible = assignedTo;
    const dueAt = deriveRelevantDueAt(input);
    if (dueAt) currentWork.dueAt = dueAt;
    if (statusUpper === "PENDING") {
      currentWork.blockingReasonKey = "waiting_customer";
    }
  }

  const caseSummary: CaseSummaryFields = {
    currentStage: status,
  };
  const category = nonEmpty(input.category);
  if (category) caseSummary.category = category;
  const channel = nonEmpty(input.channel);
  if (channel) caseSummary.channel = channel;
  const createdAt = nonEmpty(input.createdAt);
  if (createdAt) caseSummary.createdAt = createdAt;

  const customerSummary: CustomerSummaryFields = {};
  const name = nonEmpty(input.customerName);
  if (name) customerSummary.name = name;
  if (
    typeof input.complaintCount === "number" &&
    Number.isFinite(input.complaintCount)
  ) {
    customerSummary.complaintCount = input.complaintCount;
  }
  const customerType = nonEmpty(input.customerType);
  if (customerType) customerSummary.customerType = customerType;

  return {
    badges: deriveContextBadges({
      status,
      priority: input.priority,
      overallSlaStatus: input.overallSlaStatus,
    }),
    operational,
    currentWork,
    caseSummary,
    customerSummary,
  };
}
