import type { KnowledgeHistoryEntry } from "@/lib/api/types";

/** Field order for the "what changed" diff line under a KnowledgeUpdated
 * entry — matches the edit form's field order. */
const DIFF_FIELD_ORDER = [
  "title",
  "knowledgeType",
  "documentNumber",
  "versionLabel",
  "summary",
  "effectiveFrom",
  "effectiveTo",
] as const;

export type KnowledgeHistoryDiffField = (typeof DIFF_FIELD_ORDER)[number];

export function knowledgeHistoryEventLabelKey(eventType: string): string {
  switch (eventType) {
    case "KnowledgeCreated":
      return "historyEventCreated";
    case "KnowledgeUpdated":
      return "historyEventUpdated";
    case "KnowledgePublished":
      return "historyEventPublished";
    case "KnowledgeArchived":
      return "historyEventArchived";
    case "KnowledgeUnarchived":
      return "historyEventUnarchived";
    case "KnowledgeDeleted":
      return "historyEventDeleted";
    case "KnowledgeFileUploaded":
      return "historyEventFileUploaded";
    case "KnowledgeFileReplaced":
      return "historyEventFileReplaced";
    case "KnowledgeFileRemoved":
      return "historyEventFileRemoved";
    default:
      return "historyEventOther";
  }
}

export function knowledgeHistoryEventIcon(eventType: string): string {
  switch (eventType) {
    case "KnowledgeCreated":
      return "+";
    case "KnowledgePublished":
      return "✓"; // check
    case "KnowledgeArchived":
      return "▢"; // box
    case "KnowledgeUnarchived":
      return "↺"; // counterclockwise arrow
    case "KnowledgeDeleted":
      return "✕"; // x
    case "KnowledgeFileUploaded":
    case "KnowledgeFileReplaced":
    case "KnowledgeFileRemoved":
      return "📎"; // paperclip
    default:
      return "•"; // bullet
  }
}

/** Only meaningful for a KnowledgeUpdated entry — every other event type
 * carries its "what changed" in fixed old/new shapes the component reads
 * directly (status, fileName). Returns fields in a stable, form-matching
 * order, skipping anything not present in both old and new values. */
export function knowledgeHistoryDiffFields(
  entry: Pick<KnowledgeHistoryEntry, "oldValues" | "newValues">,
): Array<{ field: KnowledgeHistoryDiffField; oldValue: unknown; newValue: unknown }> {
  const { oldValues, newValues } = entry;
  if (!oldValues || !newValues) return [];
  return DIFF_FIELD_ORDER.filter((field) => field in oldValues).map((field) => ({
    field,
    oldValue: oldValues[field],
    newValue: newValues[field],
  }));
}
