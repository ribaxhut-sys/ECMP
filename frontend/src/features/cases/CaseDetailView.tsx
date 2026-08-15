"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
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
import { formatDateTime24 } from "@/shared/utils/datetime";
import { cn } from "@/shared/utils";
import { formatCmBatch1CustomerLabel } from "@/features/complaints/cmBatch1RegistrationLabels";
import { officerDisplayName } from "@/features/complaints/officerDisplayName";
import {
  Badge,
  Button,
  Card,
  CardBody,
  Empty,
  ErrorState,
  Modal,
  PageContainer,
  PageHeader,
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
import {
  getCaseHandleDecision,
  markCaseHandleClaimed,
  markCaseHandleViewed,
  rememberCaseId,
  shouldAskHandleClaim,
} from "./caseSessionRegistry";
import {
  canClose,
  canOfferResolve,
  canResolve,
  caseStatusTone,
} from "./caseStatus";
import {
  canClaimHandling,
  isHandlingReassignRole,
  sameUserId,
} from "./handlingClaim";

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

function MetaItem({
  label,
  value,
  pre,
}: {
  label: string;
  value: string;
  pre?: boolean;
}) {
  return (
    <div className="space-y-1">
      <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
        {label}
      </dt>
      <dd
        className={`text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary ${pre ? "whitespace-pre-wrap" : ""}`}
      >
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
  const tComplaints = useTranslations("complaints");
  const router = useRouter();
  const { hasPermission, user, roles } = useAuth();
  const canRead = hasPermission("complaints:read");
  const canUpdate = hasPermission("complaints:update");
  const canCreate = hasPermission("complaints:create");
  const canAct = canUpdate || canCreate;

  const [data, setData] = useState<CmCase | null>(null);
  const [customerLabel, setCustomerLabel] = useState<string | null>(null);
  const [createdByLabel, setCreatedByLabel] = useState<string | null>(null);
  const [assignedLabel, setAssignedLabel] = useState<string | null>(null);
  const [handlerLabel, setHandlerLabel] = useState<string | null>(null);
  const [directoryUsers, setDirectoryUsers] = useState<
    { id: string; label: string }[]
  >([]);
  const [reassignOpen, setReassignOpen] = useState(false);
  const [reassignUserId, setReassignUserId] = useState("");
  const [reassigning, setReassigning] = useState(false);
  const [complaintNumber, setComplaintNumber] = useState<string | null>(null);
  const [complaintStatus, setComplaintStatus] = useState<string | null>(null);
  const [complaintCreatedBy, setComplaintCreatedBy] = useState<string | null>(
    null,
  );
  const [complaintCreatedByName, setComplaintCreatedByName] = useState<
    string | null
  >(null);
  const [handlePromptOpen, setHandlePromptOpen] = useState(false);
  const [handleClaiming, setHandleClaiming] = useState(false);
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
      setComplaintStatus(complaint?.status ?? null);
      setComplaintCreatedBy(complaint?.createdBy?.trim() || null);
      setComplaintCreatedByName(complaint?.createdByName?.trim() || null);

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
      setCustomerLabel(
        formatCmBatch1CustomerLabel(
          customerName,
          customerNumber,
          caseData.customerId,
        ),
      );

      const users = usersRes?.data ?? [];
      setDirectoryUsers(
        users.map((u) => ({
          id: u.id,
          label: u.fullName?.trim() || u.username,
        })),
      );
      const findUser = (id: string | null | undefined) => {
        const key = (id || "").trim();
        if (!key) return null;
        return users.find((u) => u.id.toLowerCase() === key.toLowerCase()) ?? null;
      };

      const creator = findUser(caseData.createdBy);
      setCreatedByLabel(
        officerDisplayName(
          creator?.fullName,
          creator?.username,
          complaint?.createdByName,
        ),
      );

      const assignee = findUser(caseData.assignedUserId);
      setAssignedLabel(
        officerDisplayName(assignee?.fullName, assignee?.username),
      );
      const handler = findUser(caseData.handlingClaimedBy);
      setHandlerLabel(
        officerDisplayName(
          caseData.handlingClaimedByName,
          handler?.fullName,
          handler?.username,
        ),
      );
    } catch (err) {
      setData(null);
      setCustomerLabel(null);
      setCreatedByLabel(null);
      setAssignedLabel(null);
      setHandlerLabel(null);
      setComplaintNumber(null);
      setComplaintStatus(null);
      setComplaintCreatedBy(null);
      setComplaintCreatedByName(null);
      setError(err instanceof ApiError ? err.message : t("unableToLoad"));
    } finally {
      setLoading(false);
    }
  }, [canRead, caseId, t]);

  useEffect(() => {
    void reload();
  }, [reload]);

  useEffect(() => {
    if (loading || !data) return;
    setHandlePromptOpen(
      shouldAskHandleClaim({
        status: data.status,
        canAct,
        decision: getCaseHandleDecision(data.caseId),
        handlingClaimedBy: data.handlingClaimedBy,
        userId: user?.id,
      }),
    );
  }, [loading, data, canAct, user?.id]);

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
    ? formatDateTime24(data.createdAt) || data.createdAt
    : tCommon("emDash");
  const whenUpdated = data?.updatedAt
    ? formatDateTime24(data.updatedAt) || data.updatedAt
    : null;
  const whenClosed = data?.closedAt
    ? formatDateTime24(data.closedAt) || data.closedAt
    : null;

  const customerDisplay = customerLabel || tCommon("emDash");

  const creatorDisplay = createdByLabel || tCommon("emDash");

  const assignedDisplay = assignedLabel;

  const handlerDisplay = officerDisplayName(
    data?.handlingClaimedByName,
    handlerLabel,
  );

  const isCurrentHandler = canClaimHandling({
    handlingClaimedBy: data?.handlingClaimedBy,
    userId: user?.id,
  });
  const claimedBySomeone = Boolean(data?.handlingClaimedBy?.trim());
  const canReassign = isHandlingReassignRole(roles);

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
    data &&
      canUpdate &&
      claimedBySomeone &&
      isCurrentHandler &&
      canOfferResolve(data.status),
  );
  const showClose = Boolean(
    data &&
      canUpdate &&
      claimedBySomeone &&
      isCurrentHandler &&
      canClose(data.status),
  );
  const caseFinished =
    data?.status === "CLOSED" || data?.status === "CANCELLED";
  const parentComplaintClosed = (complaintStatus || "").toUpperCase() === "CLOSED";
  const attachmentsLocked = caseFinished || parentComplaintClosed;
  const showParentContinueLabel = Boolean(
    data && (caseFinished || data.status === "RESOLVED" || showClose),
  );
  const handleConfirmIsCreator = Boolean(
    user?.id?.trim() &&
      complaintCreatedBy?.trim() &&
      user.id.trim().toLowerCase() === complaintCreatedBy.trim().toLowerCase(),
  );

  function declineHandleClaim(): void {
    if (data) markCaseHandleViewed(data.caseId);
    setHandlePromptOpen(false);
  }

  async function acceptHandleClaim(): Promise<void> {
    if (!data || handleClaiming) return;
    if (sameUserId(data.handlingClaimedBy, user?.id)) {
      markCaseHandleClaimed(data.caseId);
      setHandlePromptOpen(false);
      return;
    }
    setHandleClaiming(true);
    try {
      await updateCmCaseStatus(data.caseId, {
        toStatus: data.status,
        reason: "HANDLE_CLAIM",
      });
      markCaseHandleClaimed(data.caseId);
      setHandlePromptOpen(false);
      await reload();
    } catch (err) {
      showErrorToast(
        err instanceof ApiError ? err.message : tComplaints("penangananLoadError"),
      );
    } finally {
      setHandleClaiming(false);
    }
  }

  async function submitReassign(): Promise<void> {
    if (!data || !reassignUserId.trim() || reassigning) return;
    setReassigning(true);
    try {
      await updateCmCaseStatus(data.caseId, {
        toStatus: data.status,
        reason: "HANDLE_REASSIGN",
        handlingClaimedBy: reassignUserId.trim(),
      });
      markCaseHandleClaimed(data.caseId);
      setReassignOpen(false);
      setReassignUserId("");
      showSuccess(tComplaints("penangananReassignDone"));
      await reload();
    } catch (err) {
      showErrorToast(
        err instanceof ApiError ? err.message : tComplaints("penangananLoadError"),
      );
    } finally {
      setReassigning(false);
    }
  }

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

  const pageTitle = !data
    ? t("detail")
    : caseFinished
      ? t("pageTitleClosed")
      : data.status === "RESOLVED"
        ? t("pageTitleResolved")
        : handlerDisplay
          ? t("pageTitleInProgress", { name: handlerDisplay })
          : t("pageTitleOpen");

  const pageDescription = !data
    ? undefined
    : caseFinished
      ? t("pageDescriptionClosed")
      : t(
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
        );

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      {data && !loading ? (
        <PageHeader
          title={pageTitle}
          description={pageDescription}
          breadcrumbs={breadcrumbs}
        />
      ) : (
        <PageHeader title={t("detail")} breadcrumbs={breadcrumbs} />
      )}

      {loading ? <Skeleton rows={6} /> : null}
      {!loading && error ? (
        <ErrorState title={t("unableToLoad")} message={error} />
      ) : null}

      {!loading && data ? (
        <div
          className="flex min-h-[50vh] flex-col gap-[var(--ecmp-section-gap)]"
          data-testid="case-detail-simple"
        >
          <section className="space-y-[var(--ecmp-panel-gap)]">
            <Card>
              <CardBody>
                <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] md:grid-cols-2">
                  <MetaItem label={t("caseNumber")} value={data.caseNumber} />
                  <div className="space-y-1">
                    <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                      {tComplaints("status")}
                    </dt>
                    <dd className="flex flex-wrap items-center gap-2">
                      <CaseStatusBadge status={data.status} />
                      <Badge tone={priorityTone(data.priority)} variant="outline">
                        {priorityLabel(data.priority)}
                      </Badge>
                    </dd>
                  </div>
                  <MetaItem
                    label={t("parentComplaint")}
                    value={complaintNumber ?? tCommon("emDash")}
                  />
                  <MetaItem
                    label={t("owningUnit")}
                    value={
                      data.owningUnitId?.trim() ||
                      data.ownerUnitId?.trim() ||
                      tCommon("emDash")
                    }
                  />
                  <MetaItem label={t("customer")} value={customerDisplay} />
                  <MetaItem
                    label={tComplaints("penangananHandler")}
                    value={handlerDisplay || tCommon("emDash")}
                  />
                  <MetaItem label={t("createdBy")} value={creatorDisplay} />
                  <MetaItem label={t("createdAt")} value={whenCreated} />
                  {assignedDisplay ? (
                    <MetaItem label={t("assignedTo")} value={assignedDisplay} />
                  ) : null}
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
                </dl>
              </CardBody>
            </Card>
          </section>

          {data.subject || data.description || data.resolution ? (
            <section className="space-y-[var(--ecmp-panel-gap)]">
              <Card>
                <CardBody className="space-y-[var(--ecmp-panel-gap)]">
                  {data.subject ? (
                    <div className="space-y-1">
                      <p className="sr-only">{t("subject")}</p>
                      <p className="text-[length:var(--ecmp-font-title-size)] font-[number:var(--ecmp-font-title-weight)] uppercase leading-[var(--ecmp-font-title-line)] tracking-tight text-ecmp-text-primary">
                        {data.subject}
                      </p>
                    </div>
                  ) : null}
                  {data.description ? (
                    <div className="space-y-1">
                      <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                        {t("description")}
                      </p>
                      <p className="whitespace-pre-wrap text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                        {data.description}
                      </p>
                    </div>
                  ) : null}
                  <div
                    className={cn(
                      "space-y-1",
                      Boolean(data.description?.trim()) &&
                        "border-t border-ecmp-border pt-[var(--ecmp-panel-gap)]",
                    )}
                  >
                    <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                      {t("resolution")}
                    </p>
                    {data.resolution ? (
                      <>
                        <div className="flex flex-wrap items-center gap-2">
                          <Badge tone={caseStatusTone(data.resolution.status)}>
                            {data.resolution.status}
                          </Badge>
                          <span className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                            {data.resolution.resolutionCode}
                          </span>
                        </div>
                        <dl className="space-y-[var(--ecmp-form-gap)]">
                          <MetaItem
                            label={t("summary")}
                            value={data.resolution.summary}
                          />
                          {data.resolution.detail ? (
                            <MetaItem
                              label={t("detailLabel")}
                              value={data.resolution.detail}
                              pre
                            />
                          ) : null}
                          <MetaItem
                            label={t("comment")}
                            value={data.resolution.comment}
                          />
                        </dl>
                      </>
                    ) : (
                      <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                        {t("noResolutionDescription")}
                      </p>
                    )}
                  </div>
                </CardBody>
              </Card>
            </section>
          ) : null}

          <CmBatch1BoundAttachmentsCard
            complaintId={data.complaintId}
            customerId={data.customerId}
            allowUpload={!attachmentsLocked}
            allowVoid={!attachmentsLocked}
          />

          <div
            className="flex flex-col-reverse gap-[var(--ecmp-form-gap)] border-t border-ecmp-border pt-[var(--ecmp-panel-gap)] sm:flex-row sm:flex-wrap sm:justify-end"
            data-testid="case-detail-actions"
          >
            <Button
              type="button"
              variant="outline"
              onClick={() => goToComplaintPenanganan()}
            >
              {showParentContinueLabel
                ? t("continueToParentComplaint")
                : t("backToComplaint")}
            </Button>
            {canReassign && claimedBySomeone && !caseFinished ? (
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setReassignUserId("");
                  setReassignOpen(true);
                }}
              >
                {tComplaints("penangananReassign")}
              </Button>
            ) : null}
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
          </div>

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
      <Modal
        open={handlePromptOpen}
        onClose={declineHandleClaim}
        title={tComplaints("handleConfirmTitle")}
        size="sm"
        footer={
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={declineHandleClaim}
              disabled={handleClaiming}
            >
              {tCommon("no")}
            </Button>
            <Button
              type="button"
              onClick={() => void acceptHandleClaim()}
              loading={handleClaiming}
            >
              {tCommon("yes")}
            </Button>
          </div>
        }
      >
        <p className="text-ecmp-text-primary">
          {handleConfirmIsCreator
            ? tComplaints("handleConfirmContinueBody")
            : tComplaints("handleConfirmTakeoverBody", {
                name:
                  complaintCreatedByName?.trim() ||
                  createdByLabel?.trim() ||
                  tCommon("emDash"),
              })}
        </p>
      </Modal>
      <Modal
        open={reassignOpen}
        onClose={() => setReassignOpen(false)}
        title={tComplaints("penangananReassignTitle")}
        size="sm"
        footer={
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setReassignOpen(false)}
              disabled={reassigning}
            >
              {tCommon("no")}
            </Button>
            <Button
              type="button"
              disabled={!reassignUserId.trim()}
              loading={reassigning}
              onClick={() => void submitReassign()}
            >
              {tCommon("yes")}
            </Button>
          </div>
        }
      >
        <p className="mb-3 text-ecmp-text-primary">
          {tComplaints("penangananReassignBody")}
        </p>
        <label className="block text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
          {tComplaints("penangananReassignPick")}
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
    </PageContainer>
  );
}
