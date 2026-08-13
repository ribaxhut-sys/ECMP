"use client";

import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  changeComplaintStatus,
  fetchBranches,
  fetchCmBatch1Customer360,
  fetchComplaint,
  fetchComplaintAssignments,
  fetchComplaintResolution,
  fetchComplaintSla,
  fetchCustomers,
  type Branch,
  type Customer,
} from "@/lib/api";
import type {
  Assignment,
  Complaint,
  ComplaintStatus,
  Priority,
  SlaRecord,
  SlaStatus,
} from "@/lib/api/types";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Empty,
  ErrorState,
  PageContainer,
  PageHeader,
  SectionHeader,
  Skeleton,
  type BadgeTone,
} from "@/shared/ui";
import { FoundationLegacyBanner } from "./FoundationLegacyBanner";
import {
  CwxContextAwareLayout,
  CwxContextHeader,
  CwxDecisionBar,
  CwxEvidenceSurface,
  CwxOperationalContextBlock,
  CwxWorkingActionsArea,
  deriveContextLevel,
  deriveOperationalContext,
  type CwxDecisionAction,
} from "@/features/cwx";
import { AssignmentCard } from "./AssignmentCard";
import { AppointmentCard } from "./AppointmentCard";
import { CloseComplaintCard } from "./CloseComplaintCard";
import { CloseEscalationCard } from "./CloseEscalationCard";
import { ComplaintAttachmentsCard } from "./ComplaintAttachmentsCard";
import { EscalationCard } from "./EscalationCard";
import { FinalResolutionCard } from "./FinalResolutionCard";
import { ResolutionCard } from "./ResolutionCard";
import { SlaCard } from "./SlaCard";
import { TimelineCard } from "./TimelineCard";
import { statusActionsFor } from "./statusTransitions";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";


type WorkingActionPanel =
  | "assignment"
  | "resolution"
  | "escalation"
  | "appointment"
  | "finalResolution"
  | "close"
  | "closeEscalation";

/** Presentation-only default-open panel from existing status (no new business rules). */
function defaultOpenWorkingAction(
  status: ComplaintStatus,
): WorkingActionPanel | null {
  switch (status) {
    case "NEW":
      return "assignment";
    case "IN_PROGRESS":
      return "resolution";
    case "ESCALATED":
      return "escalation";
    case "RESOLVED":
      return "close";
    default:
      return null;
  }
}

function WorkingActionDisclosure({
  label,
  defaultOpen,
  children,
}: {
  label: string;
  defaultOpen: boolean;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <details
      className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border/70 bg-ecmp-surface/40 open:bg-ecmp-surface"
      open={open}
      onToggle={(e) => setOpen(e.currentTarget.open)}
    >
      <summary className="cursor-pointer px-3 py-2.5 text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ecmp-focus">
        {label}
      </summary>
      <div className="space-y-[var(--ecmp-panel-gap)] border-t border-ecmp-border/60 px-3 pb-3 pt-2">
        {children}
      </div>
    </details>
  );
}

function formatWhen(value: string | null | undefined): string {
  if (!value) return "—";
  try {
    return new Intl.DateTimeFormat(undefined, {
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

function priorityTone(priority: Priority): BadgeTone {
  switch (priority) {
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

function slaTone(status: SlaStatus | undefined): BadgeTone {
  if (status === "COMPLETED") return "success";
  if (status === "BREACHED") return "danger";
  if (status === "PENDING") return "warning";
  return "neutral";
}

function DetailField({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="min-w-0 space-y-1">
      <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
        {label}
      </dt>
      <dd className="whitespace-pre-wrap break-words text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
        {value}
      </dd>
    </div>
  );
}

/**
 * CWX-M1/M2 Foundation wiring only.
 * Parent owns Foundation SoT (`fetchComplaint` + related). No Evidence / Working Actions / History (M3/M4).
 */
export function ComplaintDetailView({ complaintId }: { complaintId: string }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const t = useTranslations("complaints");
  const tCwx = useTranslations("cwx");
  const tCommon = useTranslations("common");
  const tStatus = useTranslations("status");
  const tPriority = useTranslations("priority");
  const tErrors = useTranslations("errors");
  const { hasPermission } = useAuth();
  const canUpdate = hasPermission("complaints:update");
  const canAssign = hasPermission("complaints:assign");
  const failedAttachmentCount = Number(
    searchParams.get("attachmentUploadFailed") ?? "0",
  );
  const [complaint, setComplaint] = useState<Complaint | null>(null);
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [branch, setBranch] = useState<Branch | null>(null);
  const [sla, setSla] = useState<SlaRecord | null>(null);
  const [currentAssignment, setCurrentAssignment] = useState<Assignment | null>(
    null,
  );
  const [complaintCount, setComplaintCount] = useState<number | null>(null);
  const [hasResolution, setHasResolution] = useState(false);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [timelineKey, setTimelineKey] = useState(0);
  const [actionBusy, setActionBusy] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setNotFound(false);
    setError(null);
    setComplaint(null);
    setCustomer(null);
    setBranch(null);
    setSla(null);
    setCurrentAssignment(null);
    setComplaintCount(null);
    setHasResolution(false);

    try {
      const res = await fetchComplaint(complaintId);
      const data = res.data;
      setComplaint(data);

      const [
        customersRes,
        branchesRes,
        resolutionRes,
        slaRes,
        assignmentsRes,
        customer360Res,
      ] = await Promise.all([
        fetchCustomers(100).catch(() => null),
        fetchBranches(100).catch(() => null),
        fetchComplaintResolution(complaintId).catch((err) => {
          if (err instanceof ApiError && err.status === 404) return null;
          return null;
        }),
        fetchComplaintSla(complaintId).catch(() => null),
        fetchComplaintAssignments(complaintId).catch(() => null),
        data.customerId
          ? fetchCmBatch1Customer360(data.customerId).catch(() => null)
          : Promise.resolve(null),
      ]);

      if (customersRes) {
        setCustomer(
          customersRes.data.find((c) => c.id === data.customerId) ?? null,
        );
      }
      if (branchesRes && data.branchId) {
        setBranch(
          branchesRes.data.find((b) => b.id === data.branchId) ?? null,
        );
      }
      setHasResolution(resolutionRes !== null);
      setSla(slaRes?.data ?? null);
      if (assignmentsRes) {
        const current =
          assignmentsRes.data.find((row) => row.isCurrent) ??
          assignmentsRes.data[0] ??
          null;
        setCurrentAssignment(current);
      }
      if (customer360Res?.data) {
        setComplaintCount(customer360Res.data.complaintCount);
      }
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setNotFound(true);
      } else {
        setError(
          resolveApiErrorMessage(err, tErrors, tCommon) ||
            t("unableToLoadDetail"),
        );
      }
    } finally {
      setLoading(false);
    }
  }, [complaintId, t, tCommon, tErrors]);

  useEffect(() => {
    void load();
  }, [load]);

  const breadcrumbs = useMemo(
    () => [
      { label: tCommon("home"), href: "/dashboard" },
      { label: t("title"), href: "/complaints" },
      { label: t("detailTitle") },
    ],
    [t, tCommon],
  );

  const runStatusTransition = useCallback(
    async (target: ComplaintStatus, actionId: string) => {
      setActionError(null);
      setActionBusy(actionId);
      try {
        await changeComplaintStatus(complaintId, { status: target });
        setTimelineKey((key) => key + 1);
        await load();
      } catch (err) {
        setActionError(
          err instanceof ApiError
            ? err.message
            : err instanceof Error
              ? err.message
              : t("statusChangeFailed"),
        );
      } finally {
        setActionBusy(null);
      }
    },
    [complaintId, load, t],
  );

  if (loading) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader title={t("detailTitle")} breadcrumbs={breadcrumbs} />
        <FoundationLegacyBanner />
        <Skeleton rows={8} />
      </PageContainer>
    );
  }

  if (notFound) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader title={t("detailTitle")} breadcrumbs={breadcrumbs} />
        <FoundationLegacyBanner />
        <Empty
          title={t("notFoundTitle")}
          description={t("complaintNotFound")}
          action={
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push("/complaints")}
            >
              {t("backToList")}
            </Button>
          }
        />
      </PageContainer>
    );
  }

  if (error || !complaint) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader title={t("detailTitle")} breadcrumbs={breadcrumbs} />
        <FoundationLegacyBanner />
        <ErrorState
          title={t("unableToLoadDetail")}
          message={error ?? tCommon("unexpectedErrorDescription")}
          onRetry={() => void load()}
        />
      </PageContainer>
    );
  }

  const customerName = customer?.fullName ?? tCommon("emDash");
  const customerPhone = customer?.phone?.trim() || null;
  const owner = complaint.createdBy?.trim() || tCommon("emDash");
  const overall = sla?.overallStatus;
  const slaLabel =
    overall === "BREACHED"
      ? tCwx("slaBreached")
      : overall === "COMPLETED"
        ? tCwx("slaCompleted")
        : overall === "PENDING"
          ? tCwx("slaPending")
          : overall
            ? tCwx("slaOnTrack")
            : tCwx("slaUnavailable");

  const level = deriveContextLevel({
    status: complaint.status,
    priority: complaint.priority,
    slaBreached: overall === "BREACHED",
  });

  const assignedToLabel =
    currentAssignment?.assigneeName?.trim() ||
    currentAssignment?.assigneeId?.trim() ||
    null;

  const cwxM2 = deriveOperationalContext({
    surface: "foundation",
    status: complaint.status,
    priority: complaint.priority,
    overallSlaStatus: overall,
    escalationSlaStatus: sla?.escalationStatus,
    assignedToLabel,
    branchLabel: branch?.name ?? null,
    lastUpdated: complaint.updatedAt,
    category: complaint.category,
    channel: complaint.channel,
    createdAt: complaint.createdAt,
    customerName: customer?.fullName ?? null,
    complaintCount,
    assignmentDueAt: sla?.assignmentDueAt,
    resolutionDueAt: sla?.resolutionDueAt,
    escalationDueAt: sla?.escalationDueAt,
    overallDueAt: sla?.overallDueAt,
  });

  const decisionActions: CwxDecisionAction[] = [];

  if (canUpdate) {
    for (const action of statusActionsFor(complaint.status)) {
      decisionActions.push({
        id: `status-${action.target}`,
        label: t(action.labelKey),
        emphasize: action.target === "CLOSED",
        busy: actionBusy === `status-${action.target}`,
        onClick: () => {
          void runStatusTransition(action.target, `status-${action.target}`);
        },
      });
    }
  }

  if (complaint.status === "NEW" && canAssign) {
    decisionActions.push({
      id: "assign",
      label: tCwx("assignAction"),
      onClick: () => {
        document
          .getElementById("cwx-assignment")
          ?.scrollIntoView({ behavior: "smooth", block: "start" });
      },
    });
  }

  if (canUpdate) {
    decisionActions.push({
      id: "edit",
      label: tCommon("edit"),
      onClick: () => router.push(`/complaints/${complaint.id}/edit`),
    });
  }

  decisionActions.push({
    id: "list",
    label: t("backToList"),
    onClick: () => router.push("/complaints"),
  });

  const openWorkingAction = defaultOpenWorkingAction(complaint.status);

  const main: ReactNode = (
    <div className="space-y-[var(--ecmp-section-gap)]">
      <CwxOperationalContextBlock
        derived={cwxM2}
        operationalLabels={{
          status: tStatus(complaint.status),
          assignedTo: assignedToLabel ?? undefined,
          escalationStatus: cwxM2.operational.escalationStatus
            ? cwxM2.operational.escalationStatus === "ESCALATED"
              ? tStatus("ESCALATED")
              : cwxM2.operational.escalationStatus
            : undefined,
          branch: branch?.name ?? undefined,
          lastUpdated: formatWhen(complaint.updatedAt),
        }}
        caseSummaryStageLabel={tStatus(complaint.status)}
        caseSummaryCreatedLabel={formatWhen(complaint.createdAt)}
        responsibleLabel={assignedToLabel ?? undefined}
        dueLabel={
          cwxM2.currentWork.dueAt
            ? formatWhen(cwxM2.currentWork.dueAt)
            : undefined
        }
      />

      {failedAttachmentCount > 0 ? (
        <Alert
          tone="warning"
          title={t("createdSuccessAlert")}
          description={
            <>
              <p>
                {t("attachmentFailedCount", { count: failedAttachmentCount })}
              </p>
              <p className="mt-1">{t("uploadLaterHint")}</p>
            </>
          }
        />
      ) : null}

      {actionError ? (
        <Alert
          tone="danger"
          title={t("statusChangeFailed")}
          description={actionError}
        />
      ) : null}

      <section
        className="space-y-[var(--ecmp-panel-gap)]"
        aria-label={t("information")}
      >
        <SectionHeader title={t("information")} />
        <Card>
          <CardBody>
            <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)]">
              <DetailField
                label={t("description")}
                value={complaint.description}
              />
              <DetailField
                label={t("channel")}
                value={complaint.channel?.trim() || tCommon("emDash")}
              />
              <DetailField
                label={t("category")}
                value={complaint.category?.trim() || tCommon("emDash")}
              />
              <DetailField
                label={t("reportedAtLabel")}
                value={formatWhen(complaint.reportedAt)}
              />
              <DetailField
                label={t("branch")}
                value={
                  branch?.name ??
                  (complaint.branchId
                    ? tCommon("emDash")
                    : t("unassignedBranch"))
                }
              />
              {customerPhone ? (
                <DetailField label={t("phone")} value={customerPhone} />
              ) : null}
            </dl>
          </CardBody>
        </Card>
      </section>

      <div className="space-y-[var(--ecmp-panel-gap)]">
        <CwxEvidenceSurface
          title={tCwx("evidenceSurfaceTitle")}
          showHeading={false}
        >
          <ComplaintAttachmentsCard
            complaintId={complaint.id}
            refreshKey={timelineKey}
            allowUpload
          />
        </CwxEvidenceSurface>

        <div id="cwx-assignment">
          <CwxWorkingActionsArea
            title={tCwx("workingActionsTitle")}
            description={tCwx("workingActionsDescription")}
          >
            <div
              key={complaint.status}
              className="space-y-[var(--ecmp-panel-gap)]"
            >
              <WorkingActionDisclosure
                label={t("assignmentCard")}
                defaultOpen={openWorkingAction === "assignment"}
              >
                <AssignmentCard
                  complaintId={complaint.id}
                  onAssigned={() => {
                    setTimelineKey((key) => key + 1);
                    void load();
                  }}
                />
              </WorkingActionDisclosure>
              <WorkingActionDisclosure
                label={t("resolutionCard")}
                defaultOpen={openWorkingAction === "resolution"}
              >
                <ResolutionCard
                  complaintId={complaint.id}
                  status={complaint.status}
                  onResolved={() => {
                    setTimelineKey((key) => key + 1);
                    void load();
                  }}
                />
              </WorkingActionDisclosure>
              <WorkingActionDisclosure
                label={t("escalationCard")}
                defaultOpen={openWorkingAction === "escalation"}
              >
                <EscalationCard
                  complaintId={complaint.id}
                  status={complaint.status}
                  hasResolution={hasResolution}
                  onRequested={() => {
                    setTimelineKey((key) => key + 1);
                    void load();
                  }}
                  onReviewed={() => {
                    setTimelineKey((key) => key + 1);
                    void load();
                  }}
                />
              </WorkingActionDisclosure>
              <WorkingActionDisclosure
                label={t("appointmentCard")}
                defaultOpen={openWorkingAction === "appointment"}
              >
                <AppointmentCard
                  complaintId={complaint.id}
                  refreshKey={timelineKey}
                  onBooked={() => {
                    setTimelineKey((key) => key + 1);
                    void load();
                  }}
                />
              </WorkingActionDisclosure>
              <WorkingActionDisclosure
                label={t("finalResolutionCard")}
                defaultOpen={openWorkingAction === "finalResolution"}
              >
                <FinalResolutionCard
                  complaintId={complaint.id}
                  refreshKey={timelineKey}
                  onSubmitted={() => {
                    setTimelineKey((key) => key + 1);
                    void load();
                  }}
                />
              </WorkingActionDisclosure>
              <WorkingActionDisclosure
                label={t("closeCard")}
                defaultOpen={openWorkingAction === "close"}
              >
                <CloseComplaintCard
                  complaint={complaint}
                  onClosed={() => {
                    setTimelineKey((key) => key + 1);
                    void load();
                  }}
                />
              </WorkingActionDisclosure>
              <WorkingActionDisclosure
                label={t("closeEscalationCard")}
                defaultOpen={openWorkingAction === "closeEscalation"}
              >
                <CloseEscalationCard
                  complaintId={complaint.id}
                  complaintStatus={complaint.status}
                  refreshKey={timelineKey}
                  onClosed={() => {
                    setTimelineKey((key) => key + 1);
                    void load();
                  }}
                />
              </WorkingActionDisclosure>
            </div>
          </CwxWorkingActionsArea>
        </div>
      </div>

      <SlaCard complaintId={complaint.id} refreshKey={timelineKey} />

      <section
        className="space-y-[var(--ecmp-panel-gap)]"
        aria-label={t("timelineCard")}
      >
        <TimelineCard complaintId={complaint.id} refreshKey={timelineKey} />
      </section>

      <Card>
        <CardHeader>
          <CardTitle>{t("metadata")}</CardTitle>
        </CardHeader>
        <CardBody>
          <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-3">
            <DetailField
              label={t("createdBy")}
              value={complaint.createdBy ?? tCommon("emDash")}
            />
            <DetailField
              label={t("createdAt")}
              value={formatWhen(complaint.createdAt)}
            />
            <DetailField
              label={t("updatedAt")}
              value={formatWhen(complaint.updatedAt)}
            />
          </dl>
        </CardBody>
      </Card>
    </div>
  );

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader title={t("detailTitle")} breadcrumbs={breadcrumbs} />
      <FoundationLegacyBanner />

      <CwxContextAwareLayout
        level={level}
        labels={{
          customerHistorySlot: tCwx("slotCustomerHistory"),
          decisionStatusSlot: tCwx("slotDecisionStatus"),
          slaAlertSlot: tCwx("slotSlaAlert"),
          reserved: tCwx("slotReserved"),
        }}
        header={
          <CwxContextHeader
            complaintId={complaint.complaintNumber}
            customer={customerName}
            title={complaint.subject}
            priorityLabel={tPriority(complaint.priority)}
            priorityTone={priorityTone(complaint.priority)}
            currentWork={tStatus(complaint.status)}
            owner={owner}
            slaLabel={slaLabel}
            slaTone={slaTone(overall)}
          />
        }
        decisionBar={
          <CwxDecisionBar
            actions={decisionActions}
            overflowLabel={tCwx("moreActions")}
            emptyLabel={tCwx("noActions")}
          />
        }
        main={main}
      />
    </PageContainer>
  );
}
