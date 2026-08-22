"use client";

import { useCallback, useEffect, useId, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import {
  ApiError,
  createCmCase,
  fetchCmCases,
  fetchUsers,
  updateCmCaseStatus,
  type CmCaseSummary,
} from "@/lib/api";
import {
  Alert,
  Badge,
  Button,
  Card,
  Empty,
  ErrorState,
  Modal,
  Skeleton,
  Td,
  Th,
} from "@/shared/ui";
import { CaseStatusBadge } from "@/features/cases/CaseStatusBadge";
import { CreateCaseDialog } from "@/features/cases/CreateCaseDialog";
import { mergeCreateCaseForm, toCreateCaseRequest } from "@/features/cases/caseForms";
import { rememberCaseId, markCaseHandleClaimed } from "@/features/cases/caseSessionRegistry";
import {
  canClaimHandling,
  isHandlingReassignRole,
  sameUserId,
} from "@/features/cases/handlingClaim";
import { KnowledgeReferenceText } from "./KnowledgeReferenceText";
import { officerDisplayName } from "./officerDisplayName";
import { useToast } from "@/shared/providers";
import { formatHqArrivalSlot } from "@/shared/utils/datetime";
import {
  buildPenangananSummarySegments,
  hqPathCopyKeys,
  isHqIntakeDisposition,
  joinPenangananSummarySegments,
  partitionPenanganan,
  penangananSummaryCounts,
  resolveHqPathPhase,
  resolvePenangananContextKind,
} from "./penangananGroups";

const SECTION_ID = "penanganan";

/** Matches backend BQ-003 / MAX_CASES_PER_COMPLAINT. */
const MAX_CASES_PER_COMPLAINT = 5;

/** Query value for `/complaints/cm/[id]?focus=penanganan` deep-link. */
export const PENANGANAN_FOCUS_QUERY = "penanganan";

/** Query value for `?action=escalate` — open HQ escalate re-request when allowed. */
export const CASE_ESCALATE_ACTION_QUERY = "escalate";

function statusLabelKey(status: string): string {
  const s = status.trim().toUpperCase();
  switch (s) {
    case "CREATED":
      return "penangananStatusCreated";
    case "ASSIGNED":
      return "penangananStatusAssigned";
    case "IN_PROGRESS":
      return "penangananStatusInProgress";
    case "PENDING":
      return "penangananStatusPending";
    case "ESCALATED":
      return "penangananStatusEscalated";
    case "RESOLVED":
      return "penangananStatusResolved";
    case "CLOSED":
      return "penangananStatusClosed";
    case "CANCELLED":
      return "penangananStatusCancelled";
    default:
      return "penangananStatusUnknown";
  }
}

function PenangananGroupBlock({
  title,
  items,
  continueOnOpen,
  escalateEnabled,
  currentUserId,
  canReassign,
  handlerNames,
  onContinue,
  onView,
  onEscalate,
  onReassign,
}: {
  title: string;
  items: CmCaseSummary[];
  continueOnOpen: boolean;
  escalateEnabled: boolean;
  currentUserId: string | null;
  canReassign: boolean;
  handlerNames: Record<string, string>;
  onContinue: (item: CmCaseSummary) => void;
  onView: (item: CmCaseSummary) => void;
  onEscalate: (item: CmCaseSummary) => void;
  onReassign: (item: CmCaseSummary) => void;
}) {
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  if (items.length === 0) return null;

  return (
    <div className="space-y-[var(--ecmp-panel-gap)]">
      <div className="flex flex-wrap items-center gap-2">
        <h3 className="text-[length:var(--ecmp-font-body-size)] font-semibold text-ecmp-text-primary">
          {title}
        </h3>
        <Badge tone="neutral">{items.length}</Badge>
      </div>
      <div className="overflow-x-auto rounded-[var(--ecmp-radius-table)] border border-ecmp-border/80 bg-ecmp-surface">
        <table className="min-w-full text-left text-[length:var(--ecmp-font-body-size)]">
          <caption className="sr-only">{title}</caption>
          <thead className="border-b border-ecmp-border/80 bg-ecmp-surface-sunken/90 text-ecmp-text-secondary">
            <tr>
              <Th>{t("number")}</Th>
              <Th>{t("subject")}</Th>
              <Th>{t("status")}</Th>
              <Th>{t("penangananHandler")}</Th>
              <Th className="text-right">{tCommon("actions")}</Th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr
                key={item.caseId}
                className="border-b border-ecmp-border/50 align-middle last:border-0"
              >
                <Td>
                  <Link
                    href={`/complaints/cm/cases/${encodeURIComponent(item.caseId)}`}
                    className="font-mono text-ecmp-primary hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus"
                  >
                    {item.caseNumber}
                  </Link>
                </Td>
                <Td className="max-w-[18rem] truncate">
                  {item.subject?.trim() || t("penangananNoSubject")}
                </Td>
                <Td>
                  <div className="flex flex-wrap items-center gap-2">
                    <CaseStatusBadge status={item.status} />
                    <span className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                      {t(statusLabelKey(item.status), { status: item.status })}
                    </span>
                  </div>
                </Td>
                <Td>
                  {(() => {
                    const claimed = item.handlingClaimedBy?.trim();
                    if (!claimed) return tCommon("emDash");
                    return (
                      officerDisplayName(
                        item.handlingClaimedByName,
                        handlerNames[claimed.toLowerCase()],
                      ) || tCommon("emDash")
                    );
                  })()}
                </Td>
                <Td className="text-right">
                  <div className="flex flex-wrap justify-end gap-2">
                    {continueOnOpen &&
                    canClaimHandling({
                      handlingClaimedBy: item.handlingClaimedBy,
                      userId: currentUserId,
                    }) ? (
                      <Button
                        type="button"
                        size="sm"
                        onClick={() => onContinue(item)}
                      >
                        {t("penangananContinue")}
                      </Button>
                    ) : (
                      <Button
                        type="button"
                        size="sm"
                        variant="outline"
                        onClick={() => onView(item)}
                      >
                        {t("penangananView")}
                      </Button>
                    )}
                    {canReassign && item.handlingClaimedBy ? (
                      <Button
                        type="button"
                        size="sm"
                        variant="outline"
                        onClick={() => onReassign(item)}
                      >
                        {t("penangananReassign")}
                      </Button>
                    ) : null}
                    {escalateEnabled && continueOnOpen ? (
                      <Button
                        type="button"
                        size="sm"
                        variant="outline"
                        onClick={() => onEscalate(item)}
                      >
                        {t("penangananEscalate")}
                      </Button>
                    ) : null}
                  </div>
                </Td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/**
 * Complaint-scoped Penanganan list (multi-Case): open / HQ / done.
 * Presentation only — Case API remains SoT for penanganan (DEC-026).
 */
export function ComplaintPenangananSection({
  complaintId,
  complaintStatus,
  intakeDisposition,
  hqAcceptedAt,
  hqArrivalDate,
  hqDestinationUnitId,
  hqArrivalTime,
  hqArrivalNote,
  allowStart,
  allowEscalate,
  onRequestHqEscalation,
  manageRequestToken = 0,
  seed,
  complaintCreatedBy = null,
  complaintCreatedByName = null,
  onPenangananSnapshot,
}: {
  complaintId: string;
  complaintStatus?: string | null;
  intakeDisposition?: string | null;
  hqAcceptedAt?: string | null;
  hqArrivalDate?: string | null;
  /** Pusat unit the taxpayer reports to — shown with the slot, read-only. */
  hqDestinationUnitId?: string | null;
  hqArrivalTime?: string | null;
  hqArrivalNote?: string | null;
  allowStart: boolean;
  allowEscalate: boolean;
  /** Complaint-level HQ escalate (Batch-1). Per-Case ESCALATED not Mode A delivery. */
  onRequestHqEscalation?: (item: CmCaseSummary) => void;
  /**
   * Increment from parent "Tangani pengaduan" — create the first Case and
   * stay on this complaint, or scroll to the Case list. Token 0 is ignored.
   */
  manageRequestToken?: number;
  /** Prefill for auto-create when no open penanganan exists yet. */
  seed?: {
    category?: string | null;
    subject?: string | null;
    description?: string | null;
    priority?: string | null;
    destinationUnitId?: string | null;
  } | null;
  /** Registrant — same continue vs takeover copy as bottom "Tangani pengaduan". */
  complaintCreatedBy?: string | null;
  complaintCreatedByName?: string | null;
  /** Notify parent so the Tangani hint can distinguish first vs existing. */
  onPenangananSnapshot?: (snapshot: {
    loading: boolean;
    openCount: number;
    totalCount: number;
    handlingClaimedBy: string | null;
    handlingClaimedByName: string | null;
  }) => void;
}) {
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const locale = useLocale();
  const router = useRouter();
  const { hasPermission, user, roles } = useAuth();
  const { pushSuccess, pushError } = useToast();
  const canRead =
    hasPermission("complaints:read") || hasPermission("complaints:create");
  const canCreate = hasPermission("complaints:create");
  const headingId = useId();

  const [rows, setRows] = useState<CmCaseSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [starting, setStarting] = useState(false);
  const [continueTarget, setContinueTarget] = useState<CmCaseSummary | null>(
    null,
  );
  const [reassignTarget, setReassignTarget] = useState<CmCaseSummary | null>(
    null,
  );
  const [reassignUserId, setReassignUserId] = useState("");
  const [handlerNames, setHandlerNames] = useState<Record<string, string>>(
    {},
  );
  const [directoryUsers, setDirectoryUsers] = useState<
    { id: string; label: string }[]
  >([]);
  const canReassign = isHandlingReassignRole(roles);

  const handleConfirmIsCreator = Boolean(
    user?.id?.trim() &&
      complaintCreatedBy?.trim() &&
      user.id.trim().toLowerCase() === complaintCreatedBy.trim().toLowerCase(),
  );

  const complaintOnHqPath = isHqIntakeDisposition(intakeDisposition);

  const load = useCallback(async () => {
    if (!canRead || !complaintId.trim()) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetchCmCases({
        complaintId: complaintId.trim(),
        page: 1,
        pageSize: 50,
      });
      setRows(res.data ?? []);
    } catch (err) {
      setRows([]);
      setError(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : t("penangananLoadError"),
      );
    } finally {
      setLoading(false);
    }
  }, [canRead, complaintId, t, tErrors, tCommon]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    let cancelled = false;
    void fetchUsers({ page: 1, pageSize: 100, isActive: true })
      .then((res) => {
        if (cancelled) return;
        const map: Record<string, string> = {};
        const list: { id: string; label: string }[] = [];
        for (const u of res.data ?? []) {
          const label = u.fullName?.trim() || u.username;
          if (u.id) map[u.id.toLowerCase()] = label;
          list.push({ id: u.id, label });
        }
        setHandlerNames(map);
        setDirectoryUsers(list);
      })
      .catch(() => {
        if (!cancelled) setHandlerNames({});
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const parts = useMemo(
    () => partitionPenanganan(rows, { complaintOnHqPath }),
    [rows, complaintOnHqPath],
  );
  const counts = penangananSummaryCounts(parts);
  const contextKind = resolvePenangananContextKind({
    complaintStatus,
    intakeDisposition,
    counts: {
      open: counts.open,
      pusat: counts.pusat,
      done: counts.done,
    },
  });
  const hqPhase = resolveHqPathPhase({ intakeDisposition, hqAcceptedAt });
  const hqCopy = hqPhase ? hqPathCopyKeys(hqPhase) : null;
  const compactSummary = joinPenangananSummarySegments(
    buildPenangananSummarySegments(
      {
        open: counts.open,
        pusat: counts.pusat,
        done: counts.done,
      },
      {
        open: (n) => t("penangananSummaryOpen", { count: n }),
        pusat: (n) => t("penangananSummaryPusat", { count: n }),
        done: (n) => t("penangananSummaryDone", { count: n }),
      },
    ),
  );

  const claimedRow = complaintOnHqPath
    ? null
    : parts.open.find((row) => Boolean(row.handlingClaimedBy?.trim())) ??
      null;
  const claimedBy = claimedRow?.handlingClaimedBy?.trim() || null;

  useEffect(() => {
    onPenangananSnapshot?.({
      loading,
      openCount: counts.open,
      totalCount:
        counts.open + counts.pusat + counts.done + counts.cancelled,
      handlingClaimedBy: claimedBy,
      handlingClaimedByName: claimedBy
        ? officerDisplayName(
            claimedRow?.handlingClaimedByName,
            handlerNames[claimedBy.toLowerCase()],
          )
        : null,
    });
  }, [
    loading,
    counts.open,
    counts.pusat,
    counts.done,
    counts.cancelled,
    claimedBy,
    claimedRow?.handlingClaimedByName,
    handlerNames,
    onPenangananSnapshot,
  ]);

  async function claimHandle(item: CmCaseSummary) {
    if (sameUserId(item.handlingClaimedBy, user?.id)) {
      markCaseHandleClaimed(item.caseId);
      return;
    }
    try {
      await updateCmCaseStatus(item.caseId, {
        toStatus: item.status,
        reason: "HANDLE_CLAIM",
      });
      markCaseHandleClaimed(item.caseId);
    } catch {
      // Jejak gagal tidak boleh menahan ruang kerja.
    }
  }

  async function openItem(item: CmCaseSummary) {
    rememberCaseId(complaintId, item.caseId);
    await claimHandle(item);
    router.push(
      `/complaints/cm/cases/${encodeURIComponent(item.caseId)}`,
    );
  }

  function viewItem(item: CmCaseSummary) {
    rememberCaseId(complaintId, item.caseId);
    router.push(
      `/complaints/cm/cases/${encodeURIComponent(item.caseId)}`,
    );
  }

  function requestContinue(item: CmCaseSummary) {
    if (sameUserId(item.handlingClaimedBy, user?.id)) {
      void openItem(item);
      return;
    }
    setContinueTarget(item);
  }

  function handleEscalate(item: CmCaseSummary) {
    if (onRequestHqEscalation) {
      onRequestHqEscalation(item);
    }
  }

  async function createAndOpenCase(): Promise<void> {
    if (!allowStart || !canCreate || starting) return;
    setStarting(true);
    try {
      const category = seed?.category?.trim() || "GENERAL";
      const subject =
        seed?.subject?.trim() || t("penangananNoSubject");
      const description =
        seed?.description?.trim() ||
        seed?.subject?.trim() ||
        subject;
      const values = mergeCreateCaseForm({
        caseType: category,
        category,
        subject,
        description,
        priority: seed?.priority?.trim() || "MEDIUM",
        destinationUnitId: seed?.destinationUnitId?.trim() || "",
      });
      const res = await createCmCase(
        toCreateCaseRequest(complaintId, values),
        {
          idempotencyKey:
            typeof crypto !== "undefined" && crypto.randomUUID
              ? crypto.randomUUID()
              : undefined,
        },
      );
      rememberCaseId(complaintId, res.data.caseId);
      markCaseHandleClaimed(res.data.caseId);
      pushSuccess(
        tCommon("success"),
        t("penangananCreated", { number: res.data.caseNumber }),
      );
      await load();
      scrollToPenangananSection();
    } catch (err) {
      pushError(err, t("penangananLoadError"));
      // Fallback: let officer fill the create dialog manually.
      setCreateOpen(true);
    } finally {
      setStarting(false);
    }
  }

  /** Parent CTA "Tangani pengaduan" — stay on this complaint. */
  useEffect(() => {
    if (!manageRequestToken || loading || starting) return;
    if (error) return;
    if (parts.open.length > 0) {
      scrollToPenangananSection();
      return;
    }
    if (allowStart && canCreate && contextKind === "none") {
      void createAndOpenCase();
      return;
    }
    scrollToPenangananSection();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- signal-driven navigation
  }, [manageRequestToken, loading, error, allowStart, canCreate, contextKind, parts.open]);

  if (!canRead) return null;

  const showEmptyNone = !loading && !error && contextKind === "none";
  /** Agent CTA is bottom "Tangani pengaduan" — skip duplicate Alert/Empty. */
  const showEmptyNoneAgentCta = showEmptyNone && allowStart && canCreate;
  const showEmptyNoneReadOnly = showEmptyNone && !showEmptyNoneAgentCta;
  const showScheduledSlotCard =
    !loading && !error && hqPhase === "scheduled" && rows.length === 0;
  const showEmptyHq =
    !loading &&
    !error &&
    contextKind === "hq_waiting" &&
    rows.length === 0 &&
    !showScheduledSlotCard;
  const showEmptyClosed =
    !loading && !error && contextKind === "closed" && rows.length === 0;
  const scheduledSlotParts =
    showScheduledSlotCard && hqArrivalDate && hqArrivalTime
      ? formatHqArrivalSlot(hqArrivalDate, hqArrivalTime, locale)
      : null;
  const scheduledSlotLabel = scheduledSlotParts
    ? t("hqArrivalSlotLabel", scheduledSlotParts)
    : null;
  const scheduledWpNote = hqArrivalNote?.trim() || "";
  const canAddCase =
    allowStart &&
    canCreate &&
    !loading &&
    !error &&
    contextKind !== "closed" &&
    contextKind !== "hq_waiting" &&
    rows.length < MAX_CASES_PER_COMPLAINT;

  return (
    <section
      id={SECTION_ID}
      aria-labelledby={headingId}
      className="scroll-mt-24 space-y-[var(--ecmp-section-gap)]"
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2
            id={headingId}
            className="text-[length:var(--ecmp-font-section-title-size)] font-[number:var(--ecmp-font-section-title-weight)] leading-[var(--ecmp-font-section-title-line)] text-ecmp-text-primary"
          >
            {t("penangananTitle")}
          </h2>
          <p className="mt-1 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
            {t("penangananDescription")}
          </p>
        </div>
        {canAddCase ? (
          <Button
            type="button"
            className="shrink-0"
            onClick={() => setCreateOpen(true)}
          >
            {t("penangananAddCase")}
          </Button>
        ) : null}
      </div>

      {!loading && !error && !showScheduledSlotCard ? (
        <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
          {contextKind === "closed" && !compactSummary
            ? t("penangananListClosed")
            : contextKind === "hq_waiting" && !compactSummary
              ? t((hqCopy?.list ?? "penangananListHqWaiting") as "penangananListHqWaiting")
              : contextKind === "none"
                ? t("penangananSummaryNone")
                : (compactSummary ?? t("penangananSummaryNone"))}
        </p>
      ) : null}

      {showEmptyNoneReadOnly ? (
        <Alert
          tone="warning"
          title={t("penangananEmptyTitle")}
          description={t("penangananEmptyReadOnlyDescription")}
        />
      ) : null}

      {showEmptyHq ? (
        <Alert
          tone="info"
          title={t((hqCopy?.emptyTitle ?? "penangananEmptyHqTitle") as "penangananEmptyHqTitle")}
          description={t(
            (hqCopy?.emptyDescription ?? "penangananEmptyHqDescription") as "penangananEmptyHqDescription",
          )}
        />
      ) : null}

      {showEmptyClosed ? (
        <Alert
          tone="success"
          title={t("penangananEmptyClosedTitle")}
          description={t("penangananEmptyClosedDescription")}
        />
      ) : null}

      {complaintOnHqPath && rows.length > 0 && hqPhase !== "scheduled" ? (
        <Alert
          tone="info"
          title={t((hqCopy?.pathTitle ?? "penangananHqPathTitle") as "penangananHqPathTitle")}
          description={t(
            (hqCopy?.pathDescription ?? "penangananHqPathDescription") as "penangananHqPathDescription",
          )}
        />
      ) : null}

      {showScheduledSlotCard ? (
        <Card>
          <h3 className="text-[length:var(--ecmp-font-card-title-size)] font-[number:var(--ecmp-font-card-title-weight)] leading-[var(--ecmp-font-card-title-line)] tracking-tight text-ecmp-text-primary">
            {t(
              (hqCopy?.emptyTitle ?? "penangananEmptyHqScheduledTitle") as "penangananEmptyHqScheduledTitle",
            )}
          </h3>
          {scheduledSlotLabel ? (
            <p className="mt-2 text-[length:var(--ecmp-font-section-title-size)] font-[number:var(--ecmp-font-section-title-weight)] text-ecmp-text-primary">
              {scheduledSlotLabel}
            </p>
          ) : null}
          {hqDestinationUnitId?.trim() ? (
            <p className="mt-1 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
              {t("hqDestinationUnitValue", { unit: hqDestinationUnitId.trim() })}
            </p>
          ) : null}
          {scheduledWpNote ? (
            <div className="mt-2 whitespace-pre-wrap text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
              <KnowledgeReferenceText text={scheduledWpNote} />
            </div>
          ) : null}
          <p className="mt-2 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
            {t(
              (hqCopy?.emptyDescription ??
                "penangananEmptyHqScheduledDescription") as "penangananEmptyHqScheduledDescription",
            )}
          </p>
        </Card>
      ) : null}

      {loading ? <Skeleton rows={4} /> : null}
      {error ? (
        <ErrorState
          title={t("penangananLoadError")}
          message={error}
          onRetry={() => void load()}
        />
      ) : null}

      {showEmptyNoneReadOnly ? (
        <Empty
          title={t("penangananEmptyTitle")}
          description={t("penangananEmptyReadOnlyDescription")}
        />
      ) : null}

      {showEmptyHq ? (
        <Empty
          title={t((hqCopy?.emptyTitle ?? "penangananEmptyHqTitle") as "penangananEmptyHqTitle")}
          description={t(
            (hqCopy?.emptyDescription ?? "penangananEmptyHqDescription") as "penangananEmptyHqDescription",
          )}
        />
      ) : null}

      {!loading && !error && rows.length > 0 ? (
        <div className="space-y-[var(--ecmp-section-gap)]">
          <PenangananGroupBlock
            title={t("penangananGroupOpen")}
            items={parts.open}
            continueOnOpen={contextKind !== "hq_waiting"}
            escalateEnabled={Boolean(
              allowEscalate &&
                onRequestHqEscalation &&
                !complaintOnHqPath &&
                contextKind !== "hq_waiting",
            )}
            currentUserId={user?.id ?? null}
            canReassign={canReassign}
            handlerNames={handlerNames}
            onContinue={requestContinue}
            onView={viewItem}
            onEscalate={handleEscalate}
            onReassign={(item) => {
              setReassignUserId("");
              setReassignTarget(item);
            }}
          />
          <PenangananGroupBlock
            title={t((hqCopy?.groupPusat ?? "penangananGroupPusat") as "penangananGroupPusat")}
            items={parts.pusat}
            continueOnOpen={false}
            escalateEnabled={false}
            currentUserId={user?.id ?? null}
            canReassign={false}
            handlerNames={handlerNames}
            onContinue={requestContinue}
            onView={viewItem}
            onEscalate={handleEscalate}
            onReassign={() => undefined}
          />
          <PenangananGroupBlock
            title={t("penangananGroupDone")}
            items={parts.done}
            continueOnOpen={false}
            escalateEnabled={false}
            currentUserId={user?.id ?? null}
            canReassign={false}
            handlerNames={handlerNames}
            onContinue={requestContinue}
            onView={viewItem}
            onEscalate={handleEscalate}
            onReassign={() => undefined}
          />
          <PenangananGroupBlock
            title={t("penangananGroupCancelled")}
            items={parts.cancelled}
            continueOnOpen={false}
            escalateEnabled={false}
            currentUserId={user?.id ?? null}
            canReassign={false}
            handlerNames={handlerNames}
            onContinue={requestContinue}
            onView={viewItem}
            onEscalate={handleEscalate}
            onReassign={() => undefined}
          />
        </div>
      ) : null}

      <Modal
        open={continueTarget !== null}
        onClose={() => setContinueTarget(null)}
        title={t("handleConfirmTitle")}
        size="sm"
        footer={
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setContinueTarget(null)}
            >
              {tCommon("no")}
            </Button>
            <Button
              type="button"
              onClick={() => {
                const item = continueTarget;
                setContinueTarget(null);
                if (item) void openItem(item);
              }}
            >
              {tCommon("yes")}
            </Button>
          </div>
        }
      >
        <p className="text-ecmp-text-primary">
          {handleConfirmIsCreator
            ? t("handleConfirmContinueBody")
            : t("handleConfirmTakeoverBody", {
                name: complaintCreatedByName?.trim() || tCommon("emDash"),
              })}
        </p>
      </Modal>

      <Modal
        open={reassignTarget !== null}
        onClose={() => setReassignTarget(null)}
        title={t("penangananReassignTitle")}
        size="sm"
        footer={
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setReassignTarget(null)}
            >
              {tCommon("no")}
            </Button>
            <Button
              type="button"
              disabled={!reassignUserId.trim()}
              onClick={() => {
                const item = reassignTarget;
                const nextUser = reassignUserId.trim();
                setReassignTarget(null);
                if (!item || !nextUser) return;
                void (async () => {
                  try {
                    await updateCmCaseStatus(item.caseId, {
                      toStatus: item.status,
                      reason: "HANDLE_REASSIGN",
                      handlingClaimedBy: nextUser,
                    });
                    markCaseHandleClaimed(item.caseId);
                    pushSuccess(tCommon("success"), t("penangananReassignDone"));
                    await load();
                  } catch (err) {
                    pushError(err, t("penangananLoadError"));
                  }
                })();
              }}
            >
              {tCommon("yes")}
            </Button>
          </div>
        }
      >
        <p className="mb-3 text-ecmp-text-primary">
          {t("penangananReassignBody")}
        </p>
        <label className="block text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
          {t("penangananReassignPick")}
          <select
            className="mt-1 w-full rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface px-3 py-2 text-ecmp-text-primary"
            value={reassignUserId}
            onChange={(event) => setReassignUserId(event.target.value)}
          >
            <option value="">{tCommon("emDash")}</option>
            {directoryUsers.map((entry) => (
              <option key={entry.id} value={entry.id}>
                {entry.label}
              </option>
            ))}
          </select>
        </label>
      </Modal>

      <CreateCaseDialog
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        complaintId={complaintId}
        mode={rows.length > 0 ? "add" : "create"}
        onCreated={(caseData) => {
          rememberCaseId(complaintId, caseData.caseId);
          markCaseHandleClaimed(caseData.caseId);
          pushSuccess(
            tCommon("success"),
            t("penangananCreated", { number: caseData.caseNumber }),
          );
          setCreateOpen(false);
          void load();
        }}
      />
    </section>
  );
}

export function scrollToPenangananSection(): void {
  if (typeof document === "undefined") return;
  const el = document.getElementById(SECTION_ID);
  if (el && typeof el.scrollIntoView === "function") {
    el.scrollIntoView({ behavior: "smooth", block: "start" });
    return;
  }
  // Section may mount after Aggregate fetch — retry briefly.
  if (typeof window === "undefined" || typeof window.setTimeout !== "function") {
    return;
  }
  window.setTimeout(() => {
    const target = document.getElementById(SECTION_ID);
    if (target && typeof target.scrollIntoView === "function") {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  }, 100);
  window.setTimeout(() => {
    const target = document.getElementById(SECTION_ID);
    if (target && typeof target.scrollIntoView === "function") {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  }, 400);
}
