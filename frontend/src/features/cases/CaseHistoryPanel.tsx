"use client";

import { useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import type { CmCaseHistoryEntry } from "@/lib/api";
import { officerDisplayName } from "@/features/complaints/officerDisplayName";
import { formatDateTime24, formatHqArrivalSlot } from "@/shared/utils/datetime";
import {
  Alert,
  Badge,
  Card,
  CardBody,
  Pagination,
  SectionHeader,
  Skeleton,
  type BadgeTone,
} from "@/shared/ui";
import {
  CASE_HISTORY_TONES,
  caseHistoryDisplayLabelKey,
  filterWpCaseHistoryEntries,
  isCaseCloseEvent,
} from "./caseHistoryMeta";

const LOG_PAGE_SIZE = 10;

const PRIORITY_KNOWN = ["LOW", "MEDIUM", "HIGH", "CRITICAL"] as const;

function priorityTone(priority: string): BadgeTone {
  const value = priority.trim().toUpperCase();
  if (value === "CRITICAL") return "danger";
  if (value === "HIGH") return "warning";
  if (value === "LOW") return "neutral";
  return "info";
}

function isKnownPriority(
  value: string,
): value is (typeof PRIORITY_KNOWN)[number] {
  return (PRIORITY_KNOWN as readonly string[]).includes(value);
}

/**
 * API-537 panel — Case chronology as a compact log.
 * Operational note bodies live in CaseHandlingNotes, not here.
 * caseNumber / status / unit are omitted (already on the Case page header).
 */
export function CaseHistoryPanel({
  entries,
  loading,
  error,
}: {
  entries: CmCaseHistoryEntry[];
  loading: boolean;
  error: string | null;
}) {
  const t = useTranslations("cases");
  const tCommon = useTranslations("common");
  const tPriority = useTranslations("priority");
  const tComplaints = useTranslations("complaints");
  const locale = useLocale();
  const [logPage, setLogPage] = useState(1);
  const visibleEntries = filterWpCaseHistoryEntries(entries);

  useEffect(() => {
    setLogPage(1);
  }, [entries]);

  function eventLabel(code: string, priorEventCodes: readonly string[]): string {
    const key = caseHistoryDisplayLabelKey(code, priorEventCodes);
    return t.has(key as "eventOther") ? t(key as "eventOther") : code;
  }

  const logTotalPages = Math.max(
    1,
    Math.ceil(visibleEntries.length / LOG_PAGE_SIZE),
  );
  const safeLogPage = Math.min(logPage, logTotalPages);
  const paged = visibleEntries.slice(
    (safeLogPage - 1) * LOG_PAGE_SIZE,
    safeLogPage * LOG_PAGE_SIZE,
  );
  const logFrom =
    visibleEntries.length === 0
      ? 0
      : (safeLogPage - 1) * LOG_PAGE_SIZE + 1;
  const logTo = Math.min(safeLogPage * LOG_PAGE_SIZE, visibleEntries.length);

  return (
    <section className="space-y-[var(--ecmp-panel-gap)]" data-testid="case-history">
      <SectionHeader
        title={t("historyTitle")}
        description={t("historyDescription")}
      />
      <Card>
        <CardBody className="space-y-[var(--ecmp-panel-gap)]">
          {loading ? <Skeleton rows={4} /> : null}
          {!loading && error ? (
            <Alert
              tone="warning"
              title={t("historyUnavailable")}
              description={t("historyUnavailableDescription")}
            />
          ) : null}
          {!loading && !error && visibleEntries.length === 0 ? (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              {t("historyEmpty")}
            </p>
          ) : null}
          {!loading && !error && visibleEntries.length > 0 ? (
            <>
              <ol className="space-y-[var(--ecmp-space-4)]">
                {paged.map((entry, index) => {
                  const number = (safeLogPage - 1) * LOG_PAGE_SIZE + index + 1;
                  const originalIndex = entries.findIndex(
                    (row) => row.entryId === entry.entryId,
                  );
                  const priorEventCodes = (
                    originalIndex >= 0 ? entries.slice(0, originalIndex) : []
                  ).map((row) => row.eventCode);
                  const arrivalSlotParts =
                    entry.eventCode === "HQ_ARRIVAL_SCHEDULED" &&
                    entry.arrivalDate?.trim() &&
                    entry.arrivalTime?.trim()
                      ? formatHqArrivalSlot(
                          entry.arrivalDate,
                          entry.arrivalTime,
                          locale,
                        )
                      : null;
                  const arrivalSlotLabel = arrivalSlotParts
                    ? tComplaints("hqArrivalSlotLabel", arrivalSlotParts)
                    : null;
                  const actor =
                    officerDisplayName(entry.actorName, entry.actorId) ||
                    tCommon("emDash");
                  const priorityKey = entry.priority?.trim().toUpperCase() ?? "";
                  const priorityLabel = priorityKey
                    ? isKnownPriority(priorityKey)
                      ? tPriority(priorityKey)
                      : entry.priority
                    : null;
                  return (
                    <li
                      key={entry.entryId}
                      className={`rounded-[var(--ecmp-radius-md)] border border-ecmp-border ${
                        number % 2 === 1
                          ? "bg-ecmp-surface"
                          : "bg-ecmp-surface-sunken"
                      }`}
                    >
                      <div className="flex w-full items-center gap-3 rounded-[var(--ecmp-radius-md)] px-3 py-1.5">
                        <span
                          aria-hidden
                          className="min-w-6 shrink-0 text-[length:var(--ecmp-font-body-size)] font-[number:var(--ecmp-font-overline-weight)] tabular-nums text-ecmp-text-secondary"
                        >
                          {number}.
                        </span>
                        <span className="flex min-w-0 flex-1 flex-wrap items-center gap-x-3 gap-y-1">
                          <Badge
                            tone={CASE_HISTORY_TONES[entry.eventCode] ?? "neutral"}
                          >
                            {eventLabel(entry.eventCode, priorEventCodes)}
                          </Badge>
                          {arrivalSlotLabel ? (
                            <span className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                              {arrivalSlotLabel}
                            </span>
                          ) : null}
                          <span className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                            {isCaseCloseEvent(entry.eventCode)
                              ? t("closedByActor", { name: actor })
                              : actor}
                          </span>
                          <span className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                            {entry.occurredAt
                              ? formatDateTime24(entry.occurredAt, locale)
                              : tCommon("emDash")}
                          </span>
                          {priorityLabel ? (
                            <Badge
                              tone={priorityTone(entry.priority ?? "")}
                              variant="solid"
                            >
                              {t("priorityTag", { value: priorityLabel })}
                            </Badge>
                          ) : null}
                        </span>
                      </div>
                    </li>
                  );
                })}
              </ol>
              {logTotalPages > 1 ? (
                <Pagination
                  summary={
                    <span>
                      {tCommon("showingItems", {
                        from: logFrom,
                        to: logTo,
                        total: visibleEntries.length,
                      })}
                      <span className="mx-2 text-ecmp-border">·</span>
                      {tCommon("pageOf", {
                        page: safeLogPage,
                        totalPages: logTotalPages,
                      })}
                    </span>
                  }
                  previousLabel={tCommon("previous")}
                  nextLabel={tCommon("next")}
                  previousDisabled={safeLogPage <= 1}
                  nextDisabled={safeLogPage >= logTotalPages}
                  onPrevious={() => setLogPage(Math.max(1, safeLogPage - 1))}
                  onNext={() =>
                    setLogPage(Math.min(logTotalPages, safeLogPage + 1))
                  }
                />
              ) : null}
            </>
          ) : null}
        </CardBody>
      </Card>
    </section>
  );
}
