"use client";

import { useCallback, useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import {
  ApiError,
  fetchCmCaseHistory,
  type CmCaseHistoryEntry,
} from "@/lib/api";
import { officerDisplayName } from "@/features/complaints/officerDisplayName";
import { KnowledgeReferenceText } from "@/features/complaints/KnowledgeReferenceText";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { formatDateTime24, formatHqArrivalSlot } from "@/shared/utils/datetime";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  Pagination,
  SectionHeader,
  Skeleton,
  WorkspaceToolbar,
  type BadgeTone,
} from "@/shared/ui";

const LOG_PAGE_SIZE = 10;

const CLOSE_EVENT_CODES = new Set(["CASE_CLOSED", "CASE_RESOLVED"]);

const HISTORY_TONES: Record<string, BadgeTone> = {
  CASE_CREATED: "primary",
  CASE_WORK_STARTED: "info",
  CASE_ASSIGNED: "primary",
  CASE_CANCELLED: "neutral",
  CASE_STATUS_CHANGED: "neutral",
  CASE_CLOSED: "success",
  CASE_RESOLVED: "success",
  HANDLING_CONTINUED: "primary",
  HANDLING_TAKEN_OVER: "primary",
  CASE_HANDLING_UNIT_ACCEPTED: "success",
  CASE_OWNER_ACCEPTED: "success",
  CASE_HANDLING_UNIT_REJECTED: "danger",
  CASE_OWNER_REJECTED: "danger",
  RESOLUTION_UPDATED: "info",
  ATTACHMENT_BOUND: "neutral",
  ATTACHMENT_UPLOADED: "neutral",
  HQ_ACCEPTED: "success",
  HQ_ARRIVAL_SCHEDULED: "info",
  HQ_RETURNED: "warning",
  OTHER: "neutral",
};

const HISTORY_LABEL_KEYS: Record<string, string> = {
  CASE_CREATED: "eventCaseCreated",
  CASE_WORK_STARTED: "eventCaseWorkStarted",
  CASE_ASSIGNED: "eventCaseAssigned",
  CASE_CANCELLED: "eventCaseCancelled",
  CASE_STATUS_CHANGED: "eventCaseStatusChanged",
  CASE_CLOSED: "eventCaseClosed",
  CASE_RESOLVED: "eventCaseResolved",
  HANDLING_CONTINUED: "eventHandlingContinued",
  HANDLING_TAKEN_OVER: "eventHandlingTakenOver",
  CASE_HANDLING_UNIT_ACCEPTED: "eventHandlingUnitAccepted",
  CASE_OWNER_ACCEPTED: "eventOwnerAccepted",
  CASE_HANDLING_UNIT_REJECTED: "eventHandlingUnitRejected",
  CASE_OWNER_REJECTED: "eventOwnerRejected",
  RESOLUTION_UPDATED: "eventResolutionUpdated",
  ATTACHMENT_BOUND: "eventAttachmentBound",
  ATTACHMENT_UPLOADED: "eventAttachmentUploaded",
  HQ_ACCEPTED: "eventHqAccepted",
  HQ_ARRIVAL_SCHEDULED: "eventHqScheduled",
  HQ_RETURNED: "eventHqReturned",
  OTHER: "eventOther",
};

const PRIORITY_KNOWN = ["LOW", "MEDIUM", "HIGH", "CRITICAL"] as const;

function priorityTone(priority: string): BadgeTone {
  const value = priority.trim().toUpperCase();
  if (value === "CRITICAL") return "danger";
  if (value === "HIGH") return "warning";
  if (value === "LOW") return "neutral";
  return "info";
}

function isCloseEvent(code: string): boolean {
  return CLOSE_EVENT_CODES.has(code.trim().toUpperCase());
}

function isKnownPriority(
  value: string,
): value is (typeof PRIORITY_KNOWN)[number] {
  return (PRIORITY_KNOWN as readonly string[]).includes(value);
}

/**
 * API-537 panel — chronology for this Case only.
 * Visual chrome matches Riwayat Pengaduan (confirmation event log).
 */
export function CaseHistoryPanel({
  caseId,
  refreshKey,
}: {
  caseId: string;
  refreshKey?: string | null;
}) {
  const t = useTranslations("cases");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const tPriority = useTranslations("priority");
  const tComplaints = useTranslations("complaints");
  const locale = useLocale();
  const [entries, setEntries] = useState<CmCaseHistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [logPage, setLogPage] = useState(1);
  const [openLogKeys, setOpenLogKeys] = useState<Set<string>>(new Set());

  const load = useCallback(async () => {
    const id = caseId.trim();
    if (!id) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetchCmCaseHistory(id);
      setEntries(res.data ?? []);
      setLogPage(1);
      setOpenLogKeys(new Set());
    } catch (err) {
      setEntries([]);
      setError(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : t("historyUnavailable"),
      );
    } finally {
      setLoading(false);
    }
  }, [caseId, t, tCommon, tErrors]);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  function eventLabel(code: string): string {
    const key = HISTORY_LABEL_KEYS[code];
    return key ? t(key) : code;
  }

  const logTotalPages = Math.max(1, Math.ceil(entries.length / LOG_PAGE_SIZE));
  const safeLogPage = Math.min(logPage, logTotalPages);
  const paged = entries.slice(
    (safeLogPage - 1) * LOG_PAGE_SIZE,
    safeLogPage * LOG_PAGE_SIZE,
  );
  const logFrom =
    entries.length === 0 ? 0 : (safeLogPage - 1) * LOG_PAGE_SIZE + 1;
  const logTo = Math.min(safeLogPage * LOG_PAGE_SIZE, entries.length);
  const allOnPageOpen =
    paged.length > 0 && paged.every((row) => openLogKeys.has(row.entryId));

  function toggleLogRow(key: string): void {
    setOpenLogKeys((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  }

  function toggleAllOnPage(): void {
    setOpenLogKeys((prev) => {
      const next = new Set(prev);
      for (const row of paged) {
        if (allOnPageOpen) next.delete(row.entryId);
        else next.add(row.entryId);
      }
      return next;
    });
  }

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
          {!loading && !error && entries.length === 0 ? (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              {t("historyEmpty")}
            </p>
          ) : null}
          {!loading && !error && entries.length > 0 ? (
            <>
              <WorkspaceToolbar
                summary={tCommon("showingItems", {
                  from: logFrom,
                  to: logTo,
                  total: entries.length,
                })}
                actions={
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={toggleAllOnPage}
                  >
                    {allOnPageOpen
                      ? t("historyCollapseAll")
                      : t("historyExpandAll")}
                  </Button>
                }
              />
              <ol className="space-y-[var(--ecmp-form-gap)]">
                {paged.map((entry, index) => {
                  const number = (safeLogPage - 1) * LOG_PAGE_SIZE + index + 1;
                  const open = openLogKeys.has(entry.entryId);
                  const note = entry.note?.trim() || null;
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
                  const expandable = Boolean(note);
                  const actor =
                    officerDisplayName(entry.actorName, entry.actorId) ||
                    tCommon("emDash");
                  const priorityKey = entry.priority?.trim().toUpperCase() ?? "";
                  const priorityLabel = priorityKey
                    ? isKnownPriority(priorityKey)
                      ? tPriority(priorityKey)
                      : entry.priority
                    : null;
                  const header = (
                    <>
                      <span
                        aria-hidden
                        className="min-w-6 shrink-0 text-[length:var(--ecmp-font-body-size)] font-[number:var(--ecmp-font-overline-weight)] tabular-nums text-ecmp-text-secondary"
                      >
                        {number}.
                      </span>
                      <span className="flex min-w-0 flex-1 flex-wrap items-center gap-x-3 gap-y-1">
                        <Badge tone={HISTORY_TONES[entry.eventCode] ?? "neutral"}>
                          {eventLabel(entry.eventCode)}
                        </Badge>
                        {arrivalSlotLabel ? (
                          <span className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                            {arrivalSlotLabel}
                          </span>
                        ) : null}
                        <span className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                          {isCloseEvent(entry.eventCode)
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
                    </>
                  );
                  return (
                    <li
                      key={entry.entryId}
                      className={`rounded-[var(--ecmp-radius-md)] border border-ecmp-border ${
                        number % 2 === 1
                          ? "bg-ecmp-surface"
                          : "bg-ecmp-surface-sunken"
                      }`}
                    >
                      {expandable ? (
                        <button
                          type="button"
                          onClick={() => toggleLogRow(entry.entryId)}
                          aria-expanded={open}
                          aria-controls={`case-log-note-${entry.entryId}`}
                          className="flex w-full items-start gap-3 rounded-[var(--ecmp-radius-md)] p-3 text-left hover:bg-ecmp-hover focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-primary"
                        >
                          {header}
                          <span className="shrink-0 text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                            {open ? t("historyHideNote") : t("historyShowNote")}
                          </span>
                        </button>
                      ) : (
                        <div className="flex w-full items-start gap-3 rounded-[var(--ecmp-radius-md)] p-3">
                          {header}
                        </div>
                      )}
                      {expandable && open ? (
                        <div
                          id={`case-log-note-${entry.entryId}`}
                          className="break-words border-t border-ecmp-border px-3 pb-3 pt-2 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary"
                        >
                          <div className="whitespace-pre-wrap">
                            <KnowledgeReferenceText text={note ?? ""} />
                          </div>
                        </div>
                      ) : null}
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
                        total: entries.length,
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
