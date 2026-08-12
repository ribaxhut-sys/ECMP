"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  fetchCmBatch1Complaint,
  fetchCmBatch1Customer360,
  fetchCmCase,
  fetchUsers,
  updateCmCaseStatus,
  type CmCase,
  type CmCaseStatus,
} from "@/lib/api";
import { formatDateTime } from "@/i18n/formatting";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  Empty,
  ErrorState,
  PageContainer,
  PageHeader,
  SectionHeader,
  Skeleton,
  Toast,
  type BadgeTone,
} from "@/shared/ui";
import { CmBatch1BoundAttachmentsCard } from "@/features/complaints/CmBatch1BoundAttachmentsCard";
import {
  CASE_ESCALATE_ACTION_QUERY,
  PENANGANAN_FOCUS_QUERY,
} from "@/features/complaints/ComplaintPenangananSection";
import { CaseStatusBadge } from "./CaseStatusBadge";
import { ResolveCaseDialog } from "./ResolveCaseDialog";
import { rememberCaseId } from "./caseSessionRegistry";
import {
  canClose,
  canOfferResolve,
  canResolve,
  caseStatusTone,
} from "./caseStatus";

function priorityTone(priority: string): BadgeTone {
  switch (priority.toUpperCase()) {
    case "CRITICAL":
      return "danger";
    case "HIGH":
      return "warning";
    case "MEDIUM":
      return "info";
    default:
      return "neutral";
  }
}

function statusAccentClass(status: CmCaseStatus | string): string {
  switch (caseStatusTone(status)) {
    case "success":
      return "border-l-ecmp-success";
    case "warning":
      return "border-l-ecmp-warning";
    case "danger":
      return "border-l-ecmp-danger";
    case "primary":
      return "border-l-ecmp-primary";
    case "info":
      return "border-l-ecmp-info";
    default:
      return "border-l-ecmp-secondary";
  }
}

function profileText(
  profile: Record<string, unknown> | null | undefined,
  ...keys: string[]
): string | null {
  if (!profile) return null;
  for (const key of keys) {
    const value = profile[key];
    if (typeof value === "string" && value.trim()) return value.trim();
  }
  return null;
}

function looksLikeUuid(value: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
    value.trim(),
  );
}

function MetaChip({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-[8rem] flex-1 rounded-[var(--ecmp-radius-md)] border border-ecmp-border/60 bg-ecmp-surface-sunken/40 px-3 py-2">
      <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
        {label}
      </p>
      <p className="mt-0.5 truncate text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary">
        {value}
      </p>
    </div>
  );
}

function MetaItem({
  label,
  value,
  wide,
}: {
  label: string;
  value: string;
  wide?: boolean;
}) {
  return (
    <div className={wide ? "space-y-1 sm:col-span-2" : "space-y-1"}>
      <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
        {label}
      </dt>
      <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
        {value}
      </dd>
    </div>
  );
}

function nextStepKey(
  status: CmCaseStatus,
  opts: {
    canUpdate: boolean;
    showResolve: boolean;
    showClose: boolean;
  },
): string {
  if (!opts.canUpdate) return "nextStepReadOnly";
  if (opts.showClose || status === "RESOLVED") return "nextStepClose";
  if (opts.showResolve || canOfferResolve(status)) {
    return "nextStepResolveOrEscalate";
  }
  if (status === "CLOSED" || status === "CANCELLED") return "nextStepDone";
  return "nextStepStart";
}

/**
 * Mode A Case detail — work surface with clear hierarchy.
 * Order: hero → next-step actions → description → resolution → attachments → technical.
 */
export function CaseDetailView({ caseId }: { caseId: string }) {
  const t = useTranslations("cases");
  const tPriority = useTranslations("priority");
  const tCommon = useTranslations("common");
  const tNav = useTranslations("nav");
  const locale = useLocale();
  const router = useRouter();
  const { hasPermission } = useAuth();
  const canRead = hasPermission("complaints:read");
  const canUpdate = hasPermission("complaints:update");

  const [data, setData] = useState<CmCase | null>(null);
  const [customerLabel, setCustomerLabel] = useState<string | null>(null);
  const [createdByLabel, setCreatedByLabel] = useState<string | null>(null);
  const [assignedLabel, setAssignedLabel] = useState<string | null>(null);
  const [complaintNumber, setComplaintNumber] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [resolveOpen, setResolveOpen] = useState(false);
  const [toastOpen, setToastOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [toastTone, setToastTone] = useState<"success" | "danger">("success");
  const [resolvePreparing, setResolvePreparing] = useState(false);

  const reload = useCallback(async () => {
    if (!canRead || !caseId.trim()) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetchCmCase(caseId.trim());
      const caseData = res.data;
      setData(caseData);
      rememberCaseId(caseData.complaintId, caseData.caseId);

      const [complaintRes, customer360Res, usersRes] = await Promise.all([
        fetchCmBatch1Complaint(caseData.complaintId).catch(() => null),
        caseData.customerId
          ? fetchCmBatch1Customer360(caseData.customerId).catch(() => null)
          : Promise.resolve(null),
        fetchUsers({ page: 1, pageSize: 100 }).catch(() => null),
      ]);

      const complaint = complaintRes?.data ?? null;
      setComplaintNumber(complaint?.complaintNumber?.trim() || null);

      const fromComplaint = complaint?.customerDisplayName?.trim() || null;
      const from360 = profileText(
        customer360Res?.data?.profile,
        "displayName",
        "fullName",
        "name",
      );
      const customerNumber =
        complaint?.customerNumber?.trim() ||
        profileText(
          customer360Res?.data?.profile,
          "customerNumber",
          "customer_number",
          "externalId",
        );
      const customerName = fromComplaint || from360;
      if (customerName) {
        setCustomerLabel(
          customerNumber && customerNumber !== customerName
            ? `${customerName} (${customerNumber})`
            : customerName,
        );
      } else if (customerNumber) {
        setCustomerLabel(customerNumber);
      } else {
        setCustomerLabel(null);
      }

      const users = usersRes?.data ?? [];
      const findUser = (id: string | null | undefined) => {
        const key = (id || "").trim();
        if (!key) return null;
        return users.find((u) => u.id === key) ?? null;
      };

      const creator = findUser(caseData.createdBy);
      setCreatedByLabel(
        creator?.fullName?.trim() ||
          creator?.username?.trim() ||
          complaint?.createdByName?.trim() ||
          null,
      );

      const assignee = findUser(caseData.assignedUserId);
      setAssignedLabel(
        assignee?.fullName?.trim() || assignee?.username?.trim() || null,
      );
    } catch (err) {
      setData(null);
      setCustomerLabel(null);
      setCreatedByLabel(null);
      setAssignedLabel(null);
      setComplaintNumber(null);
      setError(err instanceof ApiError ? err.message : t("unableToLoad"));
    } finally {
      setLoading(false);
    }
  }, [canRead, caseId, t]);

  useEffect(() => {
    void reload();
  }, [reload]);

  function showSuccess(message: string) {
    setToastTone("success");
    setToastMessage(message);
    setToastOpen(true);
  }

  function showErrorToast(message: string) {
    setToastTone("danger");
    setToastMessage(message);
    setToastOpen(true);
  }

  const whenCreated = data?.createdAt
    ? formatDateTime(data.createdAt, locale) || data.createdAt
    : tCommon("emDash");
  const whenUpdated = data?.updatedAt
    ? formatDateTime(data.updatedAt, locale) || data.updatedAt
    : null;
  const whenClosed = data?.closedAt
    ? formatDateTime(data.closedAt, locale) || data.closedAt
    : null;

  const customerDisplay =
    customerLabel ||
    (data?.customerId && !looksLikeUuid(data.customerId)
      ? data.customerId
      : tCommon("emDash"));

  const creatorDisplay =
    createdByLabel ||
    (data?.createdBy && !looksLikeUuid(data.createdBy)
      ? data.createdBy
      : tCommon("emDash"));

  const assignedDisplay =
    assignedLabel ||
    (data?.assignedUserId && !looksLikeUuid(data.assignedUserId)
      ? data.assignedUserId
      : null);

  const breadcrumbs = useMemo(
    () => [
      { label: tCommon("home"), href: "/dashboard" },
      { label: tNav("complaints"), href: "/complaints" },
      ...(data
        ? [
            {
              label: complaintNumber ?? t("backToComplaint"),
              href: `/complaints/cm/${encodeURIComponent(data.complaintId)}?focus=${PENANGANAN_FOCUS_QUERY}`,
            },
          ]
        : []),
      { label: data?.caseNumber ?? t("detailFallback") },
    ],
    [complaintNumber, data, t, tCommon, tNav],
  );

  if (!canRead) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader title={t("title")} breadcrumbs={breadcrumbs} />
        <Empty title={t("accessDenied")} description={t("readPermission")} />
      </PageContainer>
    );
  }

  const showResolve = Boolean(
    data && canUpdate && canOfferResolve(data.status),
  );
  const showClose = Boolean(data && canUpdate && canClose(data.status));
  const caseFinished =
    data?.status === "CLOSED" || data?.status === "CANCELLED";
  const showParentContinueLabel = Boolean(
    data && (caseFinished || data.status === "RESOLVED" || showClose),
  );
  const parentCtaPrimary = caseFinished;

  function goToComplaintPenanganan(opts?: { escalate?: boolean }): void {
    if (!data) return;
    const params = new URLSearchParams();
    params.set("focus", PENANGANAN_FOCUS_QUERY);
    if (opts?.escalate) {
      params.set("action", CASE_ESCALATE_ACTION_QUERY);
    }
    router.push(
      `/complaints/cm/${encodeURIComponent(data.complaintId)}?${params.toString()}`,
    );
  }

  async function ensureInProgressForResolve(
    current: CmCase,
  ): Promise<CmCase | null> {
    let next = current;
    if (next.status === "CREATED") {
      const unit = (next.owningUnitId || "").trim();
      if (!unit) {
        showErrorToast(t("resolveNeedUnit"));
        return null;
      }
      const assigned = await updateCmCaseStatus(next.caseId, {
        toStatus: "ASSIGNED",
        destinationUnitId: unit,
      });
      next = assigned.data;
      setData(next);
    }
    if (next.status === "ASSIGNED") {
      const inProgress = await updateCmCaseStatus(next.caseId, {
        toStatus: "IN_PROGRESS",
      });
      next = inProgress.data;
      setData(next);
    }
    if (!canResolve(next.status)) {
      showErrorToast(t("resolveNeedInProgress"));
      return null;
    }
    return next;
  }

  async function handleResolveClick(): Promise<void> {
    if (!data || resolvePreparing) return;
    setResolvePreparing(true);
    try {
      const ready = await ensureInProgressForResolve(data);
      if (ready) setResolveOpen(true);
    } catch (err) {
      showErrorToast(
        err instanceof ApiError ? err.message : t("resolveFailed"),
      );
    } finally {
      setResolvePreparing(false);
    }
  }

  function priorityLabel(priority: string): string {
    const key = priority.toUpperCase();
    return tPriority.has(key as "HIGH")
      ? tPriority(key as "HIGH")
      : priority;
  }

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader title={t("detail")} breadcrumbs={breadcrumbs} />

      {loading ? <Skeleton rows={6} /> : null}
      {!loading && error ? (
        <ErrorState title={t("unableToLoad")} message={error} />
      ) : null}

      {!loading && data ? (
        <div
          className="flex min-h-[50vh] flex-col gap-[var(--ecmp-section-gap)]"
          data-testid="case-detail-simple"
        >
          {/* 1. Hero identity */}
          <section
            aria-labelledby="case-identity-title"
            className={`rounded-[var(--ecmp-radius-lg)] border border-ecmp-border/70 border-l-4 bg-ecmp-surface px-4 py-4 shadow-ecmp-sm sm:px-5 ${statusAccentClass(data.status)}`}
          >
            <div className="flex flex-wrap items-center gap-2">
              <h2
                id="case-identity-title"
                className="font-mono text-[length:var(--ecmp-font-title-size)] font-[number:var(--ecmp-font-title-weight)] leading-[var(--ecmp-font-title-line)] tracking-tight text-ecmp-text-primary"
              >
                {data.caseNumber}
              </h2>
              <CaseStatusBadge status={data.status} />
              <Badge tone={priorityTone(data.priority)} variant="outline">
                {priorityLabel(data.priority)}
              </Badge>
            </div>

            <p className="mt-3 text-[length:var(--ecmp-font-subtitle-size)] font-[number:var(--ecmp-font-subtitle-weight)] leading-[var(--ecmp-font-subtitle-line)] text-ecmp-text-primary">
              {data.subject}
            </p>

            <div className="mt-4 flex flex-wrap gap-2">
              <MetaChip label={t("customer")} value={customerDisplay} />
              <MetaChip label={t("type")} value={data.caseType} />
              {assignedDisplay ? (
                <MetaChip label={t("assignedTo")} value={assignedDisplay} />
              ) : null}
              <button
                type="button"
                onClick={() => goToComplaintPenanganan()}
                className="min-w-[8rem] flex-1 rounded-[var(--ecmp-radius-md)] border border-ecmp-primary/25 bg-ecmp-primary-muted/30 px-3 py-2 text-left transition hover:border-ecmp-primary/50 hover:bg-ecmp-primary-muted/50"
              >
                <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("parentComplaint")}
                </p>
                <p className="mt-0.5 truncate text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-primary">
                  {complaintNumber ?? t("backToComplaint")}
                </p>
              </button>
            </div>
          </section>

          {/* 2. Next step + sticky actions */}
          <div
            className="sticky top-0 z-20 rounded-[var(--ecmp-radius-md)] border border-ecmp-border/70 bg-ecmp-background/95 px-4 py-3 shadow-ecmp-sm backdrop-blur-sm"
            data-testid="case-detail-actions"
          >
            <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
              {t("nextStepLabel")}
            </p>
            <p className="mt-1 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
              {t(
                nextStepKey(data.status, {
                  canUpdate,
                  showResolve,
                  showClose,
                }) as
                  | "nextStepStart"
                  | "nextStepResolveOrEscalate"
                  | "nextStepClose"
                  | "nextStepDone"
                  | "nextStepReadOnly",
              )}
            </p>
            <Alert
              className="mt-3"
              tone="info"
              title={t("caseVsComplaintTitle")}
              description={t("caseVsComplaintBody")}
            />
            <div className="mt-3 flex flex-wrap gap-2">
              {showResolve ? (
                <Button
                  type="button"
                  variant="primary"
                  loading={resolvePreparing}
                  onClick={() => {
                    void handleResolveClick();
                  }}
                >
                  {t("resolve")}
                </Button>
              ) : null}
              <Button
                type="button"
                variant={parentCtaPrimary ? "primary" : "ghost"}
                onClick={() => goToComplaintPenanganan()}
              >
                {showParentContinueLabel
                  ? t("continueToParentComplaint")
                  : t("backToComplaint")}
              </Button>
            </div>
            {showParentContinueLabel ? (
              <p className="mt-2 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                {t("continueToParentHint")}
              </p>
            ) : null}
          </div>

          {/* 3. Work content */}
          <section className="space-y-[var(--ecmp-panel-gap)]">
            <SectionHeader
              title={t("workContentTitle")}
              description={t("workContentDescription")}
            />
            <Card>
              <CardBody>
                <p className="whitespace-pre-wrap text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                  {data.description || tCommon("emDash")}
                </p>
              </CardBody>
            </Card>
          </section>

          {/* 4. Resolution */}
          {data.resolution ? (
            <section className="space-y-[var(--ecmp-panel-gap)]">
              <SectionHeader title={t("resolution")} />
              <Card>
                <CardBody className="space-y-2 text-[length:var(--ecmp-font-body-size)]">
                  <p className="text-ecmp-text-secondary">
                    {data.resolution.status} · {data.resolution.resolutionCode}
                  </p>
                  <p className="text-ecmp-text-primary">
                    {data.resolution.summary}
                  </p>
                  {data.resolution.detail ? (
                    <p className="whitespace-pre-wrap text-ecmp-text-secondary">
                      {data.resolution.detail}
                    </p>
                  ) : null}
                  <p className="text-ecmp-text-secondary">
                    {t("comment")}: {data.resolution.comment}
                  </p>
                </CardBody>
              </Card>
            </section>
          ) : null}

          {/* 5. Attachments */}
          <section className="space-y-[var(--ecmp-panel-gap)]">
            <SectionHeader
              title={t("evidenceTitle")}
              description={t("evidenceDescription")}
            />
            <CmBatch1BoundAttachmentsCard complaintId={data.complaintId} />
          </section>

          {/* 6. Technical details */}
          <details className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border/70 bg-ecmp-surface">
            <summary className="cursor-pointer select-none px-4 py-3 text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary">
              {t("technicalDetails")}
            </summary>
            <div className="border-t border-ecmp-border/60 px-4 py-4">
              <dl className="grid gap-[var(--ecmp-form-gap)] sm:grid-cols-2">
                <MetaItem label={t("type")} value={data.caseType} />
                <MetaItem
                  label={t("category")}
                  value={data.category ?? tCommon("emDash")}
                />
                <MetaItem
                  label={t("owningUnit")}
                  value={data.owningUnitId ?? tCommon("emDash")}
                />
                <MetaItem label={t("createdBy")} value={creatorDisplay} />
                <MetaItem label={t("createdAt")} value={whenCreated} />
                {whenUpdated ? (
                  <MetaItem label={t("updatedAt")} value={whenUpdated} />
                ) : null}
                {whenClosed ? (
                  <MetaItem label={t("closedAt")} value={whenClosed} />
                ) : null}
                {data.cancelReason ? (
                  <MetaItem
                    label={t("cancelReason")}
                    value={data.cancelReason}
                  />
                ) : null}
                <MetaItem label={t("caseIdLabel")} value={data.caseId} wide />
                <MetaItem
                  label={t("complaintIdLabel")}
                  value={data.complaintId}
                  wide
                />
              </dl>
            </div>
          </details>

          <ResolveCaseDialog
            open={resolveOpen}
            onClose={() => setResolveOpen(false)}
            caseId={data.caseId}
            onEscalate={() => goToComplaintPenanganan({ escalate: true })}
            onResolved={(next) => {
              setData(next);
              showSuccess(
                t("caseCreated", {
                  number: next.caseNumber,
                  status: next.status,
                }),
              );
            }}
          />
        </div>
      ) : null}

      <Toast
        open={toastOpen}
        onClose={() => setToastOpen(false)}
        title={toastTone === "success" ? t("success") : t("resolveFailed")}
        description={toastMessage}
        tone={toastTone}
      />
    </PageContainer>
  );
}
