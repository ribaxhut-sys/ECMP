"use client";

import { useLocale, useTranslations } from "next-intl";
import { officerDisplayName } from "@/features/complaints/officerDisplayName";
import { KnowledgeReferenceText } from "@/features/complaints/KnowledgeReferenceText";
import { formatDateTime24 } from "@/shared/utils/datetime";
import { cn } from "@/shared/utils";
import {
  groupCaseHandlingNotes,
  type CaseHandlingNote,
} from "./caseHandlingNotes";

function HandlingNoteBlock({
  note,
  nested = false,
}: {
  note: CaseHandlingNote;
  nested?: boolean;
}) {
  const t = useTranslations("cases");
  const locale = useLocale();
  const label = t.has(note.labelKey as "handlingNotesTitle")
    ? t(note.labelKey as "handlingNotesTitle")
    : note.labelKey;
  const actor = officerDisplayName(note.actorName, note.actorId) || null;
  const when = note.occurredAt
    ? formatDateTime24(note.occurredAt, locale)
    : null;
  const meta = [actor, when].filter(Boolean).join(" · ");

  return (
    <div className="space-y-1">
      <p className="leading-snug">
        <span
          data-note-role="title"
          className={cn(
            "text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-primary",
            nested ? "font-medium" : "font-semibold",
          )}
        >
          {label}
        </span>
        {meta ? (
          <span className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
            {` · ${meta}`}
          </span>
        ) : null}
      </p>
      <div
        data-note-role="body"
        className="whitespace-pre-wrap text-[length:var(--ecmp-font-helper-size)] leading-snug text-ecmp-text-primary"
      >
        <KnowledgeReferenceText text={note.text} />
      </div>
    </div>
  );
}

export function CaseHandlingNotes({
  notes,
  divided,
}: {
  notes: CaseHandlingNote[];
  divided?: boolean;
}) {
  const t = useTranslations("cases");
  if (notes.length === 0) return null;
  const groups = groupCaseHandlingNotes(notes);

  return (
    <div
      className={cn(
        "space-y-[var(--ecmp-form-gap)]",
        divided && "border-t border-ecmp-border pt-[var(--ecmp-panel-gap)]",
      )}
      data-testid="case-handling-notes"
    >
      <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
        {t("handlingNotesTitle")}
      </p>
      <ol className="space-y-3">
        {groups.map((group) => (
          <li key={group.parent.key} className="space-y-2">
            <HandlingNoteBlock note={group.parent} />
            {group.children.length > 0 ? (
              <ol
                className="space-y-2 border-l border-ecmp-border/80 pl-4"
                data-testid="case-handling-note-children"
              >
                {group.children.map((child) => (
                  <li key={child.key}>
                    <HandlingNoteBlock note={child} nested />
                  </li>
                ))}
              </ol>
            ) : null}
          </li>
        ))}
      </ol>
    </div>
  );
}
