"use client";

import { useEffect, useMemo, useState, type ReactNode } from "react";
import { useLocale, useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { useOrgUnitCode } from "@/features/announcements/useOrgUnitCode";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Empty,
  Input,
  Modal,
  ModalSection,
  PageContainer,
  PageHeader,
  Select,
  Timeline,
  Toast,
  type SelectOption,
  type TimelineItem,
} from "@/shared/ui";
import { fetchBranches, type Branch } from "@/lib/api/branches";
import { ApiError } from "@/lib/api/client";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { KnowledgeMentionTextarea } from "@/features/complaints/KnowledgeMentionTextarea";
import { KnowledgeReferenceText } from "@/features/complaints/KnowledgeReferenceText";
import {
  decideInternalTransferRequest,
  decideInternalWithdrawRequest,
  receiveInternalComplaint,
  recordInternalAcceptance,
  requestInternalTransfer,
  requestInternalWithdraw,
  resendInternalComplaintToPusat,
  resolveInternalComplaint,
  returnInternalComplaintForCompletion,
  transferInternalComplaint,
  withdrawInternalComplaint,
} from "@/lib/api/internalComplaints";
import { useInternalComplaint } from "./mock/useInternalComplaints";
import { InternalComplaintAttachmentsPanel } from "./InternalComplaintAttachments";
import { visibleInternalAcceptanceActions } from "./acceptanceGate";
import { buildInternalResolveRequest } from "./resolvePayload";
import {
  HISTORY_LABEL_KEY,
  canRequestTransfer,
  canResolve,
  canTransfer,
  hasPendingTransferRequest,
} from "./types";
import {
  InternalPriorityBadge,
  InternalStatusBadge,
} from "./components/InternalBadges";
import {
  filterInternalTransferDestinations,
  formatUnitOptionLabel,
  isAdminFamily,
} from "./transferDirection";
import {
  isAwaitingCompletion,
  mayResendToPusat,
  mayReturnForCompletion,
} from "./completionGate";
import {
  isWaitingForPusatReceive,
  mayDecideWithdraw,
  mayOwnerWithdraw,
  mayReceiveInternal,
  mayRequestWithdraw,
} from "./withdrawGate";

function formatDateTime(
  value: string | null | undefined,
  locale: string,
): string {
  if (!value) return "—";
  try {
    return new Intl.DateTimeFormat(locale, {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function displayPersonName(
  name: string | null | undefined,
  fallbackId: string | null | undefined,
  unknownLabel: string,
): string {
  const label = (name || "").trim();
  if (label) return label;
  const id = (fallbackId || "").trim();
  return id ? unknownLabel : "—";
}

function MetaItem({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <div className="min-w-0 space-y-1">
      <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
        {label}
      </dt>
      <dd className="text-sm text-ecmp-text-primary">{children}</dd>
    </div>
  );
}

type ModalKind =
  | "transfer"
  | "resolve"
  | "accept"
  | "reject"
  | "requestTransfer"
  | "decideApprove"
  | "decideReject"
  | "withdraw"
  | "requestWithdraw"
  | "decideWithdrawApprove"
  | "decideWithdrawReject"
  | "returnForCompletion"
  | "resendToPusat"
  | null;

export function InternalComplaintDetailView({ id }: { id: string }) {
  const t = useTranslations("internalComplaints");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const locale = useLocale();
  const { hasPermission, roles, userId } = useAuth();
  const actorUnitCode = useOrgUnitCode();
  const { complaint, loading, error, reload } = useInternalComplaint(id);

  const [branches, setBranches] = useState<Branch[]>([]);
  const [modal, setModal] = useState<ModalKind>(null);
  const [destinationUnitId, setDestinationUnitId] = useState("");
  const [transferReason, setTransferReason] = useState("");
  const [resolveSummary, setResolveSummary] = useState("");
  const [resolveComment, setResolveComment] = useState("");
  const [resolveFieldError, setResolveFieldError] = useState<
    "resolutionSummaryRequiredError" | "commentRequiredError" | null
  >(null);
  const [acceptParty, setAcceptParty] = useState<"OWNER" | "HANDLING_UNIT">(
    "OWNER",
  );
  const [acceptNote, setAcceptNote] = useState("");
  const [requestDestinationUnitId, setRequestDestinationUnitId] = useState("");
  const [requestReasonText, setRequestReasonText] = useState("");
  const [decisionReason, setDecisionReason] = useState("");
  const [cancelReason, setCancelReason] = useState("");
  const [completionReason, setCompletionReason] = useState("");
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchBranches(100)
      .then((res) => setBranches(res.data ?? []))
      .catch(() => setBranches([]));
  }, []);

  const activityItems: TimelineItem[] = useMemo(() => {
    const unknown = t("unknownUser");
    return (complaint?.history ?? [])
      .slice()
      .reverse()
      .map((event) => {
        const actorName = displayPersonName(
          event.actorName,
          event.actorId,
          unknown,
        );
        const unitMove =
          event.sourceUnitId &&
          event.targetUnitId &&
          event.sourceUnitId !== event.targetUnitId
            ? `${event.sourceUnitId} → ${event.targetUnitId}`
            : null;
        return {
          id: event.eventId,
          title: t(HISTORY_LABEL_KEY[event.eventType] ?? "activityCREATED"),
          description:
            event.note || unitMove ? (
              <>
                {event.note ? <KnowledgeReferenceText text={event.note} /> : null}
                {event.note && unitMove ? " · " : null}
                {unitMove}
              </>
            ) : undefined,
          time: formatDateTime(event.occurredAt, locale),
          actor: t("historyActor", { name: actorName }),
        };
      });
  }, [complaint, t, locale]);

  const actorIsAdmin = isAdminFamily(roles);
  const unitOptions: SelectOption[] = useMemo(() => {
    if (actorUnitCode === undefined) return [];
    return filterInternalTransferDestinations(branches, {
      actorUnitId: actorUnitCode,
      handlingUnitId: complaint?.handlingUnitId,
      actorIsAdmin,
    }).map((b) => ({
      value: b.code,
      label: formatUnitOptionLabel(b.code, b.name),
    }));
  }, [
    actorIsAdmin,
    actorUnitCode,
    branches,
    complaint?.handlingUnitId,
  ]);

  if (loading) {
    return (
      <PageContainer>
        <Empty title={tCommon("loading")} description="" />
      </PageContainer>
    );
  }

  if (!complaint || error) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader
          title={t("detailFallback")}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: t("title"), href: "/internal" },
            { label: t("listTitle"), href: "/internal/complaints" },
          ]}
        />
        <Empty
          title={t("detailFallback")}
          description={error ?? t("listEmptyDescription")}
        />
      </PageContainer>
    );
  }

  async function run(action: () => Promise<unknown>, okMessage: string) {
    setBusy(true);
    setActionError(null);
    try {
      await action();
      setModal(null);
      setToastMessage(okMessage);
      reload();
    } catch (err) {
      setActionError(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : t("actionFailed"),
      );
    } finally {
      setBusy(false);
    }
  }

  const complaintId = complaint.id;

  function submitResolve(action: "PROPOSE" | "ACCEPT") {
    const payload = buildInternalResolveRequest({
      action,
      summary: resolveSummary,
      comment: resolveComment,
    });
    if (!payload.ok) {
      setResolveFieldError(payload.error);
      return;
    }
    setResolveFieldError(null);
    void run(
      () => resolveInternalComplaint(complaintId, payload.body),
      action === "PROPOSE" ? t("proposeOk") : t("resolveOk"),
    );
  }

  const canAssign = hasPermission("complaints:assign");
  const canDecideTransferRequest = hasPermission("internal:escalate-decide");
  const canUpdate = hasPermission("complaints:update");
  const waitingForPusat = isWaitingForPusatReceive({
    status: complaint.status,
    ownerUnitId: complaint.ownerUnitId,
    handlingUnitId: complaint.handlingUnitId,
  });
  const ownerMayWithdraw = mayOwnerWithdraw({
    roles,
    actorUserId: userId ?? "",
    creatorUserId: complaint.createdBy,
    actorUnitCode: actorUnitCode ?? null,
    ownerUnitId: complaint.ownerUnitId,
    hasAssignPermission: canAssign,
  });
  const showReceive = mayReceiveInternal({
    status: complaint.status,
    actorUnitCode: actorUnitCode ?? null,
    handlingUnitId: complaint.handlingUnitId,
    hasUpdatePermission: canUpdate,
    completionRequestStatus: complaint.completionRequestStatus,
  });
  const awaitingCompletion = isAwaitingCompletion(
    complaint.completionRequestStatus,
  );
  const showReturn = mayReturnForCompletion({
    status: complaint.status,
    actorUnitCode: actorUnitCode ?? null,
    ownerUnitId: complaint.ownerUnitId,
    handlingUnitId: complaint.handlingUnitId,
    hasUpdatePermission: canUpdate,
    completionRequestStatus: complaint.completionRequestStatus,
  });
  const showResend = mayResendToPusat({
    status: complaint.status,
    actorUnitCode: actorUnitCode ?? null,
    ownerUnitId: complaint.ownerUnitId,
    handlingUnitId: complaint.handlingUnitId,
    hasUpdatePermission: canUpdate,
    completionRequestStatus: complaint.completionRequestStatus,
  });
  const showWithdraw =
    (waitingForPusat || awaitingCompletion) && ownerMayWithdraw && canUpdate;
  const showRequestWithdraw = mayRequestWithdraw({
    status: complaint.status,
    ownerUnitId: complaint.ownerUnitId,
    handlingUnitId: complaint.handlingUnitId,
    withdrawRequestStatus: complaint.withdrawRequestStatus,
    roles,
    actorUserId: userId ?? "",
    creatorUserId: complaint.createdBy,
    actorUnitCode: actorUnitCode ?? null,
    hasAssignPermission: canAssign,
  }) && canUpdate;
  const showDecideWithdraw = mayDecideWithdraw({
    withdrawRequestStatus: complaint.withdrawRequestStatus,
    roles,
    actorUnitCode: actorUnitCode ?? null,
    handlingUnitId: complaint.handlingUnitId,
    hasAssignPermission: canAssign,
    hasEscalateDecidePermission: canDecideTransferRequest,
  });
  const showTransfer =
    canTransfer(complaint.status) &&
    canAssign &&
    unitOptions.length > 0 &&
    !awaitingCompletion;
  const showResolve = canResolve(complaint.status) && hasPermission("complaints:update");
  const acceptanceActions = visibleInternalAcceptanceActions({
    status: complaint.status,
    hasUpdatePermission: hasPermission("complaints:update"),
    actorUnitReady: actorUnitCode !== undefined && Boolean(userId),
    roles,
    actorUnitCode: actorUnitCode ?? null,
    ownerUnitId: complaint.ownerUnitId,
    handlingUnitId: complaint.handlingUnitId,
    actorUserId: userId ?? "",
    creatorUserId: complaint.createdBy,
    handlingUnitAcceptance: complaint.handlingUnitAcceptance,
    ownerAcceptance: complaint.ownerAcceptance,
  });
  const showAcceptHandling = acceptanceActions.acceptHandling;
  const showAcceptOwner = acceptanceActions.acceptOwner;
  const rejectParties = acceptanceActions.rejectParties;
  const showReject = rejectParties.length > 0;
  const rejectPartyLocked = rejectParties.length === 1;
  const localClosure = acceptanceActions.gate === "local";
  const showClosureHint = complaint.status === "RESOLVED";
  // Agent-family: request instead of direct transfer, and may re-apply after reject.
  const showRequestTransfer =
    !canAssign &&
    hasPermission("complaints:create") &&
    canRequestTransfer(complaint) &&
    unitOptions.length > 0;
  const showReapplyTransfer =
    !canAssign &&
    hasPermission("complaints:create") &&
    complaint.transferRequestStatus === "REJECTED" &&
    complaint.status === "CREATED" &&
    complaint.handlingUnitId === complaint.ownerUnitId &&
    unitOptions.length > 0;
  const showDecideTransferRequest =
    canDecideTransferRequest && hasPendingTransferRequest(complaint);

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={complaint.number}
        description={complaint.title}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title"), href: "/internal" },
          { label: t("listTitle"), href: "/internal/complaints" },
          { label: complaint.number },
        ]}
        actions={
          <div className="flex flex-wrap gap-2">
            {showRequestTransfer ? (
              <Button
                type="button"
                variant="secondary"
                disabled={busy}
                onClick={() => {
                  setRequestDestinationUnitId("");
                  setRequestReasonText("");
                  setModal("requestTransfer");
                }}
              >
                {t("requestTransfer")}
              </Button>
            ) : null}
            {showReapplyTransfer ? (
              <Button
                type="button"
                variant="secondary"
                disabled={busy}
                onClick={() => {
                  setRequestDestinationUnitId(
                    complaint.transferRequestDestinationUnitId ?? "",
                  );
                  setRequestReasonText("");
                  setModal("requestTransfer");
                }}
              >
                {t("reapplyTransfer")}
              </Button>
            ) : null}
            {showDecideTransferRequest ? (
              <>
                <Button
                  type="button"
                  disabled={busy}
                  onClick={() => {
                    setDecisionReason("");
                    setModal("decideApprove");
                  }}
                >
                  {t("approveTransferRequest")}
                </Button>
                <Button
                  type="button"
                  variant="danger"
                  disabled={busy}
                  onClick={() => {
                    setDecisionReason("");
                    setModal("decideReject");
                  }}
                >
                  {t("rejectTransferRequest")}
                </Button>
              </>
            ) : null}
            {showWithdraw ? (
              <Button
                type="button"
                variant="danger"
                disabled={busy}
                onClick={() => {
                  setCancelReason("");
                  setModal("withdraw");
                }}
              >
                {t("withdraw")}
              </Button>
            ) : null}
            {showRequestWithdraw ? (
              <Button
                type="button"
                variant="secondary"
                disabled={busy}
                onClick={() => {
                  setCancelReason("");
                  setModal("requestWithdraw");
                }}
              >
                {t("requestWithdraw")}
              </Button>
            ) : null}
            {showDecideWithdraw ? (
              <>
                <Button
                  type="button"
                  disabled={busy}
                  onClick={() => {
                    setDecisionReason("");
                    setModal("decideWithdrawApprove");
                  }}
                >
                  {t("approveWithdrawRequest")}
                </Button>
                <Button
                  type="button"
                  variant="danger"
                  disabled={busy}
                  onClick={() => {
                    setDecisionReason("");
                    setModal("decideWithdrawReject");
                  }}
                >
                  {t("rejectWithdrawRequest")}
                </Button>
              </>
            ) : null}
            {showReceive ? (
              <Button
                type="button"
                disabled={busy}
                onClick={() =>
                  run(
                    () => receiveInternalComplaint(complaint.id),
                    t("receivedOk"),
                  )
                }
              >
                {t("receive")}
              </Button>
            ) : null}
            {showReturn ? (
              <Button
                type="button"
                variant="secondary"
                disabled={busy}
                onClick={() => {
                  setCompletionReason("");
                  setModal("returnForCompletion");
                }}
              >
                {t("returnForCompletion")}
              </Button>
            ) : null}
            {showResend ? (
              <Button
                type="button"
                disabled={busy}
                onClick={() => {
                  setCompletionReason("");
                  setModal("resendToPusat");
                }}
              >
                {t("resendToPusat")}
              </Button>
            ) : null}
            {showTransfer ? (
              <Button
                type="button"
                variant="secondary"
                disabled={busy}
                onClick={() => setModal("transfer")}
              >
                {t("transfer")}
              </Button>
            ) : null}
            {showResolve ? (
              <Button
                type="button"
                disabled={busy}
                onClick={() => {
                  setResolveFieldError(null);
                  setModal("resolve");
                }}
              >
                {t("resolve")}
              </Button>
            ) : null}
            {showAcceptHandling ? (
              <Button
                type="button"
                disabled={busy}
                onClick={() => {
                  setAcceptParty("HANDLING_UNIT");
                  setAcceptNote("");
                  setModal("accept");
                }}
              >
                {t("acceptHandling")}
              </Button>
            ) : null}
            {showAcceptOwner ? (
              <Button
                type="button"
                disabled={busy}
                onClick={() => {
                  setAcceptParty("OWNER");
                  setAcceptNote("");
                  setModal("accept");
                }}
              >
                {localClosure ? t("acceptLocal") : t("acceptOwner")}
              </Button>
            ) : null}
            {showReject ? (
              <Button
                type="button"
                variant="danger"
                disabled={busy}
                onClick={() => {
                  setAcceptParty(rejectParties[0] ?? "HANDLING_UNIT");
                  setAcceptNote("");
                  setModal("reject");
                }}
              >
                {t("rejectReturnToHandling")}
              </Button>
            ) : null}
          </div>
        }
      />

      {actionError ? <Alert tone="danger" title={actionError} /> : null}
      {waitingForPusat && showWithdraw ? (
        <Alert tone="info" title={t("waitingForPusatReceiveHint")} />
      ) : null}
      {awaitingCompletion && showResend ? (
        <Alert tone="warning" title={t("awaitingCompletionHint")} />
      ) : null}
      {awaitingCompletion && !showResend ? (
        <Alert tone="info" title={t("awaitingCompletionViewerHint")} />
      ) : null}
      {showDecideWithdraw ? (
        <Alert tone="warning" title={t("pendingWithdrawRequestHint")} />
      ) : null}
      {showRequestWithdraw && complaint.withdrawRequestStatus === "REJECTED" ? (
        <Alert tone="info" title={t("requestWithdrawHint")} />
      ) : null}
      {showClosureHint ? (
        <Alert
          tone="info"
          title={
            localClosure ? t("closureHintLocal") : t("closureHintTransferred")
          }
        />
      ) : null}

      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>{t("sectionBasics")}</CardTitle>
          </CardHeader>
          <CardBody className="space-y-4 text-sm">
            <dl className="grid grid-cols-1 gap-x-6 gap-y-3 md:grid-cols-2">
              <MetaItem label={t("status")}>
                <div className="flex flex-wrap gap-2">
                  <InternalStatusBadge status={complaint.status} />
                  <InternalPriorityBadge priority={complaint.priority} />
                </div>
              </MetaItem>
              <MetaItem label={t("relatedComplaint")}>
                {complaint.relatedComplaintNumber || tCommon("emDash")}
              </MetaItem>
              <MetaItem label={t("ownerUnit")}>{complaint.ownerUnitId}</MetaItem>
              <MetaItem label={t("handlingUnit")}>
                {complaint.handlingUnitId}
              </MetaItem>
              {awaitingCompletion ? (
                <MetaItem label={t("completionReturnReason")}>
                  {complaint.completionReturnReason || tCommon("emDash")}
                </MetaItem>
              ) : null}
              <MetaItem label={t("handlingAcceptance")}>
                {complaint.handlingUnitAcceptance === "ACCEPT"
                  ? t("acceptanceAccepted")
                  : complaint.handlingUnitAcceptance === "REJECT"
                    ? t("acceptanceRejected")
                    : tCommon("emDash")}
              </MetaItem>
              <MetaItem label={t("ownerAcceptance")}>
                {complaint.ownerAcceptance === "ACCEPT"
                  ? t("acceptanceAccepted")
                  : complaint.ownerAcceptance === "REJECT"
                    ? t("acceptanceRejected")
                    : tCommon("emDash")}
              </MetaItem>
              <MetaItem label={t("createdBy")}>
                {displayPersonName(
                  complaint.createdByName,
                  complaint.createdBy,
                  t("unknownUser"),
                )}
              </MetaItem>
              <MetaItem label={t("createdAt")}>
                {formatDateTime(complaint.createdAt, locale)}
              </MetaItem>
            </dl>
            {complaint.closedAt ? (
              <dl className="grid grid-cols-1 gap-x-6 gap-y-3 md:grid-cols-2">
                <MetaItem label={t("closedBy")}>
                  {displayPersonName(
                    complaint.closedByName,
                    complaint.closedBy,
                    t("unknownUser"),
                  )}
                </MetaItem>
                <MetaItem label={t("closedAt")}>
                  {formatDateTime(complaint.closedAt, locale)}
                </MetaItem>
              </dl>
            ) : null}
            {complaint.resolutionSummary ? (
              <dl>
                <MetaItem label={t("resolutionSummary")}>
                  {complaint.resolutionSummary}
                </MetaItem>
              </dl>
            ) : null}
            {complaint.withdrawRequestStatus ? (
              <div className="mt-2 space-y-1 rounded-md border border-ecmp-border p-3">
                <p className="font-medium">
                  {t("withdrawRequestSectionTitle")}:{" "}
                  {t(`withdrawRequestStatus${complaint.withdrawRequestStatus}`)}
                </p>
                <p>
                  <span className="text-ecmp-text-secondary">{t("reason")}: </span>
                  {complaint.withdrawRequestReason ?? "—"}
                </p>
                <p>
                  <span className="text-ecmp-text-secondary">
                    {t("requestedBy")}:{" "}
                  </span>
                  {displayPersonName(
                    complaint.withdrawRequestedByName,
                    complaint.withdrawRequestedBy,
                    t("unknownUser"),
                  )}
                </p>
                {complaint.withdrawRequestStatus !== "PENDING" ? (
                  <>
                    <p>
                      <span className="text-ecmp-text-secondary">
                        {t("decidedBy")}:{" "}
                      </span>
                      {displayPersonName(
                        complaint.withdrawDecidedByName,
                        complaint.withdrawDecidedBy,
                        t("unknownUser"),
                      )}
                    </p>
                    {complaint.withdrawDecisionReason ? (
                      <p>
                        <span className="text-ecmp-text-secondary">
                          {t("decisionReason")}:{" "}
                        </span>
                        {complaint.withdrawDecisionReason}
                      </p>
                    ) : null}
                  </>
                ) : null}
              </div>
            ) : null}
            {complaint.status === "WITHDRAWN" && complaint.withdrawReason ? (
              <dl>
                <MetaItem label={t("withdrawReason")}>
                  {complaint.withdrawReason}
                </MetaItem>
              </dl>
            ) : null}
            {complaint.transferRequestStatus ? (
              <div className="mt-2 space-y-1 rounded-md border border-ecmp-border p-3">
                <p className="font-medium">
                  {t("transferRequestSectionTitle")}:{" "}
                  {t(`transferRequestStatus${complaint.transferRequestStatus}`)}
                </p>
                <p>
                  <span className="text-ecmp-text-secondary">
                    {t("destinationUnit")}:{" "}
                  </span>
                  {complaint.transferRequestDestinationUnitId ?? "—"}
                </p>
                <p>
                  <span className="text-ecmp-text-secondary">{t("reason")}: </span>
                  {complaint.transferRequestReason ?? "—"}
                </p>
                <p>
                  <span className="text-ecmp-text-secondary">
                    {t("requestedBy")}:{" "}
                  </span>
                  {displayPersonName(
                    complaint.transferRequestedByName,
                    complaint.transferRequestedBy,
                    t("unknownUser"),
                  )}
                </p>
                {complaint.transferRequestStatus !== "PENDING" ? (
                  <>
                    <p>
                      <span className="text-ecmp-text-secondary">
                        {t("decidedBy")}:{" "}
                      </span>
                      {displayPersonName(
                        complaint.transferDecidedByName,
                        complaint.transferDecidedBy,
                        t("unknownUser"),
                      )}
                    </p>
                    {complaint.transferDecisionReason ? (
                      <p>
                        <span className="text-ecmp-text-secondary">
                          {t("decisionReason")}:{" "}
                        </span>
                        {complaint.transferDecisionReason}
                      </p>
                    ) : null}
                  </>
                ) : null}
              </div>
            ) : null}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t("sectionNarrative")}</CardTitle>
          </CardHeader>
          <CardBody className="space-y-3 text-sm whitespace-pre-wrap">
            <div>
              <div className="text-ecmp-text-secondary">{t("description")}</div>
              <div>
                <KnowledgeReferenceText text={complaint.description} />
              </div>
            </div>
            {complaint.chronology ? (
              <div>
                <div className="text-ecmp-text-secondary">{t("chronology")}</div>
                <div>
                  <KnowledgeReferenceText text={complaint.chronology} />
                </div>
              </div>
            ) : null}
            {complaint.impact ? (
              <div>
                <div className="text-ecmp-text-secondary">{t("impact")}</div>
                <div>
                  <KnowledgeReferenceText text={complaint.impact} />
                </div>
              </div>
            ) : null}
          </CardBody>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t("sectionAttachments")}</CardTitle>
        </CardHeader>
        <CardBody>
          <InternalComplaintAttachmentsPanel
            complaintId={complaint.id}
            canUpload={hasPermission("attachment:create")}
          />
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t("history")}</CardTitle>
        </CardHeader>
        <CardBody>
          {activityItems.length === 0 ? (
            <Empty title={t("historyEmpty")} description="" />
          ) : (
            <Timeline items={activityItems} />
          )}
        </CardBody>
      </Card>

      <Modal
        open={modal === "transfer"}
        onClose={() => setModal(null)}
        title={t("transfer")}
      >
        <ModalSection className="space-y-3">
          <Select
            label={t("destinationUnit")}
            options={unitOptions}
            value={destinationUnitId}
            onChange={(e) => setDestinationUnitId(e.target.value)}
            hint={t("transferDirectionHint")}
          />
          <KnowledgeMentionTextarea
            label={t("reason")}
            value={transferReason}
            onChange={setTransferReason}
          />
          <Button
            type="button"
            disabled={busy || !destinationUnitId}
            onClick={() =>
              run(
                () =>
                  transferInternalComplaint(complaint.id, {
                    destinationUnitId,
                    reason: transferReason || null,
                  }),
                t("transferOk"),
              )
            }
          >
            {t("transfer")}
          </Button>
        </ModalSection>
      </Modal>

      <Modal
        open={modal === "requestTransfer"}
        onClose={() => setModal(null)}
        title={t("requestTransfer")}
      >
        <ModalSection className="space-y-3">
          <Select
            label={t("destinationUnit")}
            options={unitOptions}
            value={requestDestinationUnitId}
            onChange={(e) => setRequestDestinationUnitId(e.target.value)}
            hint={t("transferRequestHint")}
          />
          <KnowledgeMentionTextarea
            label={t("requestReason")}
            value={requestReasonText}
            onChange={setRequestReasonText}
            hint={t("requestReasonHint")}
            required
          />
          <Button
            type="button"
            disabled={
              busy || !requestDestinationUnitId || !requestReasonText.trim()
            }
            onClick={() =>
              run(
                () =>
                  requestInternalTransfer(complaint.id, {
                    destinationUnitId: requestDestinationUnitId,
                    reason: requestReasonText.trim(),
                  }),
                t("requestTransferOk"),
              )
            }
          >
            {t("submit")}
          </Button>
        </ModalSection>
      </Modal>

      <Modal
        open={modal === "decideApprove" || modal === "decideReject"}
        onClose={() => setModal(null)}
        title={
          modal === "decideReject"
            ? t("rejectTransferRequest")
            : t("approveTransferRequest")
        }
      >
        <ModalSection className="space-y-3">
          <p className="text-sm text-ecmp-text-secondary">
            {t("transferRequestDecidePrompt", {
              destination: complaint.transferRequestDestinationUnitId ?? "—",
              reason: complaint.transferRequestReason ?? "—",
            })}
          </p>
          <KnowledgeMentionTextarea
            label={t("decisionReason")}
            value={decisionReason}
            onChange={setDecisionReason}
            hint={
              modal === "decideReject"
                ? t("decisionReasonRequiredHint")
                : t("decisionReasonOptionalHint")
            }
          />
          <Button
            type="button"
            variant={modal === "decideReject" ? "danger" : "primary"}
            disabled={
              busy || (modal === "decideReject" && !decisionReason.trim())
            }
            onClick={() =>
              run(
                () =>
                  decideInternalTransferRequest(complaint.id, {
                    decision: modal === "decideReject" ? "REJECT" : "APPROVE",
                    reason: decisionReason.trim() || null,
                  }),
                modal === "decideReject"
                  ? t("rejectTransferRequestOk")
                  : t("approveTransferRequestOk"),
              )
            }
          >
            {modal === "decideReject"
              ? t("rejectTransferRequest")
              : t("approveTransferRequest")}
          </Button>
        </ModalSection>
      </Modal>

      <Modal
        open={modal === "withdraw"}
        onClose={() => setModal(null)}
        title={t("withdraw")}
      >
        <ModalSection className="space-y-3">
          <p className="text-sm text-ecmp-text-secondary">{t("withdrawPrompt")}</p>
          <KnowledgeMentionTextarea
            label={t("withdrawReason")}
            value={cancelReason}
            onChange={setCancelReason}
            hint={t("withdrawReasonHint")}
            required
          />
          <Button
            type="button"
            variant="danger"
            disabled={busy || !cancelReason.trim()}
            onClick={() =>
              run(
                () =>
                  withdrawInternalComplaint(complaint.id, {
                    reason: cancelReason.trim(),
                  }),
                t("withdrawOk"),
              )
            }
          >
            {t("withdraw")}
          </Button>
        </ModalSection>
      </Modal>

      <Modal
        open={modal === "requestWithdraw"}
        onClose={() => setModal(null)}
        title={t("requestWithdraw")}
      >
        <ModalSection className="space-y-3">
          <p className="text-sm text-ecmp-text-secondary">
            {t("requestWithdrawPrompt")}
          </p>
          <KnowledgeMentionTextarea
            label={t("withdrawReason")}
            value={cancelReason}
            onChange={setCancelReason}
            hint={t("withdrawReasonHint")}
            required
          />
          <Button
            type="button"
            disabled={busy || !cancelReason.trim()}
            onClick={() =>
              run(
                () =>
                  requestInternalWithdraw(complaint.id, {
                    reason: cancelReason.trim(),
                  }),
                t("requestWithdrawOk"),
              )
            }
          >
            {t("requestWithdraw")}
          </Button>
        </ModalSection>
      </Modal>

      <Modal
        open={
          modal === "decideWithdrawApprove" || modal === "decideWithdrawReject"
        }
        onClose={() => setModal(null)}
        title={
          modal === "decideWithdrawReject"
            ? t("rejectWithdrawRequest")
            : t("approveWithdrawRequest")
        }
      >
        <ModalSection className="space-y-3">
          <p className="text-sm text-ecmp-text-secondary">
            {t("withdrawRequestDecidePrompt", {
              reason: complaint.withdrawRequestReason ?? "—",
            })}
          </p>
          <KnowledgeMentionTextarea
            label={t("decisionReason")}
            value={decisionReason}
            onChange={setDecisionReason}
            hint={
              modal === "decideWithdrawReject"
                ? t("decisionReasonRequiredHint")
                : t("decisionReasonOptionalHint")
            }
          />
          <Button
            type="button"
            variant={modal === "decideWithdrawReject" ? "danger" : "primary"}
            disabled={
              busy ||
              (modal === "decideWithdrawReject" && !decisionReason.trim())
            }
            onClick={() =>
              run(
                () =>
                  decideInternalWithdrawRequest(complaint.id, {
                    decision:
                      modal === "decideWithdrawReject" ? "REJECT" : "APPROVE",
                    reason: decisionReason.trim() || null,
                  }),
                modal === "decideWithdrawReject"
                  ? t("rejectWithdrawRequestOk")
                  : t("approveWithdrawRequestOk"),
              )
            }
          >
            {modal === "decideWithdrawReject"
              ? t("rejectWithdrawRequest")
              : t("approveWithdrawRequest")}
          </Button>
        </ModalSection>
      </Modal>

      <Modal
        open={modal === "resolve"}
        onClose={() => setModal(null)}
        title={t("resolve")}
      >
        <ModalSection className="space-y-3">
          <Input
            label={t("resolutionSummary")}
            value={resolveSummary}
            onChange={(e) => {
              setResolveSummary(e.target.value);
              if (resolveFieldError === "resolutionSummaryRequiredError") {
                setResolveFieldError(null);
              }
            }}
            error={
              resolveFieldError === "resolutionSummaryRequiredError"
                ? t(resolveFieldError)
                : undefined
            }
          />
          <KnowledgeMentionTextarea
            label={t("comment")}
            value={resolveComment}
            onChange={(next) => {
              setResolveComment(next);
              if (resolveFieldError === "commentRequiredError") {
                setResolveFieldError(null);
              }
            }}
            error={
              resolveFieldError === "commentRequiredError"
                ? t(resolveFieldError)
                : undefined
            }
          />
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant="secondary"
              disabled={busy}
              onClick={() => submitResolve("PROPOSE")}
            >
              {t("propose")}
            </Button>
            <Button
              type="button"
              disabled={busy}
              onClick={() => submitResolve("ACCEPT")}
            >
              {t("resolveAccept")}
            </Button>
          </div>
        </ModalSection>
      </Modal>

      <Modal
        open={modal === "accept" || modal === "reject"}
        onClose={() => setModal(null)}
        title={modal === "reject" ? t("rejectReturnToHandling") : t("acceptance")}
      >
        <ModalSection className="space-y-3">
          {modal === "reject" && !rejectPartyLocked ? (
            <Select
              label={t("party")}
              options={rejectParties.map((party) => ({
                value: party,
                label:
                  party === "HANDLING_UNIT"
                    ? t("partyHandling")
                    : t("partyOwner"),
              }))}
              value={acceptParty}
              onChange={(e) =>
                setAcceptParty(e.target.value as "OWNER" | "HANDLING_UNIT")
              }
            />
          ) : (
            <p className="text-sm text-ecmp-text-primary">
              <span className="text-ecmp-text-secondary">{t("party")}: </span>
              {localClosure
                ? t("partyOwnerLocal")
                : acceptParty === "HANDLING_UNIT"
                  ? t("partyHandling")
                  : t("partyOwner")}
            </p>
          )}
          <KnowledgeMentionTextarea
            label={t("note")}
            value={acceptNote}
            onChange={setAcceptNote}
          />
          <Button
            type="button"
            variant={modal === "reject" ? "danger" : "primary"}
            disabled={busy || (modal === "reject" && !acceptNote.trim())}
            onClick={() =>
              run(
                () =>
                  recordInternalAcceptance(complaint.id, {
                    party: acceptParty,
                    decision: modal === "reject" ? "REJECT" : "ACCEPT",
                    note: acceptNote || null,
                  }),
                modal === "reject" ? t("rejectOk") : t("acceptOk"),
              )
            }
          >
            {modal === "reject" ? t("rejectReturnToHandling") : t("confirmAccept")}
          </Button>
        </ModalSection>
      </Modal>

      <Modal
        open={modal === "returnForCompletion"}
        onClose={() => setModal(null)}
        title={t("returnForCompletion")}
      >
        <ModalSection className="space-y-3">
          <p className="text-sm text-ecmp-text-secondary">
            {t("returnForCompletionPrompt")}
          </p>
          <KnowledgeMentionTextarea
            label={t("returnForCompletionReason")}
            value={completionReason}
            onChange={setCompletionReason}
            hint={t("returnForCompletionReasonHint")}
            required
          />
          <Button
            type="button"
            disabled={busy || !completionReason.trim()}
            onClick={() =>
              run(
                () =>
                  returnInternalComplaintForCompletion(complaint.id, {
                    reason: completionReason.trim(),
                  }),
                t("returnForCompletionOk"),
              )
            }
          >
            {t("returnForCompletion")}
          </Button>
        </ModalSection>
      </Modal>

      <Modal
        open={modal === "resendToPusat"}
        onClose={() => setModal(null)}
        title={t("resendToPusat")}
      >
        <ModalSection className="space-y-3">
          <p className="text-sm text-ecmp-text-secondary">
            {t("resendToPusatPrompt")}
          </p>
          {complaint.completionReturnReason ? (
            <p className="text-sm text-ecmp-text-primary">
              <span className="text-ecmp-text-secondary">
                {t("completionReturnReason")}:{" "}
              </span>
              {complaint.completionReturnReason}
            </p>
          ) : null}
          <KnowledgeMentionTextarea
            label={t("resendToPusatNote")}
            value={completionReason}
            onChange={setCompletionReason}
            hint={t("resendToPusatNoteHint")}
            required
          />
          <Button
            type="button"
            disabled={busy || !completionReason.trim()}
            onClick={() =>
              run(
                () =>
                  resendInternalComplaintToPusat(complaint.id, {
                    note: completionReason.trim(),
                  }),
                t("resendToPusatOk"),
              )
            }
          >
            {t("resendToPusat")}
          </Button>
        </ModalSection>
      </Modal>

      <Toast
        open={Boolean(toastMessage)}
        onClose={() => setToastMessage(null)}
        title={toastMessage ?? ""}
        tone="success"
      />
    </PageContainer>
  );
}
