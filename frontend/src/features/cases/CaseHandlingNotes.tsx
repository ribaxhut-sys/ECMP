"use client";

import { useLocale, useTranslations } from "next-intl";
import { officerDisplayName } from "@/features/complaints/officerDisplayName";
import { KnowledgeReferenceText } from "@/features/complaints/KnowledgeReferenceText";
import { formatDateTime24 } from "@/shared/utils/datetime";
import { cn } from "@/shared/utils";
import type { CaseHandlingNote } from "./caseHandlingNotes";

export function CaseHandlingNotes({
  notes,
  divided,
}: {
  notes: CaseHandlingNote[];
  divided?: boolean;
}) {
  const t = useTranslations("cases");
  const tCommon = useTranslations("common");
  const locale = useLocale();
  if (notes.length === 0) return null;

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
      <ol className="space-y-[var(--ecmp-form-gap)]">
        {notes.map((note) => {
          const label = t.has(note.labelKey as "handlingNotesTitle")
            ? t(note.labelKey as "handlingNotesTitle")
            : note.labelKey;
          const actor =
            officerDisplayName(note.actorName, note.actorId) || null;
          const when = note.occurredAt
            ? formatDateTime24(note.occurredAt, locale)
            : null;
          const meta = [label, actor, when].filter(Boolean).join(" · ");
          return (
            <li key={note.key} className="space-y-1">
              <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                {meta || tCommon("emDash")}
              </p>
              <div className="whitespace-pre-wrap text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                <KnowledgeReferenceText text={note.text} />
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
