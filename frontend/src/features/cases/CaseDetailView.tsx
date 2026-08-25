"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { useOrgUnitCode } from "@/features/announcements/useOrgUnitCode";
import {
  ApiError,
  acceptAndScheduleCmBatch1HqEscalation,
  completeCmBatch1HqVisit,
  cancelCmCaseEscalationToPusat,
  decideCmBatch1IntakeEscalation,
  escalateCmCaseToPusat,
  fetchBranches,
  returnCmCaseEscalation,
  returnCmBatch1HqEscalation,
  scheduleCmBatch1HqArrival,
  fetchCmBatch1Complaint,
  fetchCmBatch1Customer360,
  fetchCmCase,
  fetchUsers,
  updateCmCaseStatus,
  type CmCase,
  type CmBatch1HqReturnReasonCode,
  type CmCaseStatus,
} from "@/lib/api";
import type { Branch } from "@/lib/api/branches";
import type { ComplaintSla } from "@/lib/api/types";
import { useReasonPresets } from "@/shared/hooks";
import {
  formatDateTime24,
  formatHqArrivalSlot,
  resolveHqArrivalDisplay,
  toLocalDateKey,
} from "@/shared/utils/datetime";
import { refreshWorkBadges } from "./workBadgesSignal";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { cn } from "@/shared/utils";
import { formatCmBatch1CustomerLabel } from "@/features/complaints/cmBatch1RegistrationLabels";
import { officerDisplayName } from "@/features/complaints/officerDisplayName";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  Empty,
  ErrorState,
  Modal,
  PageContainer,
  PageHeader,
  Select,
  ReasonPresetTags,
  Skeleton,
  Textarea,
  Toast,
  type BadgeTone,
} from "@/shared/ui";
import {
  HqArrivalSlotPicker,
  type HqArrivalSlotValue,
} from "@/features/complaints/HqArrivalSlotPicker";
import { CmBatch1BoundAttachmentsCard } from "@/features/complaints/CmBatch1BoundAttachmentsCard";
import { ComplaintSlaBadge } from "@/features/complaints/ComplaintSlaBadge";
import { KnowledgeReferenceText } from "@/features/complaints/KnowledgeReferenceText";
import { PENANGANAN_FOCUS_QUERY } from "@/features/complaints/ComplaintPenangananSection";
import { PresetTextField } from "@/features/complaints/PresetTextField";
import { CaseStatusBadge } from "./CaseStatusBadge";
import { CaseHistoryPanel } from "./CaseHistoryPanel";
import { CaseHandlingNotes } from "./CaseHandlingNotes";
import {
  caseDescriptionNarrative,
  collectCaseHandlingNotes,
  intakeNoteFromDescription,
} from "./caseHandlingNotes";
import { useCmCaseHistory } from "./useCmCaseHistory";
import { ResolveCaseDialog } from "./ResolveCaseDialog";
import {
  getCaseHandleDecision,
  markCaseHandleClaimed,
  markCaseHandleViewed,
  rememberCaseId,
  shouldAskHandleClaim,
} from "./caseSessionRegistry";
import {
  actorMayHandleEscalatedCase,
  hideCaseBranchWorkActions,
  resolveCaseHqPath,
  showCaseCancelEscalation,
  showCaseLevelCancelEscalation,
  showCaseReturnEscalation,
} from "./caseHqPath";
import {
  canCmBatch1HqReview,
  hqCroDestinationDisplayLabel,
  isCmBatch1HqAcceptScheduleReady,
  isCmBatch1HqNoteReady,
  isCmBatch1HqRescheduleReady,
  resolveCmBatch1HqActionVisibility,
  resolveDefaultHqScheduleDestinationUnitCode,
} from "@/features/complaints/cmBatch1HqActions";
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

const CANCEL_NOTE_MIN = 20;
const ESCALATE_REASON_MIN = 20;
const RETURN_NOTE_MIN = 10;
const CANCEL_ESCALATION_PRESET_KEYS = [
  "cm_batch1.cancel_escalation_note_presets",
] as const;
const ESCALATE_TO_PUSAT_PRESET_KEYS = [
  "cm_batch1.rerequest_escalation_reason_presets",
] as const;
const HQ_ACCEPT_SCHEDULE_PRESET_KEY = "cm_batch1.hq_accept_schedule_note_presets";
const HQ_RETURN_PRESET_KEY = "cm_batch1.hq_return_note_presets";
const HQ_SCHEDULE_PRESET_KEY = "cm_batch1.hq_schedule_note_presets";
const HQ_COMPLETE_PRESET_KEY = "cm_batch1.hq_complete_note_presets";
const HQ_RETURN_REASON_CODES: CmBatch1HqReturnReasonCode[] = [
  "MISSING_ATTACHMENT",
  "INCOMPLETE_CHRONOLOGY",
  "UNCLEAR_CUSTOMER_DATA",
  "WRONG_CATEGORY_OR_ROUTING",
  "ADDITIONAL_EVIDENCE_REQUIRED",
  "OTHER",
];

function nextStepKey(
  status: CmCaseStatus,
  opts: {
    canUpdate: boolean;
    showResolve: boolean;
    showClose: boolean;
    onHqPath: boolean;
    escalatedToPusat: boolean;
    actorIsPusat: boolean;
  },
): string {
  if (opts.escalatedToPusat && !opts.actorIsPusat) return "nextStepPusat";
  if (
    opts.escalatedToPusat &&
    opts.actorIsPusat &&
    !opts.showResolve &&
    !opts.showClose
  ) {
    return "nextStepStart";
  }
  if (
    opts.onHqPath &&
    status !== "RESOLVED" &&
    status !== "CLOSED" &&
    status !== "CANCELLED"
  ) {
    return "nextStepHqPath";
  }
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
 * Order: hero → description → resolution → attachments → history → actions.
 */
export function CaseDetailView({ caseId }: { caseId: string }) {
  const t = useTranslations("cases");
  const tPriority = useTranslations("priority");
  const tCommon = useTranslations("common");
  const tNav = useTranslations("nav");
  const tComplaints = useTranslations("complaints");
  const tErrors = useTranslations("errors");
  const locale = useLocale();
  const router = useRouter();
  const { hasPermission, user, roles } = useAuth();
  const unitCode = useOrgUnitCode();
  const orgReady = unitCode !== undefined;
  const actorIsPusat = Boolean(
    orgReady &&
      actorMayHandleEscalatedCase({ roles, hasPermission, unitCode }),
  );
  const canRead = hasPermission("complaints:read");
  const canUpdate = hasPermission("complaints:update");
  const canCreate = hasPermission("complaints:create");
  const canAct = canUpdate || canCreate;
  const canDecideEscalation = hasPermission("complaints:escalate");
  const cancelPresets = useReasonPresets(CANCEL_ESCALATION_PRESET_KEYS);
  const escalatePresets = useReasonPresets(ESCALATE_TO_PUSAT_PRESET_KEYS);
  const hqAcceptPresets = useReasonPresets([HQ_ACCEPT_SCHEDULE_PRESET_KEY] as const);
  const hqReturnPresets = useReasonPresets([HQ_RETURN_PRESET_KEY] as const);
  const hqSchedulePresets = useReasonPresets([HQ_SCHEDULE_PRESET_KEY] as const);
  const hqCompletePresets = useReasonPresets([HQ_COMPLETE_PRESET_KEY] as const);

  const [data, setData] = useState<CmCase | null>(null);
  const [branches, setBranches] = useState<Branch[]>([]);
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
  const [complaintIntakeDisposition, setComplaintIntakeDisposition] = useState<
    string | null
  >(null);
  const [complaintHqAcceptedAt, setComplaintHqAcceptedAt] = useState<
    string | null
  >(null);
  const [complaintHqArrivalDate, setComplaintHqArrivalDate] = useState<
    string | null
  >(null);
  const [complaintHqArrivalTime, setComplaintHqArrivalTime] = useState<
    string | null
  >(null);
  const [complaintProposedArrivalDate, setComplaintProposedArrivalDate] =
    useState<string | null>(null);
  const [complaintProposedArrivalTime, setComplaintProposedArrivalTime] =
    useState<string | null>(null);
  const [complaintHqDestinationUnitId, setComplaintHqDestinationUnitId] = useState<
    string | null
  >(null);
  const [complaintHqArrivalNote, setComplaintHqArrivalNote] = useState<
    string | null
  >(null);
  const [complaintIntakeNote, setComplaintIntakeNote] = useState<string | null>(
    null,
  );
  const [complaintSla, setComplaintSla] = useState<ComplaintSla | null>(null);
  const [handlePromptOpen, setHandlePromptOpen] = useState(false);
  const [handleClaiming, setHandleClaiming] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [resolveOpen, setResolveOpen] = useState(false);
  const [cancelOpen, setCancelOpen] = useState(false);
  const [cancelNote, setCancelNote] = useState("");
  const cancelNoteRef = useRef<HTMLTextAreaElement | null>(null);
  /** Bumped when a preset tag fills the note, to hand the caret back. */
  const [cancelNoteCaretTick, setCancelNoteCaretTick] = useState(0);
  const [cancellingEscalation, setCancellingEscalation] = useState(false);
  const [escalateOpen, setEscalateOpen] = useState(false);
  const [escalateReason, setEscalateReason] = useState("");
  const [escalating, setEscalating] = useState(false);
  const [returnOpen, setReturnOpen] = useState(false);
  const [returnNote, setReturnNote] = useState("");
  const [returnReasonCode, setReturnReasonCode] =
    useState<CmBatch1HqReturnReasonCode>("MISSING_ATTACHMENT");
  const [returning, setReturning] = useState(false);
  const [hqAcceptOpen, setHqAcceptOpen] = useState(false);
  const [hqReturnOpen, setHqReturnOpen] = useState(false);
  const [hqScheduleOpen, setHqScheduleOpen] = useState(false);
  const [hqCompleteOpen, setHqCompleteOpen] = useState(false);
  const [arrivalDate, setArrivalDate] = useState("");
  const [arrivalTime, setArrivalTime] = useState("");
  const [arrivalNote, setArrivalNote] = useState("");
  const [hqReturnNote, setHqReturnNote] = useState("");
  const [hqReturnReasonCode, setHqReturnReasonCode] =
    useState<CmBatch1HqReturnReasonCode>("MISSING_ATTACHMENT");
  const [hqCompleteNote, setHqCompleteNote] = useState("");
  const [hqActionPending, setHqActionPending] = useState(false);
  const [toastOpen, setToastOpen] = useState(false);
  const [toastTitle, setToastTitle] = useState("");
  const [toastMessage, setToastMessage] = useState("");
  const [toastTone, setToastTone] = useState<"success" | "danger">("success");
  const [resolvePreparing, setResolvePreparing] = useState(false);

  const history = useCmCaseHistory(
    canRead && data ? data.caseId : "",
    data?.updatedAt ?? data?.status ?? null,
  );
  const descriptionNarrative = caseDescriptionNarrative(data?.description);
  const handlingNotes = collectCaseHandlingNotes(
    data?.description,
    history.entries,
    {
      parentIntakeNote: complaintIntakeNote,
      resolutionTexts: [
        data?.resolution?.summary,
        data?.resolution?.comment,
        data?.resolution?.detail,
      ],
    },
  );
  const resolutionSummaryText = data?.resolution?.summary?.trim() ?? "";
  const resolutionCommentText = data?.resolution?.comment?.trim() ?? "";
  const showResolutionComment =
    Boolean(resolutionCommentText) &&
    resolutionCommentText.toLowerCase() !==
      resolutionSummaryText.toLowerCase();

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
      // Reading the Case also marks its parent read for a Pusat user — refresh
      // the sidebar without waiting for the next navigation.
      refreshWorkBadges();

      const [complaintRes, customer360Res, usersRes, branchesRes] = await Promise.all([
        fetchCmBatch1Complaint(caseData.complaintId).catch(() => null),
        caseData.customerId
          ? fetchCmBatch1Customer360(caseData.customerId).catch(() => null)
          : Promise.resolve(null),
        fetchUsers({ page: 1, pageSize: 100 }).catch(() => null),
        fetchBranches(100).catch(() => null),
      ]);

      const complaint = complaintRes?.data ?? null;
      setComplaintNumber(complaint?.complaintNumber?.trim() || null);
      setComplaintStatus(complaint?.status ?? null);
      setComplaintCreatedBy(complaint?.createdBy?.trim() || null);
      setComplaintCreatedByName(complaint?.createdByName?.trim() || null);
      setComplaintIntakeDisposition(complaint?.intakeDisposition ?? null);
      setComplaintHqAcceptedAt(complaint?.hqAcceptedAt ?? null);
      setComplaintHqArrivalDate(complaint?.hqArrivalDate ?? null);
      setComplaintHqArrivalTime(complaint?.hqArrivalTime ?? null);
      setComplaintProposedArrivalDate(complaint?.proposedArrivalDate ?? null);
      setComplaintProposedArrivalTime(complaint?.proposedArrivalTime ?? null);
      setComplaintHqDestinationUnitId(complaint?.hqDestinationUnitId ?? null);
      setComplaintHqArrivalNote(complaint?.hqArrivalNote ?? null);
      setComplaintIntakeNote(
        complaint?.branchResolution?.trim() ||
          intakeNoteFromDescription(complaint?.description),
      );
      setComplaintSla(complaint?.sla ?? null);
      setBranches(branchesRes?.data ?? []);

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
      setBranches([]);
      setCustomerLabel(null);
      setCreatedByLabel(null);
      setAssignedLabel(null);
      setHandlerLabel(null);
      setComplaintNumber(null);
      setComplaintStatus(null);
      setComplaintCreatedBy(null);
      setComplaintCreatedByName(null);
      setComplaintIntakeDisposition(null);
      setComplaintHqAcceptedAt(null);
      setComplaintHqArrivalDate(null);
      setComplaintHqArrivalTime(null);
      setComplaintProposedArrivalDate(null);
      setComplaintProposedArrivalTime(null);
      setComplaintHqDestinationUnitId(null);
      setComplaintHqArrivalNote(null);
      setComplaintSla(null);
      setError(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : t("unableToLoad"),
      );
    } finally {
      setLoading(false);
    }
  }, [canRead, caseId, t, tErrors, tCommon]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const hqPath = resolveCaseHqPath({
    intakeDisposition: complaintIntakeDisposition,
    hqAcceptedAt: complaintHqAcceptedAt,
  });
  const hideBranchActions = hideCaseBranchWorkActions(
    hqPath.onHqPath,
    data?.status,
    Boolean(data?.escalatedToPusat),
    Boolean(orgReady && actorIsPusat),
  );
  const showParentCancelEscalation = showCaseCancelEscalation({
    canDecideEscalation,
    complaintStatus,
    intakeDisposition: complaintIntakeDisposition,
    hqAcceptedAt: complaintHqAcceptedAt,
  });
  const showCaseLevelCancel = Boolean(
    orgReady &&
      data &&
      showCaseLevelCancelEscalation({
        escalatedToPusat: Boolean(data.escalatedToPusat),
        handlingClaimedBy: data.handlingClaimedBy,
        canCancel: canCreate || canDecideEscalation,
        actorIsPusat,
        caseStatus: data.status,
        hqAcceptedAt: complaintHqAcceptedAt,
        intakeDisposition: complaintIntakeDisposition,
      }),
  );
  const showCancelEscalation =
    showParentCancelEscalation || showCaseLevelCancel;
  const showReturnEscalation = Boolean(
    orgReady &&
      data &&
      showCaseReturnEscalation({
        escalatedToPusat: Boolean(data.escalatedToPusat),
        actorIsPusat,
        canUpdate,
        caseStatus: data.status,
      }),
  );
  const cancelNoteOk = cancelNote.trim().length >= CANCEL_NOTE_MIN;
  const returnNoteOk = returnNote.trim().length >= RETURN_NOTE_MIN;
  const canHqReview = canCmBatch1HqReview({ roles, hasPermission, unitCode });
  const hqActions = resolveCmBatch1HqActionVisibility(
    {
      status: complaintStatus,
      intakeDisposition: complaintIntakeDisposition,
      hqAcceptedAt: complaintHqAcceptedAt,
      hqArrivalDate: complaintHqArrivalDate,
      caseCreated: Boolean(data?.caseId),
    },
    canHqReview,
  );
  const {
    showHqAcceptAndSchedule,
    showHqReturn,
    showHqReschedule,
    showHqComplete,
  } = hqActions;
  /** Parent HQ return (API-519) — hide when DEC-029 Case return (API-521) applies. */
  const showParentHqReturn = Boolean(showHqReturn && !showReturnEscalation);
  const hqReturnNoteOk = isCmBatch1HqNoteReady(hqReturnNote);
  const hqCompleteNoteOk = isCmBatch1HqNoteReady(hqCompleteNote);
  const hqCroDestinationUnit = useMemo(
    () => resolveDefaultHqScheduleDestinationUnitCode(branches),
    [branches],
  );
  const hqCroDestinationLabel = useMemo(
    () => hqCroDestinationDisplayLabel(branches),
    [branches],
  );
  const hqAcceptScheduleReady = isCmBatch1HqAcceptScheduleReady({
    arrivalDate,
    arrivalTime,
    arrivalNote,
    destinationUnitId: hqCroDestinationUnit,
  });
  const hqScheduleReady = isCmBatch1HqRescheduleReady({
    arrivalDate,
    arrivalTime,
    arrivalNote,
  });

  // Plain textarea counterpart of PresetTextField: after a preset tag is
  // clicked the caret goes back to the end of the note so typing can continue.
  useEffect(() => {
    if (cancelNoteCaretTick === 0) return;
    const el = cancelNoteRef.current;
    if (!el) return;
    el.focus();
    el.setSelectionRange(el.value.length, el.value.length);
  }, [cancelNoteCaretTick]);

  useEffect(() => {
    if (loading || !data) return;
    setHandlePromptOpen(
      !hideBranchActions &&
        shouldAskHandleClaim({
          status: data.status,
          canAct,
          decision: getCaseHandleDecision(data.caseId),
          handlingClaimedBy: data.handlingClaimedBy,
          userId: user?.id,
        }),
    );
  }, [loading, data, canAct, user?.id, hideBranchActions]);

  function showSuccess(message: string) {
    setToastTone("success");
    setToastTitle(tCommon("success"));
    setToastMessage(message);
    setToastOpen(true);
  }

  function showErrorToast(message: string, title = tCommon("errorTitle")) {
    setToastTone("danger");
    setToastTitle(title);
    setToastMessage(message);
    setToastOpen(true);
  }

  const whenCreated = data?.createdAt
    ? formatDateTime24(data.createdAt, locale) || data.createdAt
    : tCommon("emDash");
  const whenUpdated = data?.updatedAt
    ? formatDateTime24(data.updatedAt, locale) || data.updatedAt
    : null;
  const whenClosed = data?.closedAt
    ? formatDateTime24(data.closedAt, locale) || data.closedAt
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
      !hideBranchActions &&
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
    data &&
      (caseFinished ||
        data.status === "RESOLVED" ||
        showClose ||
        hideBranchActions),
  );
  const showEscalateToPusat = Boolean(
    data &&
      (canCreate || canDecideEscalation) &&
      !data.escalatedToPusat &&
      !hqPath.onHqPath &&
      !caseFinished &&
      data.status !== "RESOLVED" &&
      (data.status === "CREATED" ||
        data.status === "ASSIGNED" ||
        data.status === "IN_PROGRESS"),
  );
  const escalateReasonOk = escalateReason.trim().length >= ESCALATE_REASON_MIN;
  const handleConfirmIsCreator = Boolean(
    user?.id?.trim() &&
      complaintCreatedBy?.trim() &&
      user.id.trim().toLowerCase() === complaintCreatedBy.trim().toLowerCase(),
  );
  const handleConfirmIsPusatClaim = Boolean(
    data?.escalatedToPusat &&
      actorIsPusat &&
      !(data.handlingClaimedBy || "").trim(),
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
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : tComplaints("penangananLoadError"),
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
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : tComplaints("penangananLoadError"),
      );
    } finally {
      setReassigning(false);
    }
  }

  function goToComplaintPenanganan(): void {
    if (!data) return;
    const params = new URLSearchParams();
    params.set("focus", PENANGANAN_FOCUS_QUERY);
    router.push(
      `/complaints/cm/${encodeURIComponent(data.complaintId)}?${params.toString()}`,
    );
  }

  async function submitCancelEscalation(): Promise<void> {
    if (!data || cancellingEscalation || !cancelNoteOk) return;
    setCancellingEscalation(true);
    try {
      if (showCaseLevelCancel) {
        const res = await cancelCmCaseEscalationToPusat(data.caseId, {
          reason: cancelNote.trim(),
        });
        setData(res.data);
        setCancelOpen(false);
        setCancelNote("");
        showSuccess(t("cancelEscalationToPusatSuccess"));
        await reload();
        return;
      }
      const res = await decideCmBatch1IntakeEscalation(data.complaintId, {
        decision: "CANCEL",
        note: cancelNote.trim(),
      });
      setComplaintStatus(res.data.status);
      setComplaintIntakeDisposition(res.data.intakeDisposition ?? null);
      setComplaintHqAcceptedAt(res.data.hqAcceptedAt ?? null);
      setCancelOpen(false);
      setCancelNote("");
      showSuccess(
        t("cancelEscalationCaseToastDescription", {
          number: res.data.complaintNumber,
        }),
      );
    } catch (err) {
      showErrorToast(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : tComplaints("escalationDecisionFailed"),
      );
    } finally {
      setCancellingEscalation(false);
    }
  }

  async function submitEscalateToPusat(): Promise<void> {
    if (!data || escalating || !escalateReasonOk) return;
    setEscalating(true);
    try {
      const res = await escalateCmCaseToPusat(data.caseId, {
        reason: escalateReason.trim(),
      });
      setData(res.data);
      setEscalateOpen(false);
      setEscalateReason("");
      showSuccess(t("escalateToPusatSuccess"));
      await reload();
    } catch (err) {
      showErrorToast(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : t("escalateToPusatFailed"),
      );
    } finally {
      setEscalating(false);
    }
  }

  async function submitReturnEscalation(): Promise<void> {
    if (!data || returning || !returnNoteOk) return;
    setReturning(true);
    try {
      const note = `[${returnReasonCode}] ${returnNote.trim()}`;
      const res = await returnCmCaseEscalation(data.caseId, {
        returnNote: note,
      });
      setData(res.data);
      setReturnOpen(false);
      setReturnNote("");
      setReturnReasonCode("MISSING_ATTACHMENT");
      showSuccess(t("returnEscalationSuccess"));
      await reload();
    } catch (err) {
      showErrorToast(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : t("returnEscalationFailed"),
      );
    } finally {
      setReturning(false);
    }
  }

  async function submitHqAcceptAndSchedule(): Promise<void> {
    if (!data || hqActionPending || !hqAcceptScheduleReady) return;
    setHqActionPending(true);
    try {
      const res = await acceptAndScheduleCmBatch1HqEscalation(data.complaintId, {
        arrivalDate: arrivalDate.trim(),
        arrivalTime: arrivalTime.trim(),
        destinationUnitId: hqCroDestinationUnit,
        note: arrivalNote.trim(),
      });
      setComplaintStatus(res.data.status);
      setComplaintIntakeDisposition(res.data.intakeDisposition ?? null);
      setComplaintHqAcceptedAt(res.data.hqAcceptedAt ?? null);
      setComplaintHqArrivalDate(res.data.hqArrivalDate ?? null);
      setComplaintHqArrivalTime(res.data.hqArrivalTime ?? null);
      setComplaintHqDestinationUnitId(res.data.hqDestinationUnitId ?? null);
      setComplaintHqArrivalNote(res.data.hqArrivalNote ?? null);
      setHqAcceptOpen(false);
      setArrivalDate("");
      setArrivalTime("");
      setArrivalNote("");
      showSuccess(
        tComplaints("hqAcceptScheduledToastDescription", {
          number: res.data.complaintNumber,
          date: res.data.hqArrivalDate ?? arrivalDate.trim(),
          time: res.data.hqArrivalTime ?? arrivalTime.trim(),
        }),
      );
      await reload();
    } catch (err) {
      showErrorToast(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : tComplaints("hqAcceptScheduleFailed"),
      );
    } finally {
      setHqActionPending(false);
    }
  }

  async function submitHqReturn(): Promise<void> {
    if (!data || hqActionPending || !hqReturnNoteOk) return;
    setHqActionPending(true);
    try {
      const res = await returnCmBatch1HqEscalation(data.complaintId, {
        reasonCode: hqReturnReasonCode,
        note: hqReturnNote.trim(),
      });
      setComplaintStatus(res.data.status);
      setComplaintIntakeDisposition(res.data.intakeDisposition ?? null);
      setComplaintHqAcceptedAt(res.data.hqAcceptedAt ?? null);
      setComplaintHqArrivalDate(res.data.hqArrivalDate ?? null);
      setComplaintHqArrivalTime(res.data.hqArrivalTime ?? null);
      setComplaintHqDestinationUnitId(res.data.hqDestinationUnitId ?? null);
      setComplaintHqArrivalNote(res.data.hqArrivalNote ?? null);
      setHqReturnOpen(false);
      setHqReturnNote("");
      showSuccess(
        tComplaints("hqReturnedToastDescription", {
          number: res.data.complaintNumber,
        }),
      );
      await reload();
    } catch (err) {
      showErrorToast(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : tComplaints("hqReturnFailed"),
      );
    } finally {
      setHqActionPending(false);
    }
  }

  async function submitHqSchedule(): Promise<void> {
    if (!data || hqActionPending || !hqScheduleReady) return;
    setHqActionPending(true);
    try {
      const res = await scheduleCmBatch1HqArrival(data.complaintId, {
        arrivalDate: arrivalDate.trim(),
        arrivalTime: arrivalTime.trim(),
        note: arrivalNote.trim() || undefined,
      });
      setComplaintStatus(res.data.status);
      setComplaintIntakeDisposition(res.data.intakeDisposition ?? null);
      setComplaintHqAcceptedAt(res.data.hqAcceptedAt ?? null);
      setComplaintHqArrivalDate(res.data.hqArrivalDate ?? null);
      setComplaintHqArrivalTime(res.data.hqArrivalTime ?? null);
      setComplaintHqDestinationUnitId(res.data.hqDestinationUnitId ?? null);
      setComplaintHqArrivalNote(res.data.hqArrivalNote ?? null);
      setHqScheduleOpen(false);
      setArrivalNote("");
      showSuccess(
        tComplaints("hqScheduledToastDescription", {
          number: res.data.complaintNumber,
          date: arrivalDate.trim(),
          time: arrivalTime.trim(),
        }),
      );
      await reload();
    } catch (err) {
      showErrorToast(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : tComplaints("hqScheduleFailed"),
      );
    } finally {
      setHqActionPending(false);
    }
  }

  async function submitHqComplete(): Promise<void> {
    if (!data || hqActionPending || !hqCompleteNoteOk) return;
    setHqActionPending(true);
    try {
      const res = await completeCmBatch1HqVisit(data.complaintId, {
        note: hqCompleteNote.trim(),
      });
      setComplaintStatus(res.data.status);
      setComplaintIntakeDisposition(res.data.intakeDisposition ?? null);
      setComplaintHqAcceptedAt(res.data.hqAcceptedAt ?? null);
      setComplaintHqArrivalDate(res.data.hqArrivalDate ?? null);
      setComplaintHqArrivalTime(res.data.hqArrivalTime ?? null);
      setComplaintHqDestinationUnitId(res.data.hqDestinationUnitId ?? null);
      setComplaintHqArrivalNote(res.data.hqArrivalNote ?? null);
      setHqCompleteOpen(false);
      setHqCompleteNote("");
      showSuccess(
        tComplaints("hqCompletedToastDescription", {
          number: res.data.complaintNumber,
        }),
      );
      await reload();
    } catch (err) {
      showErrorToast(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : tComplaints("hqCompleteFailed"),
      );
    } finally {
      setHqActionPending(false);
    }
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
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : t("resolveFailed"),
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

  const scheduledSlotParts =
    hqPath.phase === "scheduled" &&
    complaintHqArrivalDate?.trim() &&
    complaintHqArrivalTime?.trim()
      ? formatHqArrivalSlot(
          complaintHqArrivalDate,
          complaintHqArrivalTime,
          locale,
        )
      : null;
  const scheduledSlotLabel = scheduledSlotParts
    ? tComplaints("hqArrivalSlotLabel", scheduledSlotParts)
    : null;
  const scheduledWpNote =
    resolveHqArrivalDisplay({
      arrivalDate: complaintHqArrivalDate,
      arrivalTime: complaintHqArrivalTime,
      note: complaintHqArrivalNote,
    })?.wpNote || "";
  const hqPageTitle = hqPath.copy
    ? tComplaints(hqPath.copy.pageTitle as "hqPathScheduledPageTitle")
    : null;
  const hqPageDescription = hqPath.copy
    ? tComplaints(
        hqPath.copy.pageDescription as "hqPathScheduledPageDescription",
      )
    : null;

  const hqPhaseTitle =
    hqPath.phase === "scheduled" || hqPath.phase === "accepted_unscheduled"
      ? hqPageTitle
      : null;

  const escalationPageTitle = data?.escalatedToPusat
    ? actorIsPusat
      ? handlerDisplay
        ? t("pageTitleInProgress", { name: handlerDisplay })
        : t("pageTitleEscalatedToPusatPusat")
      : t("pageTitleEscalatedToPusat")
    : null;

  const pageTitle = !data
    ? t("detail")
    : caseFinished
      ? t("pageTitleClosed")
      : data.status === "RESOLVED"
        ? t("pageTitleResolved")
        : hqPhaseTitle
          ? hqPhaseTitle
          : escalationPageTitle
            ? escalationPageTitle
            : hqPageTitle
              ? hqPageTitle
              : handlerDisplay
                ? t("pageTitleInProgress", { name: handlerDisplay })
                : t("pageTitleOpen");

  const pageDescription = !data
    ? undefined
    : caseFinished
      ? t("pageDescriptionClosed")
      : hqPath.phase === "scheduled" && scheduledSlotLabel
        ? scheduledSlotLabel
        : hqPageDescription
          ? hqPageDescription
          : t(
              nextStepKey(data.status, {
                canUpdate,
                showResolve,
                showClose,
                onHqPath: hqPath.onHqPath,
                escalatedToPusat: Boolean(data.escalatedToPusat),
                actorIsPusat,
              }) as
                | "nextStepStart"
                | "nextStepResolveOrEscalate"
                | "nextStepClose"
                | "nextStepDone"
                | "nextStepReadOnly"
                | "nextStepHqPath"
                | "nextStepPusat",
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
          {data.escalatedToPusat ? (
            <p
              className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary"
              data-testid="case-with-pusat-note"
            >
              {t(
                actorIsPusat
                  ? "escalatedToPusatNotePusat"
                  : "escalatedToPusatNote",
              )}
            </p>
          ) : null}
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
                      <ComplaintSlaBadge sla={complaintSla} />
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

          {hqPath.phase === "scheduled" ? (
            <section>
              <Card
                data-testid="case-hq-schedule-card"
                data-tone="info"
                className="border-ecmp-info-border bg-ecmp-info-bg shadow-none border-l-4 border-l-ecmp-info"
              >
                <CardBody className="space-y-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge tone="info">{tComplaints("tagHqScheduled")}</Badge>
                    <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-[number:var(--ecmp-font-card-title-weight)] leading-[var(--ecmp-font-card-title-line)] tracking-tight text-ecmp-info-text">
                      {tComplaints("hqPathScheduledPageTitle")}
                    </h2>
                  </div>
                  {scheduledSlotLabel ? (
                    <p className="text-[length:var(--ecmp-font-section-title-size)] font-[number:var(--ecmp-font-section-title-weight)] text-ecmp-text-primary">
                      {scheduledSlotLabel}
                    </p>
                  ) : null}
                  {scheduledWpNote ? (
                    <div className="whitespace-pre-wrap text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                      <KnowledgeReferenceText text={scheduledWpNote} />
                    </div>
                  ) : null}
                  <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-info-text">
                    {t("nextStepHqPath")}
                  </p>
                </CardBody>
              </Card>
            </section>
          ) : null}

          {data.subject ||
          descriptionNarrative ||
          handlingNotes.length > 0 ||
          data.resolution ? (
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
                  {descriptionNarrative ? (
                    <div className="space-y-1">
                      <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                        {t("description")}
                      </p>
                      <p className="whitespace-pre-wrap text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                        <KnowledgeReferenceText text={descriptionNarrative} />
                      </p>
                    </div>
                  ) : null}
                  <CaseHandlingNotes
                    notes={handlingNotes}
                    divided={Boolean(data.subject || descriptionNarrative)}
                  />
                  <div
                    className={cn(
                      "space-y-1",
                      Boolean(descriptionNarrative || handlingNotes.length > 0) &&
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
                          {showResolutionComment ? (
                            <div className="space-y-1">
                              <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                                {t("comment")}
                              </dt>
                              <dd className="whitespace-pre-wrap text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                                <KnowledgeReferenceText
                                  text={data.resolution.comment}
                                />
                              </dd>
                            </div>
                          ) : null}
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
            caseId={data.caseId}
            allowUpload={!attachmentsLocked}
            allowVoid={!attachmentsLocked}
          />

          <CaseHistoryPanel
            entries={history.entries}
            loading={history.loading}
            error={history.error}
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
            {showCancelEscalation ? (
              <Button
                type="button"
                variant="outline"
                data-testid="case-cancel-escalation"
                onClick={() => setCancelOpen(true)}
                disabled={cancellingEscalation}
              >
                {tComplaints("cancelEscalation")}
              </Button>
            ) : null}
            {showHqAcceptAndSchedule ? (
              <Button
                type="button"
                onClick={() => {
                  const proposedDate =
                    complaintProposedArrivalDate?.trim() ?? "";
                  const proposedTime =
                    complaintProposedArrivalTime?.trim() ?? "";
                  const proposedStale =
                    Boolean(proposedDate) &&
                    proposedDate < toLocalDateKey(new Date());
                  setArrivalDate(proposedStale ? "" : proposedDate);
                  setArrivalTime(proposedStale ? "" : proposedTime);
                  setArrivalNote("");
                  setHqAcceptOpen(true);
                }}
                disabled={hqActionPending}
              >
                {tComplaints("hqAcceptAndSchedule")}
              </Button>
            ) : null}
            {showParentHqReturn ? (
              <Button
                type="button"
                variant="outline"
                onClick={() => setHqReturnOpen(true)}
                disabled={hqActionPending}
              >
                {tComplaints("hqReturn")}
              </Button>
            ) : null}
            {showHqReschedule ? (
              <Button
                type="button"
                onClick={() => {
                  setArrivalDate(complaintHqArrivalDate ?? "");
                  setArrivalTime(complaintHqArrivalTime ?? "");
                  setArrivalNote("");
                  setHqScheduleOpen(true);
                }}
                disabled={hqActionPending}
              >
                {complaintHqArrivalDate
                  ? tComplaints("hqRescheduleArrival")
                  : tComplaints("hqScheduleArrival")}
              </Button>
            ) : null}
            {showHqComplete ? (
              <Button
                type="button"
                onClick={() => {
                  setHqCompleteNote("");
                  setHqCompleteOpen(true);
                }}
                disabled={hqActionPending}
              >
                {tComplaints("hqComplete")}
              </Button>
            ) : null}
            {showReturnEscalation ? (
              <Button
                type="button"
                variant="outline"
                data-testid="case-return-escalation"
                onClick={() => {
                  setReturnReasonCode("MISSING_ATTACHMENT");
                  setReturnNote("");
                  setReturnOpen(true);
                }}
                disabled={returning}
              >
                {tComplaints("hqReturn")}
              </Button>
            ) : null}
            {showEscalateToPusat ? (
              <Button
                type="button"
                variant="outline"
                data-testid="case-escalate-to-pusat"
                onClick={() => setEscalateOpen(true)}
                disabled={escalating}
              >
                {t("escalateToPusat")}
              </Button>
            ) : null}
            {canReassign && claimedBySomeone && !caseFinished && !hideBranchActions ? (
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

      <Modal
        open={hqAcceptOpen}
        onClose={() => (!hqActionPending ? setHqAcceptOpen(false) : undefined)}
        title={tComplaints("hqAcceptAndScheduleTitle")}
        size="md"
        footer={
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setHqAcceptOpen(false)}
              disabled={hqActionPending}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              loading={hqActionPending}
              disabled={!hqAcceptScheduleReady || hqActionPending}
              onClick={() => void submitHqAcceptAndSchedule()}
            >
              {tComplaints("hqAcceptAndSchedule")}
            </Button>
          </div>
        }
      >
        <div className="space-y-3">
          <p className="text-ecmp-text-primary">
            {tComplaints("hqAcceptAndScheduleBody", {
              number: complaintNumber ?? tCommon("emDash"),
            })}
          </p>
          {complaintProposedArrivalDate?.trim() &&
          complaintProposedArrivalTime?.trim() ? (
            <Alert
              tone="info"
              title={tComplaints("proposedArrivalHintTitle")}
              description={
                complaintProposedArrivalDate.trim() <
                toLocalDateKey(new Date())
                  ? tComplaints("branchProposedArrivalStaleHint", {
                      date: complaintProposedArrivalDate,
                      time: complaintProposedArrivalTime,
                    })
                  : tComplaints("branchProposedArrivalHint", {
                      date: complaintProposedArrivalDate,
                      time: complaintProposedArrivalTime,
                    })
              }
            />
          ) : null}
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
            {hqCroDestinationUnit.trim()
              ? tComplaints("hqDestinationUnitValue", {
                  unit: hqCroDestinationLabel,
                })
              : tComplaints("hqDestinationUnitMissing")}
          </p>
          {hqCroDestinationUnit.trim() ? (
            <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
              {tComplaints("hqDestinationUnitHint")}
            </p>
          ) : null}
          <HqArrivalSlotPicker
            value={
              arrivalDate || arrivalTime
                ? ({ date: arrivalDate, time: arrivalTime } satisfies HqArrivalSlotValue)
                : null
            }
            onChange={(slot: HqArrivalSlotValue | null) => {
              setArrivalDate(slot?.date ?? "");
              setArrivalTime(slot?.time ?? "");
            }}
            destinationUnitCode={hqCroDestinationUnit}
            allowOverCapacity
            disabled={hqActionPending}
          />
          <PresetTextField
            presets={hqAcceptPresets[HQ_ACCEPT_SCHEDULE_PRESET_KEY] ?? []}
            name="hqAcceptScheduleNote"
            label={tComplaints("hqAcceptScheduleNoteLabel")}
            hint={tComplaints("hqAcceptScheduleNoteHint")}
            value={arrivalNote}
            onChange={setArrivalNote}
            rows={4}
            maxLength={2000}
            disabled={hqActionPending}
            required
          />
        </div>
      </Modal>

      <Modal
        open={hqReturnOpen}
        onClose={() => (!hqActionPending ? setHqReturnOpen(false) : undefined)}
        title={tComplaints("hqReturnTitle")}
        size="sm"
        footer={
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setHqReturnOpen(false)}
              disabled={hqActionPending}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              loading={hqActionPending}
              disabled={!hqReturnNoteOk || hqActionPending}
              onClick={() => void submitHqReturn()}
            >
              {tComplaints("hqReturn")}
            </Button>
          </div>
        }
      >
        <div className="space-y-3">
          <p className="text-ecmp-text-primary">
            {tComplaints("hqReturnBody", {
              number: complaintNumber ?? tCommon("emDash"),
            })}
          </p>
          <Select
            name="hqReturnReasonCode"
            label={tComplaints("hqReturnReasonLabel")}
            options={HQ_RETURN_REASON_CODES.map((code) => ({
              value: code,
              label: tComplaints(`hqReturnReason_${code}` as never),
            }))}
            value={hqReturnReasonCode}
            onChange={(event) =>
              setHqReturnReasonCode(event.target.value as CmBatch1HqReturnReasonCode)
            }
            disabled={hqActionPending}
          />
          <PresetTextField
            presets={hqReturnPresets[HQ_RETURN_PRESET_KEY] ?? []}
            name="hqReturnNote"
            label={tComplaints("hqReturnNoteLabel")}
            hint={tComplaints("hqReturnNoteHint")}
            value={hqReturnNote}
            onChange={setHqReturnNote}
            rows={4}
            maxLength={2000}
            disabled={hqActionPending}
            required
          />
        </div>
      </Modal>

      <Modal
        open={hqScheduleOpen}
        onClose={() => (!hqActionPending ? setHqScheduleOpen(false) : undefined)}
        title={tComplaints("hqScheduleTitle")}
        size="md"
        footer={
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setHqScheduleOpen(false)}
              disabled={hqActionPending}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              loading={hqActionPending}
              disabled={!hqScheduleReady || hqActionPending}
              onClick={() => void submitHqSchedule()}
            >
              {tComplaints("hqScheduleSave")}
            </Button>
          </div>
        }
      >
        <div className="space-y-3">
          <p className="text-ecmp-text-primary">
            {tComplaints("hqScheduleBody", {
              number: complaintNumber ?? tCommon("emDash"),
            })}
          </p>
          <HqArrivalSlotPicker
            value={
              arrivalDate || arrivalTime
                ? ({ date: arrivalDate, time: arrivalTime } satisfies HqArrivalSlotValue)
                : null
            }
            onChange={(slot: HqArrivalSlotValue | null) => {
              setArrivalDate(slot?.date ?? "");
              setArrivalTime(slot?.time ?? "");
            }}
            destinationUnitCode={
              complaintHqDestinationUnitId ?? hqCroDestinationUnit
            }
            allowOverCapacity
            disabled={hqActionPending}
          />
          <PresetTextField
            presets={hqSchedulePresets[HQ_SCHEDULE_PRESET_KEY] ?? []}
            name="hqArrivalNote"
            label={tComplaints("hqArrivalNoteLabel")}
            hint={tComplaints("hqArrivalNoteHint")}
            value={arrivalNote}
            onChange={setArrivalNote}
            rows={4}
            maxLength={2000}
            disabled={hqActionPending}
          />
        </div>
      </Modal>

      <Modal
        open={hqCompleteOpen}
        onClose={() => (!hqActionPending ? setHqCompleteOpen(false) : undefined)}
        title={tComplaints("hqCompleteTitle")}
        size="sm"
        footer={
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setHqCompleteOpen(false)}
              disabled={hqActionPending}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              loading={hqActionPending}
              disabled={!hqCompleteNoteOk || hqActionPending}
              onClick={() => void submitHqComplete()}
            >
              {tComplaints("hqCompleteAction")}
            </Button>
          </div>
        }
      >
        <div className="space-y-3">
          <p className="text-ecmp-text-primary">
            {tComplaints("hqCompleteBody", {
              number: complaintNumber ?? tCommon("emDash"),
            })}
          </p>
          <PresetTextField
            presets={hqCompletePresets[HQ_COMPLETE_PRESET_KEY] ?? []}
            name="hqCompleteNote"
            label={tComplaints("hqCompleteNoteLabel")}
            hint={tComplaints("hqCompleteNoteHint")}
            value={hqCompleteNote}
            onChange={setHqCompleteNote}
            rows={4}
            maxLength={2000}
            disabled={hqActionPending}
            required
          />
        </div>
      </Modal>

      <Toast
        open={toastOpen}
        onClose={() => setToastOpen(false)}
        title={
          toastTitle ||
          (toastTone === "success" ? tCommon("success") : tCommon("errorTitle"))
        }
        description={toastMessage}
        tone={toastTone}
      />
      <Modal
        open={handlePromptOpen}
        onClose={declineHandleClaim}
        title={
          handleConfirmIsPusatClaim
            ? tComplaints("handleConfirmPusatClaimTitle")
            : tComplaints("handleConfirmTitle")
        }
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
          {handleConfirmIsPusatClaim
            ? tComplaints("handleConfirmPusatClaimBody")
            : handleConfirmIsCreator
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
      <Modal
        open={escalateOpen}
        onClose={() => {
          if (escalating) return;
          setEscalateOpen(false);
        }}
        title={t("escalateToPusatTitle")}
        size="md"
        footer={
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setEscalateOpen(false)}
              disabled={escalating}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              loading={escalating}
              disabled={!escalateReasonOk}
              onClick={() => void submitEscalateToPusat()}
            >
              {t("escalateToPusatSubmit")}
            </Button>
          </div>
        }
      >
        <div className="space-y-3">
          <p className="text-ecmp-text-primary">{t("escalateToPusatBody")}</p>
          <ReasonPresetTags
            presets={
              escalatePresets["cm_batch1.rerequest_escalation_reason_presets"] ??
              []
            }
            value={escalateReason}
            onSelect={setEscalateReason}
          />
          <Textarea
            name="escalateToPusatReason"
            label={t("escalateToPusatReasonLabel")}
            hint={t("escalateToPusatReasonHint")}
            value={escalateReason}
            onChange={(event) => setEscalateReason(event.target.value)}
            rows={4}
            maxLength={2000}
            disabled={escalating}
            required
          />
        </div>
      </Modal>
      <Modal
        open={cancelOpen}
        onClose={() => (!cancellingEscalation ? setCancelOpen(false) : undefined)}
        title={tComplaints("cancelEscalationTitle")}
        size="sm"
        footer={
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setCancelOpen(false)}
              disabled={cancellingEscalation}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              variant="danger"
              loading={cancellingEscalation}
              disabled={!cancelNoteOk}
              onClick={() => void submitCancelEscalation()}
            >
              {tComplaints("cancelEscalation")}
            </Button>
          </div>
        }
      >
        <div className="space-y-3">
          <p className="text-ecmp-text-primary">
            {t(
              showCaseLevelCancel
                ? "cancelEscalationToPusatBody"
                : "cancelEscalationCaseBody",
              {
                number: complaintNumber ?? tCommon("emDash"),
              },
            )}
          </p>
          <ReasonPresetTags
            presets={
              cancelPresets["cm_batch1.cancel_escalation_note_presets"] ?? []
            }
            value={cancelNote}
            onSelect={(next) => {
              setCancelNote(next);
              setCancelNoteCaretTick((tick) => tick + 1);
            }}
          />
          <Textarea
            ref={cancelNoteRef}
            name="cancelEscalationNote"
            label={tComplaints("cancelEscalationNoteLabel")}
            hint={tComplaints("cancelEscalationNoteHint")}
            value={cancelNote}
            onChange={(event) => setCancelNote(event.target.value)}
            rows={4}
            maxLength={2000}
            disabled={cancellingEscalation}
            required
          />
        </div>
      </Modal>
      <Modal
        open={returnOpen}
        onClose={() => (!returning ? setReturnOpen(false) : undefined)}
        title={tComplaints("hqReturnTitle")}
        size="sm"
        footer={
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setReturnOpen(false)}
              disabled={returning}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              variant="danger"
              loading={returning}
              disabled={!returnNoteOk}
              onClick={() => void submitReturnEscalation()}
            >
              {tComplaints("hqReturn")}
            </Button>
          </div>
        }
      >
        <div className="space-y-3">
          <p className="text-ecmp-text-primary">
            {t("returnEscalationBody", {
              number: data?.caseNumber ?? tCommon("emDash"),
            })}
          </p>
          <Select
            name="returnReasonCode"
            label={tComplaints("hqReturnReasonLabel")}
            options={HQ_RETURN_REASON_CODES.map((code) => ({
              value: code,
              label: tComplaints(`hqReturnReason_${code}` as never),
            }))}
            value={returnReasonCode}
            onChange={(event) =>
              setReturnReasonCode(event.target.value as CmBatch1HqReturnReasonCode)
            }
            disabled={returning}
          />
          <PresetTextField
            presets={hqReturnPresets[HQ_RETURN_PRESET_KEY] ?? []}
            name="returnNote"
            label={t("returnEscalationNoteLabel")}
            hint={t("returnEscalationNoteHint")}
            value={returnNote}
            onChange={setReturnNote}
            rows={4}
            maxLength={2000}
            disabled={returning}
            required
          />
        </div>
      </Modal>
    </PageContainer>
  );
}
