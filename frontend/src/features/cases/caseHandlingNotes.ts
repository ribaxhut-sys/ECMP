import type { CmCaseHistoryEntry } from "@/lib/api";
import { parseCmBatch1Description } from "@/features/complaints/createComplaintForm";
import { caseHistoryDisplayLabelKey } from "./caseHistoryMeta";

export type CaseHandlingNoteSource = "blob" | "history";

export interface CaseHandlingNote {
  key: string;
  source: CaseHandlingNoteSource;
  /** `cases.*` message key for the note heading. */
  labelKey: string;
  /** History event code when the note came from API-537; omitted for blob notes. */
  eventCode?: string;
  text: string;
  actorName?: string | null;
  actorId?: string | null;
  occurredAt?: string | null;
}

export interface CaseHandlingNoteGroup {
  parent: CaseHandlingNote;
  children: CaseHandlingNote[];
}

const INTAKE_PARENT_CODES = new Set([
  "CASE_CREATED",
  "CASE_ESCALATED_TO_PUSAT",
]);

const INLINE_NOTE = /\n\n(?:Catatan|Note):\s*\n/i;
const LEADING_DESCRIPTION = /^(Deskripsi|Description):\s*\n/i;

const BLOB_NOTE_KEYS = [
  { field: "escalationReason", labelKey: "handlingNoteEscalationReason" },
  { field: "supervisorNote", labelKey: "handlingNoteSupervisor" },
  { field: "rejectionNote", labelKey: "handlingNoteRejection" },
  { field: "cancellationNote", labelKey: "handlingNoteCancellation" },
] as const;

/**
 * Outcome / acceptance notes belong in Resolusi + Riwayat log — not Catatan.
 * Dual-acceptance codes are Internal Complaint vocabulary (hidden on WP Case).
 * Repeating them under every lifecycle label is noise (same body N times).
 */
const HISTORY_NOTE_EXCLUDED_CODES = new Set([
  "CASE_RESOLVED",
  "CASE_CLOSED",
  "CASE_OWNER_ACCEPTED",
  "CASE_OWNER_REJECTED",
  "CASE_HANDLING_UNIT_ACCEPTED",
  "CASE_HANDLING_UNIT_REJECTED",
]);

function normalizeNoteText(text: string): string {
  return text.trim().replace(/\s+/g, " ").toLowerCase();
}

function stripLeadingDescriptionLabel(text: string): string {
  return text.replace(LEADING_DESCRIPTION, "").trim();
}

function splitInlineNote(text: string): { narrative: string; note: string | null } {
  const idx = text.search(INLINE_NOTE);
  if (idx === -1) {
    return { narrative: stripLeadingDescriptionLabel(text), note: null };
  }
  const note = text.slice(idx).replace(INLINE_NOTE, "").trim() || null;
  return {
    narrative: stripLeadingDescriptionLabel(text.slice(0, idx)),
    note,
  };
}

/** Narrative only — section labels and catatan stay out of Deskripsi. */
export function caseDescriptionNarrative(raw: string | null | undefined): string {
  const parsed = parseCmBatch1Description(raw);
  return splitInlineNote(parsed.narrative).narrative;
}

/** Intake Catatan from a description blob (Case or parent Complaint). */
export function intakeNoteFromDescription(
  raw: string | null | undefined,
): string | null {
  const parsed = parseCmBatch1Description(raw);
  const inline = splitInlineNote(parsed.narrative);
  return parsed.branchResolution?.trim() || inline.note;
}

function blobNotesFromDescription(raw: string | null | undefined): CaseHandlingNote[] {
  const parsed = parseCmBatch1Description(raw);
  const notes: CaseHandlingNote[] = [];
  const intake = intakeNoteFromDescription(raw);
  if (intake) {
    notes.push({
      key: "blob-intake",
      source: "blob",
      labelKey: "handlingNoteIntake",
      text: intake,
    });
  }
  for (const { field, labelKey } of BLOB_NOTE_KEYS) {
    const text = parsed[field]?.trim();
    if (!text) continue;
    notes.push({
      key: `blob-${field}`,
      source: "blob",
      labelKey,
      text,
    });
  }
  return notes;
}

function historyNotes(
  entries: CmCaseHistoryEntry[],
  seen: Set<string>,
): CaseHandlingNote[] {
  const notes: CaseHandlingNote[] = [];
  entries.forEach((entry, index) => {
    const code = entry.eventCode.trim().toUpperCase();
    if (HISTORY_NOTE_EXCLUDED_CODES.has(code)) return;
    const text = entry.note?.trim() || "";
    if (!text) return;
    const key = normalizeNoteText(text);
    if (seen.has(key)) return;
    seen.add(key);
    notes.push({
      key: entry.entryId || `history-${index}`,
      source: "history",
      labelKey: caseHistoryDisplayLabelKey(
        entry.eventCode,
        entries.slice(0, index).map((row) => row.eventCode),
      ),
      eventCode: code,
      text,
      actorName: entry.actorName,
      actorId: entry.actorId,
      occurredAt: entry.occurredAt,
    });
  });
  return notes;
}

export type CollectCaseHandlingNotesExtras = {
  parentIntakeNote?: string | null;
  /** Resolusi summary/comment — omit from Catatan when identical. */
  resolutionTexts?: Array<string | null | undefined>;
};

/**
 * Catatan for the Case work card: blob sections not already on the timeline,
 * then chronological timeline notes (API-537).
 *
 * Milestone resolve/close/dual-acceptance notes are omitted (Resolusi + Riwayat).
 * Identical note bodies appear once.
 *
 * `parentIntakeNote` covers Cases created via Tangani pengaduan that did not
 * copy the Complaint Catatan onto the Case row — still Case-page content
 * (BR-017), not the parent confirmation card.
 */
export function collectCaseHandlingNotes(
  description: string | null | undefined,
  entries: CmCaseHistoryEntry[],
  extras?: CollectCaseHandlingNotesExtras,
): CaseHandlingNote[] {
  const seen = new Set<string>();
  for (const raw of extras?.resolutionTexts ?? []) {
    const text = raw?.trim() || "";
    if (text) seen.add(normalizeNoteText(text));
  }
  const fromHistory = historyNotes(entries, seen);
  const fromBlob = blobNotesFromDescription(description).filter((row) => {
    const key = normalizeNoteText(row.text);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
  const parentIntake = extras?.parentIntakeNote?.trim() || "";
  if (parentIntake) {
    const key = normalizeNoteText(parentIntake);
    if (!seen.has(key)) {
      seen.add(key);
      fromBlob.push({
        key: "blob-intake-parent",
        source: "blob",
        labelKey: "handlingNoteIntake",
        text: parentIntake,
      });
    }
  }
  return [...fromBlob, ...fromHistory];
}

/**
 * Outline for Catatan: HQ accept nests under create/escalate; later arrival
 * slots nest under the first schedule (reschedule — not a new domain event).
 * Notes without a parent stay top-level. Empty parents are not invented.
 */
export function groupCaseHandlingNotes(
  notes: CaseHandlingNote[],
): CaseHandlingNoteGroup[] {
  const groups: CaseHandlingNoteGroup[] = [];
  let intakeGroup: CaseHandlingNoteGroup | null = null;
  let scheduleGroup: CaseHandlingNoteGroup | null = null;

  for (const note of notes) {
    const code = (note.eventCode || "").trim().toUpperCase();

    if (code === "HQ_ACCEPTED" && intakeGroup) {
      intakeGroup.children.push(note);
      continue;
    }

    if (code === "HQ_ARRIVAL_SCHEDULED" && scheduleGroup) {
      scheduleGroup.children.push({
        ...note,
        labelKey: "eventHqRescheduled",
      });
      continue;
    }

    const group: CaseHandlingNoteGroup = { parent: note, children: [] };
    groups.push(group);
    if (INTAKE_PARENT_CODES.has(code)) intakeGroup = group;
    if (code === "HQ_ARRIVAL_SCHEDULED") scheduleGroup = group;
  }

  return groups;
}
