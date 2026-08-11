"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { IconFile } from "@/shared/icons";
import { parseKnowledgeReferenceSegments } from "./knowledgeReferenceMarker";

/**
 * Read-mode renderer for `resolutionNotes` — plain text stays plain text;
 * each `@[title](knowledge:<id>)` marker renders as a clickable reference
 * that opens the existing Knowledge detail page (which already resolves the
 * primary file via AttachmentViewer — no new file-open path here).
 */
export function KnowledgeReferenceText({ text }: { text: string }) {
  const router = useRouter();
  const t = useTranslations("knowledgeMention");
  const segments = parseKnowledgeReferenceSegments(text);

  return (
    <span className="whitespace-pre-wrap break-words">
      {segments.map((segment, index) => {
        if (segment.type === "text") {
          return <span key={index}>{segment.value}</span>;
        }
        return (
          <button
            key={index}
            type="button"
            className="mx-0.5 inline-flex items-center gap-1 rounded-[var(--ecmp-radius-sm)] bg-ecmp-primary-muted px-1.5 py-0.5 align-baseline text-[length:var(--ecmp-font-body-size)] font-medium italic text-ecmp-primary underline-offset-2 hover:underline"
            onClick={() => router.push(`/knowledge/${segment.knowledgeId}`)}
            title={t("openKnowledge")}
          >
            <IconFile className="size-3.5 shrink-0" aria-hidden />
            <span className="italic">
              {segment.title || t("untitledReference")}
            </span>
          </button>
        );
      })}
    </span>
  );
}
