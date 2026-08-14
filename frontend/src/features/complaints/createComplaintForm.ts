import type { CmBatch1CreateComplaintRequest } from "@/lib/api/cmBatch1";
import type { ComplaintCreateRequest, Priority } from "@/lib/api/types";

export interface CreateComplaintFormValues {
  customerName: string;
  customerId: string;
  subject: string;
  description: string;
  /** Agent disposition note: branch resolution OR escalation reason (history). */
  resolution: string;
  priority: Priority | "";
  branchId: string;
  channel: string;
  /** Hidden in UI; API-500 still requires category — default GENERAL. */
  category: string;
  reportedAt: string;
}

export type CreateComplaintFieldErrors = Partial<
  Record<keyof CreateComplaintFormValues, string>
>;

/** Local `datetime-local` value (YYYY-MM-DDTHH:mm) for the current moment. */
export function defaultReportedAtLocal(date = new Date()): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function createEmptyComplaintForm(
  defaults?: { branchId?: string | null; channel?: string | null },
): CreateComplaintFormValues {
  return {
    customerName: "",
    customerId: "",
    subject: "",
    description: "",
    resolution: "",
    priority: "",
    branchId: defaults?.branchId?.trim() || "",
    channel: defaults?.channel?.trim() || "BRANCH",
    category: "GENERAL",
    reportedAt: defaultReportedAtLocal(),
  };
}

/** Values only — labels come from useTranslations in the view. */
export const PRIORITY_OPTIONS = [
  { value: "LOW" },
  { value: "MEDIUM" },
  { value: "HIGH" },
  { value: "CRITICAL" },
] as const;

export const CHANNEL_OPTIONS = [
  { value: "CALL" },
  { value: "EMAIL" },
  { value: "BRANCH" },
  { value: "WEB" },
  { value: "OTHER" },
] as const;

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

function isUuid(value: string): boolean {
  return UUID_RE.test(value.trim());
}

/**
 * Client-side validation aligned with ComplaintCreateRequest (API-201).
 * Returns `validation.*` message keys (not localized strings).
 */
export function validateCreateComplaintForm(
  values: CreateComplaintFormValues,
): CreateComplaintFieldErrors {
  const errors: CreateComplaintFieldErrors = {};

  const customerId = values.customerId.trim();
  if (!customerId) {
    errors.customerId = "selectCustomer";
  } else if (!isUuid(customerId)) {
    errors.customerId = "customerIdInvalid";
  }

  if (!values.customerName.trim()) {
    errors.customerName = "customerNameRequired";
  }

  const subject = values.subject.trim();
  if (!subject) {
    errors.subject = "subjectRequired";
  } else if (subject.length > 200) {
    errors.subject = "subjectMax";
  }

  const description = values.description.trim();
  if (!description) {
    errors.description = "descriptionRequired";
  } else if (description.length > 5000) {
    errors.description = "descriptionMax";
  }

  if (!values.priority) {
    errors.priority = "priorityRequired";
  }

  const branchId = values.branchId.trim();
  if (!branchId) {
    errors.branchId = "selectBranch";
  } else if (!isUuid(branchId)) {
    errors.branchId = "branchIdInvalid";
  }

  const channel = values.channel.trim();
  if (channel.length > 32) {
    errors.channel = "channelMax";
  }

  const category = values.category.trim();
  if (category.length > 64) {
    errors.category = "categoryMax";
  }

  if (values.reportedAt) {
    const parsed = new Date(values.reportedAt);
    if (Number.isNaN(parsed.getTime())) {
      errors.reportedAt = "invalidDateTime";
    }
  }

  return errors;
}

export function toCreateComplaintRequest(
  values: CreateComplaintFormValues,
): ComplaintCreateRequest {
  const branchId = values.branchId.trim();
  const channel = values.channel.trim();
  const category = values.category.trim();
  const reportedAtLocal = values.reportedAt.trim();

  const body: ComplaintCreateRequest = {
    customerId: values.customerId.trim(),
    subject: values.subject.trim(),
    description: values.description.trim(),
    priority: values.priority as Priority,
    branchId,
  };

  if (channel) body.channel = channel;
  if (category) body.category = category;
  if (reportedAtLocal) {
    body.reportedAt = new Date(reportedAtLocal).toISOString();
  }

  return body;
}

/**
 * Client-side validation for CM Batch-1 Aggregate create (API-500).
 * Category + channel required; customerId is opaque string (not UUID-only).
 * Returns `validation.*` message keys (not localized strings).
 */
export function validateCmBatch1CreateForm(
  values: CreateComplaintFormValues,
): CreateComplaintFieldErrors {
  const errors: CreateComplaintFieldErrors = {};

  const customerId = values.customerId.trim();
  if (!customerId) {
    errors.customerId = "selectCustomer";
  } else if (customerId.length > 128) {
    errors.customerId = "customerIdMax";
  }

  if (!values.customerName.trim()) {
    errors.customerName = "customerNameRequired";
  }

  const subject = values.subject.trim();
  if (!subject) {
    errors.subject = "subjectRequired";
  } else if (subject.length > 200) {
    errors.subject = "subjectMax";
  }

  const description = values.description.trim();
  if (!description) {
    errors.description = "descriptionRequired";
  } else if (description.length > 5000) {
    errors.description = "descriptionMax";
  }

  const resolution = values.resolution.trim();
  if (!resolution) {
    errors.resolution = "intakeNoteRequired";
  } else if (resolution.length > 5000) {
    errors.resolution = "descriptionMax";
  }
  const composedLen = Math.max(
    composeCmBatch1Description(description, resolution).length,
    composeCmBatch1Description(description, resolution, { escalate: true })
      .length,
  );
  if (composedLen > 5000) {
    errors.resolution = "descriptionMax";
  }

  // category is system-defaulted (GENERAL) — not collected on intake UI

  const channel = values.channel.trim();
  if (!channel) {
    errors.channel = "channelRequired";
  } else if (channel.length > 32) {
    errors.channel = "channelMax";
  }

  if (values.priority) {
    // optional on Aggregate create; validate enum only when set
  }

  const branchId = values.branchId.trim();
  if (branchId && !isUuid(branchId)) {
    errors.branchId = "branchIdInvalid";
  }

  return errors;
}

/** Marker labels persisted in description — history for Supervisor / HQ. */
/** Intake officer note (register / branch close) — preferred section label. */
export const INTAKE_SECTION_INTAKE_NOTE = "Catatan";
/** Legacy label for intake note — still parsed for older rows. */
export const INTAKE_SECTION_BRANCH_RESOLUTION = "Penyelesaian";
export const INTAKE_SECTION_ESCALATION_REASON = "Alasan eskalasi";
export const INTAKE_SECTION_ESCALATION_REQUEST = "Ajuan eskalasi";
export const INTAKE_SECTION_SUPERVISOR_NOTE = "Catatan Supervisor";
export const INTAKE_SECTION_REJECTION_NOTE = "Penolakan Eskalasi";
export const INTAKE_SECTION_CANCEL_NOTE = "Batalkan Eskalasi";
/** Legacy history label — still parsed for older rows. */
export const INTAKE_SECTION_CANCEL_NOTE_LEGACY = "Batal Eskalasi";

const SECTION_SEP = "\n\n---\n";

export interface ParsedCmBatch1Description {
  narrative: string;
  branchResolution: string | null;
  escalationReason: string | null;
  escalationRequestNote: string | null;
  supervisorNote: string | null;
  rejectionNote: string | null;
  cancellationNote: string | null;
}

/** Parse structured intake history from the Aggregate description blob. */
export function parseCmBatch1Description(
  raw: string | null | undefined,
): ParsedCmBatch1Description {
  const text = (raw ?? "").trim();
  if (!text) {
    return {
      narrative: "",
      branchResolution: null,
      escalationReason: null,
      escalationRequestNote: null,
      supervisorNote: null,
      rejectionNote: null,
      cancellationNote: null,
    };
  }

  const parts = text.split(SECTION_SEP);
  const narrative = parts[0]?.trim() ?? "";
  let branchResolution: string | null = null;
  let escalationReason: string | null = null;
  let escalationRequestNote: string | null = null;
  let supervisorNote: string | null = null;
  let rejectionNote: string | null = null;
  let cancellationNote: string | null = null;

  for (const part of parts.slice(1)) {
    const chunk = part.trim();
    if (chunk.startsWith(`${INTAKE_SECTION_INTAKE_NOTE}:`)) {
      const value = chunk.slice(INTAKE_SECTION_INTAKE_NOTE.length + 1).trim();
      branchResolution = value || null;
    } else if (chunk.startsWith(`${INTAKE_SECTION_BRANCH_RESOLUTION}:`)) {
      // Legacy: "Penyelesaian:" → same slot as Catatan (prefer Catatan if both).
      if (!branchResolution) {
        const value = chunk
          .slice(INTAKE_SECTION_BRANCH_RESOLUTION.length + 1)
          .trim();
        branchResolution = value || null;
      }
    } else if (chunk.startsWith(`${INTAKE_SECTION_ESCALATION_REASON}:`)) {
      const value = chunk
        .slice(INTAKE_SECTION_ESCALATION_REASON.length + 1)
        .trim();
      escalationReason = value || null;
    } else if (chunk.startsWith(`${INTAKE_SECTION_ESCALATION_REQUEST}:`)) {
      const value = chunk
        .slice(INTAKE_SECTION_ESCALATION_REQUEST.length + 1)
        .trim();
      escalationRequestNote = value || null;
    } else if (chunk.startsWith(`${INTAKE_SECTION_SUPERVISOR_NOTE}:`)) {
      const value = chunk.slice(INTAKE_SECTION_SUPERVISOR_NOTE.length + 1).trim();
      supervisorNote = value || null;
    } else if (chunk.startsWith(`${INTAKE_SECTION_REJECTION_NOTE}:`)) {
      const value = chunk.slice(INTAKE_SECTION_REJECTION_NOTE.length + 1).trim();
      rejectionNote = value || null;
    } else if (chunk.startsWith(`${INTAKE_SECTION_CANCEL_NOTE}:`)) {
      const value = chunk.slice(INTAKE_SECTION_CANCEL_NOTE.length + 1).trim();
      cancellationNote = value || null;
    } else if (chunk.startsWith(`${INTAKE_SECTION_CANCEL_NOTE_LEGACY}:`)) {
      if (!cancellationNote) {
        const value = chunk
          .slice(INTAKE_SECTION_CANCEL_NOTE_LEGACY.length + 1)
          .trim();
        cancellationNote = value || null;
      }
    }
  }

  return {
    narrative,
    branchResolution,
    escalationReason,
    escalationRequestNote,
    supervisorNote,
    rejectionNote,
    cancellationNote,
  };
}

/**
 * Compose Aggregate description as durable intake history.
 * - Register / branch close → section Catatan (what was told / done for the taxpayer)
 * - Escalate → section Alasan eskalasi (+ pending-approval marker)
 */
export function composeCmBatch1Description(
  description: string,
  resolution: string,
  options?: { escalate?: boolean },
): string {
  const body = description.trim();
  const note = resolution.trim();
  const parts = [body];
  if (note) {
    if (options?.escalate) {
      parts.push(`---\n${INTAKE_SECTION_ESCALATION_REASON}:\n${note}`);
    } else {
      parts.push(`---\n${INTAKE_SECTION_INTAKE_NOTE}:\n${note}`);
    }
  }
  if (options?.escalate) {
    parts.push(
      `---\n${INTAKE_SECTION_ESCALATION_REQUEST}:\nMenunggu persetujuan Supervisor/Manager cabang untuk eskalasi ke Pusat. Deskripsi dan alasan eskalasi tersimpan sebagai riwayat untuk Pusat.`,
    );
  }
  return parts.filter(Boolean).join("\n\n");
}

/** Format REGISTERED intake-history note: Deskripsi + Catatan. */
export function formatRegisteredIntakeNote(
  narrative: string,
  intakeNote: string | null | undefined,
  labels: { description: string; note: string },
): string {
  const desc = narrative.trim() || "—";
  const note = (intakeNote ?? "").trim() || "—";
  return `${labels.description}:\n${desc}\n\n${labels.note}:\n${note}`;
}

/** Map form values → API-500 CreateComplaintBatch1Request. */
export function toCmBatch1CreateRequest(
  values: CreateComplaintFormValues,
  options?: {
    duplicateOverrideJustification?: string | null;
    stagingToken?: string | null;
    escalate?: boolean;
    closeAtBranch?: boolean;
    /** Branch.code — preferred org key (not Branch.id UUID). */
    recordingUnitCode?: string | null;
  },
): CmBatch1CreateComplaintRequest {
  const body: CmBatch1CreateComplaintRequest = {
    customerId: values.customerId.trim(),
    category: values.category.trim() || "GENERAL",
    channel: values.channel.trim(),
    subject: values.subject.trim(),
    description: composeCmBatch1Description(
      values.description,
      values.resolution,
      { escalate: Boolean(options?.escalate) },
    ),
  };

  if (values.priority) {
    body.priority = values.priority;
  }
  const recordingUnitId =
    (options?.recordingUnitCode || "").trim() || values.branchId.trim();
  if (recordingUnitId) {
    body.recordingUnitId = recordingUnitId;
  }
  const justification = options?.duplicateOverrideJustification?.trim();
  if (justification) {
    body.duplicateOverrideJustification = justification;
  }
  const stagingToken = options?.stagingToken?.trim();
  if (stagingToken) {
    body.stagingToken = stagingToken;
  }
  if (options?.closeAtBranch) {
    body.intakeDisposition = "BRANCH_CLOSED";
  }
  if (options?.escalate) {
    body.intakeDisposition = "ESCALATE_PENDING_APPROVAL";
  }

  return body;
}

/** Idempotency-Key for API-500 (UUID v4 when available). */
export function newCmBatch1IdempotencyKey(): string {
  if (
    typeof globalThis.crypto !== "undefined" &&
    typeof globalThis.crypto.randomUUID === "function"
  ) {
    return globalThis.crypto.randomUUID();
  }
  return `cm-b1-${Date.now()}-${Math.random().toString(36).slice(2, 12)}`;
}

/**
 * Create-session staging token (FR-004 / API-507).
 * Matches backend pattern `STG-{hex}`; reused for all staged uploads in one create.
 */
export function newCmBatch1StagingToken(): string {
  if (
    typeof globalThis.crypto !== "undefined" &&
    typeof globalThis.crypto.randomUUID === "function"
  ) {
    return `STG-${globalThis.crypto.randomUUID().replace(/-/g, "")}`;
  }
  return `STG-${Date.now().toString(16)}${Math.random().toString(16).slice(2, 14)}`;
}
