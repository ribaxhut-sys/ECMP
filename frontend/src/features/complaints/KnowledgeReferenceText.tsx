"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { fetchKnowledge } from "@/lib/api";
import { Badge } from "@/shared/ui";
import { knowledgeTypeKey } from "@/features/knowledge/KnowledgeBadges";
import {
  extractKnowledgeIds,
  parseKnowledgeReferenceSegments,
} from "./knowledgeReferenceMarker";
import {
  isKnowledgeReferenceActive,
  type KnowledgeReferenceMeta,
} from "./knowledgeReferenceActivity";
import { knowledgeReferenceChipClass } from "./knowledgeMentionEditor";

/**
 * Read-mode renderer for `resolutionNotes` — plain text stays plain text;
 * each `@[title](knowledge:<id>)` marker renders as a clickable italic
 * reference (type tag + title; blue if active, red if inactive).
 */
export function KnowledgeReferenceText({ text }: { text: string }) {
  const router = useRouter();
  const t = useTranslations("knowledgeMention");
  const tKnowledge = useTranslations("knowledge");
  const segments = useMemo(
    () => parseKnowledgeReferenceSegments(text),
    [text],
  );
  const knowledgeIds = useMemo(() => extractKnowledgeIds(text), [text]);
  const knowledgeIdsKey = knowledgeIds.join("|");

  const [metaById, setMetaById] = useState<
    Record<string, KnowledgeReferenceMeta>
  >({});

  useEffect(() => {
    if (knowledgeIds.length === 0) {
      setMetaById({});
      return;
    }
    let cancelled = false;
    for (const id of knowledgeIds) {
      fetchKnowledge(id)
        .then((res) => {
          if (cancelled) return;
          setMetaById((prev) => ({
            ...prev,
            [id]: {
              active: isKnowledgeReferenceActive(res.data),
              knowledgeType: res.data.knowledgeType,
              status: res.data.status,
            },
          }));
        })
        .catch(() => {
          if (cancelled) return;
          setMetaById((prev) => ({
            ...prev,
            [id]: { active: false },
          }));
        });
    }
    return () => {
      cancelled = true;
    };
    // knowledgeIdsKey tracks identity; knowledgeIds is derived from the same text.
    // eslint-disable-next-line react-hooks/exhaustive-deps -- stable key from ids
  }, [knowledgeIdsKey]);

  return (
    <span className="whitespace-pre-wrap break-words">
      {segments.map((segment, index) => {
        if (segment.type === "text") {
          return <span key={index}>{segment.value}</span>;
        }
        const meta = metaById[segment.knowledgeId];
        const active = meta?.active ?? true;
        const title = segment.title || t("untitledReference");
        return (
          <button
            key={index}
            type="button"
            className={knowledgeReferenceChipClass(active)}
            onClick={() => router.push(`/knowledge/${segment.knowledgeId}`)}
            title={active ? t("openKnowledge") : t("inactiveReference")}
          >
            {meta?.knowledgeType ? (
              <Badge
                tone={active ? "info" : "danger"}
                className="mr-1 inline-flex px-1.5 py-0 align-baseline not-italic"
              >
                {tKnowledge(knowledgeTypeKey(meta.knowledgeType))}
              </Badge>
            ) : null}
            {title}
          </button>
        );
      })}
    </span>
  );
}
