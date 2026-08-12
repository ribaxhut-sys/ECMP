"use client";

import { useCallback, useEffect, useId, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  createCmCase,
  fetchCmCases,
  type CmCaseSummary,
} from "@/lib/api";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  Empty,
  ErrorState,
  Skeleton,
} from "@/shared/ui";
import { CaseStatusBadge } from "@/features/cases/CaseStatusBadge";
import { CreateCaseDialog } from "@/features/cases/CreateCaseDialog";
import {
  mergeCreateCaseForm,
  toCreateCaseRequest,
} from "@/features/cases/caseForms";
import { rememberCaseId } from "@/features/cases/caseSessionRegistry";
import { useToast } from "@/shared/providers";
import {
  buildPenangananSummarySegments,
  isHqIntakeDisposition,
  joinPenangananSummarySegments,
  partitionPenanganan,
  penangananSummaryCounts,
  resolvePenangananContextKind,
} from "./penangananGroups";

const SECTION_ID = "penanganan";

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

function PenangananItemCard({
  item,
  indexLabel,
  showContinue,
  showEscalate,
  onContinue,
  onEscalate,
}: {
  item: CmCaseSummary;
  indexLabel: string;
  showContinue: boolean;
  showEscalate: boolean;
  onContinue: () => void;
  onEscalate: () => void;
}) {
  const t = useTranslations("complaints");
  const subject = item.subject?.trim() || t("penangananNoSubject");

  return (
    <Card>
      <CardBody className="space-y-[var(--ecmp-panel-gap)]">
        <div className="flex flex-wrap items-start justify-between gap-[var(--ecmp-form-gap)]">
          <div className="min-w-0 space-y-1">
            <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
              {indexLabel}
            </p>
            <p className="truncate font-medium text-ecmp-text-primary">
              {item.caseNumber}
            </p>
            <p className="truncate text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
              {subject}
            </p>
          </div>
          <div className="flex flex-col items-end gap-1">
            <CaseStatusBadge status={item.status} />
            <span className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
              {t(statusLabelKey(item.status), { status: item.status })}
            </span>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {showContinue ? (
            <Button type="button" onClick={onContinue}>
              {t("penangananContinue")}
            </Button>
          ) : (
            <Button type="button" variant="outline" onClick={onContinue}>
              {t("penangananView")}
            </Button>
          )}
          {showEscalate ? (
            <Button type="button" variant="outline" onClick={onEscalate}>
              {t("penangananEscalate")}
            </Button>
          ) : null}
        </div>
      </CardBody>
    </Card>
  );
}

function PenangananGroupBlock({
  title,
  items,
  baseIndex,
  continueOnOpen,
  escalateEnabled,
  onContinue,
  onEscalate,
}: {
  title: string;
  items: CmCaseSummary[];
  baseIndex: number;
  continueOnOpen: boolean;
  escalateEnabled: boolean;
  onContinue: (item: CmCaseSummary) => void;
  onEscalate: (item: CmCaseSummary) => void;
}) {
  const t = useTranslations("complaints");
  if (items.length === 0) return null;
  return (
    <div className="space-y-[var(--ecmp-panel-gap)]">
      <div className="flex flex-wrap items-center gap-2">
        <h3 className="text-[length:var(--ecmp-font-body-size)] font-semibold text-ecmp-text-primary">
          {title}
        </h3>
        <Badge tone="neutral">{items.length}</Badge>
      </div>
      <ul className="grid gap-[var(--ecmp-panel-gap)]">
        {items.map((item, i) => (
          <li key={item.caseId}>
            <PenangananItemCard
              item={item}
              indexLabel={t("penangananItemLabel", {
                n: baseIndex + i + 1,
              })}
              showContinue={continueOnOpen}
              showEscalate={escalateEnabled && continueOnOpen}
              onContinue={() => onContinue(item)}
              onEscalate={() => onEscalate(item)}
            />
          </li>
        ))}
      </ul>
    </div>
  );
}

/**
 * Complaint-scoped Penanganan list (multi-Case): open / HQ / done.
 * Presentation only — Case API remains SoT (DEC-020 coexistence).
 */
export function ComplaintPenangananSection({
  complaintId,
  complaintStatus,
  intakeDisposition,
  allowStart,
  allowEscalate,
  onRequestHqEscalation,
  manageRequestToken = 0,
  seed,
  onPenangananSnapshot,
}: {
  complaintId: string;
  complaintStatus?: string | null;
  intakeDisposition?: string | null;
  allowStart: boolean;
  allowEscalate: boolean;
  /** Complaint-level HQ escalate (Batch-1). Per-Case ESCALATED not Mode A delivery. */
  onRequestHqEscalation?: (item: CmCaseSummary) => void;
  /**
   * Increment from parent "Tangani pengaduan" — open existing case page or
   * create then navigate to `/complaints/cm/cases/{id}`.
   * Token 0 is ignored (mount).
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
  /** Notify parent so "Tangani pengaduan" can hide when open cases exist. */
  onPenangananSnapshot?: (snapshot: {
    loading: boolean;
    openCount: number;
    totalCount: number;
  }) => void;
}) {
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const router = useRouter();
  const { hasPermission } = useAuth();
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
        err instanceof ApiError ? err.message : t("penangananLoadError"),
      );
    } finally {
      setLoading(false);
    }
  }, [canRead, complaintId, t]);

  useEffect(() => {
    void load();
  }, [load]);

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

  useEffect(() => {
    onPenangananSnapshot?.({
      loading,
      openCount: counts.open,
      totalCount:
        counts.open + counts.pusat + counts.done + counts.cancelled,
    });
    // Depend on primitive count fields — `counts` is a new object each render
    // and would re-fire this effect forever, blocking App Router soft-nav.
  }, [
    loading,
    counts.open,
    counts.pusat,
    counts.done,
    counts.cancelled,
    onPenangananSnapshot,
  ]);

  function openItem(item: CmCaseSummary) {
    rememberCaseId(complaintId, item.caseId);
    router.push(
      `/complaints/cm/cases/${encodeURIComponent(item.caseId)}`,
    );
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
      pushSuccess(
        tCommon("success"),
        t("penangananCreated", { number: res.data.caseNumber }),
      );
      router.push(
        `/complaints/cm/cases/${encodeURIComponent(res.data.caseId)}`,
      );
    } catch (err) {
      pushError(err, t("penangananLoadError"));
      // Fallback: let agent fill the create dialog manually.
      setCreateOpen(true);
    } finally {
      setStarting(false);
    }
  }

  /** Parent CTA "Tangani pengaduan" → case workspace URL. */
  useEffect(() => {
    if (!manageRequestToken || loading || starting) return;
    if (error) return;
    if (parts.open.length > 0) {
      openItem(parts.open[0]!);
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
  const showEmptyHq =
    !loading && !error && contextKind === "hq_waiting" && rows.length === 0;
  const showEmptyClosed =
    !loading && !error && contextKind === "closed" && rows.length === 0;

  return (
    <section
      id={SECTION_ID}
      aria-labelledby={headingId}
      className="scroll-mt-24 space-y-[var(--ecmp-section-gap)]"
    >
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

      {!loading && !error ? (
        <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
          {contextKind === "closed" && !compactSummary
            ? t("penangananListClosed")
            : contextKind === "hq_waiting" && !compactSummary
              ? t("penangananListHqWaiting")
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
          title={t("penangananEmptyHqTitle")}
          description={t("penangananEmptyHqDescription")}
        />
      ) : null}

      {showEmptyClosed ? (
        <Alert
          tone="success"
          title={t("penangananEmptyClosedTitle")}
          description={t("penangananEmptyClosedDescription")}
        />
      ) : null}

      {complaintOnHqPath && rows.length > 0 ? (
        <Alert
          tone="info"
          title={t("penangananHqPathTitle")}
          description={t("penangananHqPathDescription")}
        />
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
          title={t("penangananEmptyHqTitle")}
          description={t("penangananEmptyHqDescription")}
        />
      ) : null}

      {!loading && !error && rows.length > 0 ? (
        <div className="space-y-[var(--ecmp-section-gap)]">
          <PenangananGroupBlock
            title={t("penangananGroupOpen")}
            items={parts.open}
            baseIndex={0}
            continueOnOpen={contextKind !== "hq_waiting"}
            escalateEnabled={Boolean(
              allowEscalate &&
                onRequestHqEscalation &&
                contextKind !== "hq_waiting",
            )}
            onContinue={openItem}
            onEscalate={handleEscalate}
          />
          <PenangananGroupBlock
            title={t("penangananGroupPusat")}
            items={parts.pusat}
            baseIndex={parts.open.length}
            continueOnOpen={false}
            escalateEnabled={false}
            onContinue={openItem}
            onEscalate={handleEscalate}
          />
          <PenangananGroupBlock
            title={t("penangananGroupDone")}
            items={parts.done}
            baseIndex={parts.open.length + parts.pusat.length}
            continueOnOpen={false}
            escalateEnabled={false}
            onContinue={openItem}
            onEscalate={handleEscalate}
          />
          <PenangananGroupBlock
            title={t("penangananGroupCancelled")}
            items={parts.cancelled}
            baseIndex={
              parts.open.length + parts.pusat.length + parts.done.length
            }
            continueOnOpen={false}
            escalateEnabled={false}
            onContinue={openItem}
            onEscalate={handleEscalate}
          />

          {allowStart && canCreate && contextKind === "has_counts" ? (
            <Button type="button" variant="secondary" onClick={() => setCreateOpen(true)}>
              {t("penangananStartAnother")}
            </Button>
          ) : null}
        </div>
      ) : null}

      <CreateCaseDialog
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        complaintId={complaintId}
        mode={rows.length > 0 ? "add" : "create"}
        onCreated={(caseData) => {
          rememberCaseId(complaintId, caseData.caseId);
          pushSuccess(
            tCommon("success"),
            t("penangananCreated", { number: caseData.caseNumber }),
          );
          setCreateOpen(false);
          void load();
          router.push(
            `/complaints/cm/cases/${encodeURIComponent(caseData.caseId)}`,
          );
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
