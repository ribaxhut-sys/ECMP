"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { parseKnowledgeReferenceSegments } from "./knowledgeReferenceMarker";
import { knowledgeReferenceChipClassName } from "./knowledgeMentionEditor";

/**
 * Read-mode renderer for `resolutionNotes` — plain text stays plain text;
 * each `@[title](knowledge:<id>)` marker renders as a clickable italic blue
 * reference (no background; underline on hover) that opens Knowledge detail.
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
            className={knowledgeReferenceChipClassName}
            onClick={() => router.push(`/knowledge/${segment.knowledgeId}`)}
            title={t("openKnowledge")}
          >
            {segment.title || t("untitledReference")}
          </button>
        );
      })}
    </span>
  );
}
