"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { fetchAttachment } from "@/lib/api";
import type { Attachment } from "@/lib/api/types";
import { Badge } from "@/shared/ui";
import { useToast } from "@/shared/providers";
import { knowledgeTypeKey } from "@/features/knowledge/KnowledgeBadges";
import { AttachmentViewer } from "@/features/attachments/AttachmentViewer";
import {
  extractMentionRefs,
  parseKnowledgeReferenceSegments,
  type MentionKind,
} from "./knowledgeReferenceMarker";
import { resolveMentionReferenceMeta } from "./knowledgeReferenceActivity";
import { knowledgeReferenceChipClass } from "./knowledgeMentionEditor";

type MentionMeta = { active: boolean; typeLabel: string };

/**
 * Read-mode renderer for `resolutionNotes` / Catatan — plain text stays
 * plain text; each `@[title](<kind>:<id>)` marker renders as a clickable
 * italic reference (type tag + title; blue if active, red if inactive).
 * Covers all 3 mention kinds: knowledge, announcement, attachment.
 */
export function KnowledgeReferenceText({ text }: { text: string }) {
  const router = useRouter();
  const { pushError } = useToast();
  const t = useTranslations("knowledgeMention");
  const tKnowledge = useTranslations("knowledge");
  const segments = useMemo(
    () => parseKnowledgeReferenceSegments(text),
    [text],
  );
  const refs = useMemo(() => extractMentionRefs(text), [text]);
  const refsKey = refs.map((ref) => `${ref.kind}:${ref.id}`).join("|");

  const [metaByKey, setMetaByKey] = useState<Record<string, MentionMeta>>({});
  const [previewAttachment, setPreviewAttachment] = useState<Attachment | null>(
    null,
  );

  useEffect(() => {
    if (refs.length === 0) {
      setMetaByKey({});
      return;
    }
    let cancelled = false;
    for (const ref of refs) {
      const key = `${ref.kind}:${ref.id}`;
      resolveMentionReferenceMeta(ref.kind, ref.id, {
        knowledgeType: (type) => tKnowledge(knowledgeTypeKey(type)),
        announcement: t("sourceAnnouncement"),
        attachment: t("sourceAttachment"),
      })
        .then((meta) => {
          if (cancelled) return;
          setMetaByKey((prev) => ({ ...prev, [key]: meta }));
        })
        .catch(() => {
          if (cancelled) return;
          setMetaByKey((prev) => ({
            ...prev,
            [key]: { active: false, typeLabel: "" },
          }));
        });
    }
    return () => {
      cancelled = true;
    };
    // refsKey tracks identity; refs is derived from the same text.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refsKey]);

  function openAttachment(id: string) {
    fetchAttachment(id)
      .then((res) => setPreviewAttachment(res.data))
      .catch((err) => pushError(err, t("attachmentPreviewError")));
  }

  function openReference(kind: MentionKind, id: string) {
    if (kind === "knowledge") {
      router.push(`/knowledge/${id}`);
    } else if (kind === "announcement") {
      router.push(`/announcements/${id}`);
    } else {
      openAttachment(id);
    }
  }

  return (
    <span className="whitespace-pre-wrap break-words">
      {segments.map((segment, index) => {
        if (segment.type === "text") {
          return <span key={index}>{segment.value}</span>;
        }
        const meta = metaByKey[`${segment.kind}:${segment.id}`];
        const active = meta?.active ?? true;
        const title = segment.title || t("untitledReference");
        return (
          <button
            key={index}
            type="button"
            className={knowledgeReferenceChipClass(active)}
            onClick={() => openReference(segment.kind, segment.id)}
            title={active ? t("openReference") : t("inactiveReference")}
          >
            {meta?.typeLabel ? (
              <Badge
                tone={active ? "info" : "danger"}
                className="mr-1 inline-flex px-1.5 py-0 align-baseline not-italic"
              >
                {meta.typeLabel}
              </Badge>
            ) : null}
            {title}
          </button>
        );
      })}
      {previewAttachment ? (
        <AttachmentViewer
          attachment={previewAttachment}
          open
          onClose={() => setPreviewAttachment(null)}
        />
      ) : null}
    </span>
  );
}
