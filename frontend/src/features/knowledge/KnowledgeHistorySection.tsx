"use client";

import { useCallback, useEffect, useState, type ReactNode } from "react";
import { useLocale, useTranslations } from "next-intl";
import { fetchKnowledgeHistory } from "@/lib/api";
import type { KnowledgeHistoryEntry, KnowledgeType } from "@/lib/api/types";
import { formatDateTime } from "@/i18n/formatting";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { Empty, ErrorState, Skeleton, Timeline, type TimelineItem } from "@/shared/ui";
import { knowledgeTypeKey } from "./KnowledgeBadges";
import {
  knowledgeHistoryDiffFields,
  knowledgeHistoryEventIcon,
  knowledgeHistoryEventLabelKey,
  knowledgeHistoryIsPostPublish,
  type KnowledgeHistoryDiffField,
} from "./knowledgeHistory";

type Translator = ReturnType<typeof useTranslations>;

function fieldLabel(field: KnowledgeHistoryDiffField, tKnowledge: Translator): string {
  switch (field) {
    case "title":
      return tKnowledge("fieldTitleLabel");
    case "knowledgeType":
      return tKnowledge("fieldTypeLabel");
    case "documentNumber":
      return tKnowledge("fieldDocumentNumberLabel");
    case "versionLabel":
      return tKnowledge("fieldVersionLabel");
    case "summary":
      return tKnowledge("fieldSummaryLabel");
    case "effectiveFrom":
      return tKnowledge("fieldEffectiveFromLabel");
    case "effectiveTo":
      return tKnowledge("fieldEffectiveToLabel");
  }
}

function formatFieldValue(
  field: KnowledgeHistoryDiffField,
  value: unknown,
  tKnowledge: Translator,
  tCommon: Translator,
  locale: string,
): string {
  if (value == null || value === "") return tCommon("emDash");
  if (field === "knowledgeType" && typeof value === "string") {
    return tKnowledge(knowledgeTypeKey(value as KnowledgeType));
  }
  if ((field === "effectiveFrom" || field === "effectiveTo") && typeof value === "string") {
    return formatDateTime(value, locale) || tCommon("emDash");
  }
  return String(value);
}

function fileName(values: Record<string, unknown> | null): string | null {
  const name = values?.fileName;
  return typeof name === "string" ? name : null;
}

export function KnowledgeHistorySection({ knowledgeId }: { knowledgeId: string }) {
  const t = useTranslations("knowledge");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const locale = useLocale();

  const [entries, setEntries] = useState<KnowledgeHistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchKnowledgeHistory(knowledgeId);
      setEntries(res.data);
    } catch (err) {
      setEntries([]);
      setError(resolveApiErrorMessage(err, tErrors, tCommon) || t("historyLoadError"));
    } finally {
      setLoading(false);
    }
  }, [knowledgeId, t, tCommon, tErrors]);

  useEffect(() => {
    void load();
  }, [load]);

  function describeEntry(entry: KnowledgeHistoryEntry): ReactNode {
    if (entry.eventType === "KnowledgeUpdated") {
      const diffs = knowledgeHistoryDiffFields(entry);
      if (diffs.length === 0) return null;
      return (
        <ul className="space-y-0.5">
          {diffs.map((diff) => (
            <li key={diff.field}>
              <span className="font-medium">{fieldLabel(diff.field, t)}:</span>{" "}
              {formatFieldValue(diff.field, diff.oldValue, t, tCommon, locale)}
              {" → "}
              {formatFieldValue(diff.field, diff.newValue, t, tCommon, locale)}
            </li>
          ))}
        </ul>
      );
    }
    if (
      entry.eventType === "KnowledgeFileUploaded" ||
      entry.eventType === "KnowledgeFileReplaced" ||
      entry.eventType === "KnowledgeFilePrimaryChanged" ||
      entry.eventType === "KnowledgeFileRemoved"
    ) {
      const oldName = fileName(entry.oldValues);
      const newName = fileName(entry.newValues);
      if (oldName && newName) return `${oldName} → ${newName}`;
      return newName ?? oldName ?? null;
    }
    return null;
  }

  return (
    <div className="space-y-[var(--ecmp-panel-gap)]">
      {loading ? (
        <Skeleton rows={4} />
      ) : error ? (
        <ErrorState
          title={t("historyLoadError")}
          message={error}
          onRetry={() => void load()}
        />
      ) : entries.length === 0 ? (
        <Empty title={t("historyEmpty")} description={t("historyEmptyDescription")} />
      ) : (
        <Timeline
          aria-label={t("historyAriaLabel")}
          items={entries.map(
            (entry): TimelineItem => ({
              id: entry.id,
              title: t(knowledgeHistoryEventLabelKey(entry.eventType)),
              status: knowledgeHistoryIsPostPublish(entry)
                ? t("historyPostPublishBadge")
                : undefined,
              statusTone: "warning",
              actor: entry.actorName?.trim() || t("historySystemActor"),
              time: (
                <time dateTime={entry.createdAt}>
                  {formatDateTime(entry.createdAt, locale)}
                </time>
              ),
              icon: <span aria-hidden>{knowledgeHistoryEventIcon(entry.eventType)}</span>,
              description: describeEntry(entry),
            }),
          )}
        />
      )}
    </div>
  );
}
