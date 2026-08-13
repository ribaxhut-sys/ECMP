"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  acceptAndScheduleCmBatch1HqEscalation,
  decideCmBatch1IntakeEscalation,
  fetchBranches,
  fetchCmBatch1Complaint,
  fetchCmBatch1ComplaintHistory,
  requestCmBatch1IntakeEscalation,
  returnCmBatch1HqEscalation,
  scheduleCmBatch1HqArrival,
  type CmBatch1ComplaintResponse,
  type CmBatch1HqReturnReasonCode,
  type CmBatch1IntakeHistoryEntry,
} from "@/lib/api";
import {
  Alert,
  Badge,
  type BadgeTone,
  Button,
  Card,
  CardBody,
  Empty,
  ErrorState,
  Input,
  Modal,
  PageContainer,
  PageHeader,
  SectionHeader,
  Select,
  Skeleton,
  Textarea,
  Pagination,
  WorkspaceToolbar,
} from "@/shared/ui";
import { useToast } from "@/shared/providers";
import { CmBatch1BoundAttachmentsCard } from "./CmBatch1BoundAttachmentsCard";
import {
  CASE_ESCALATE_ACTION_QUERY,
  ComplaintPenangananSection,
  PENANGANAN_FOCUS_QUERY,
  scrollToPenangananSection,
} from "./ComplaintPenangananSection";
import { CM_BATCH1_ESCALATION_PENDING_HREF } from "./cmBatch1ListFilters";
import { KnowledgeReferenceText } from "./KnowledgeReferenceText";
import {
  canCmBatch1HqReview,
  cmBatch1BlobEventCodes,
  isCmBatch1HqAcceptScheduleReady,
  isCmBatch1HqNoteReady,
  isCmBatch1HqRescheduleReady,
  isCmBatch1PusatUnitCode,
  resolveCmBatch1HqActionVisibility,
} from "./cmBatch1HqActions";
import {
  formatCmBatch1CustomerLabel,
  resolveCmBatch1RegistrationUnitLabel,
  shouldShowCmBatch1Category,
} from "./cmBatch1RegistrationLabels";
import type { Branch } from "@/lib/api/branches";
import {
  PRIORITY_OPTIONS,
  formatRegisteredIntakeNote,
  parseCmBatch1Description,
} from "./createComplaintForm";

const REJECT_NOTE_MIN = 20;
const LOG_PAGE_SIZE = 10;
const APPROVE_PRIORITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"] as const;
const HQ_RETURN_REASON_CODES: CmBatch1HqReturnReasonCode[] = [
  "MISSING_ATTACHMENT",
  "INCOMPLETE_CHRONOLOGY",
  "UNCLEAR_CUSTOMER_DATA",
  "WRONG_CATEGORY_OR_ROUTING",
  "ADDITIONAL_EVIDENCE_REQUIRED",
  "OTHER",
];

/** Event code → badge tone. Unknown codes stay neutral rather than disappear. */
const HISTORY_TONES: Record<string, BadgeTone> = {
  REGISTERED: "neutral",
  ESCALATION_REQUESTED: "warning",
  BRANCH_CLOSED: "success",
  ESCALATION_APPROVED: "success",
  ESCALATION_REJECTED: "danger",
  ESCALATION_CANCELLED: "neutral",
  ESCALATION_RE_REQUESTED: "warning",
  HQ_ACCEPTED: "info",
  HQ_RETURNED: "warning",
  HQ_ARRIVAL_SCHEDULED: "info",
};

const HISTORY_LABEL_KEYS: Record<string, string> = {
  REGISTERED: "registered",
  ESCALATION_REQUESTED: "tagEscalationRequested",
  BRANCH_CLOSED: "tagBranchClosed",
  ESCALATION_APPROVED: "escalationApproved",
  ESCALATION_REJECTED: "escalationRejected",
  ESCALATION_CANCELLED: "escalationCancelled",
  ESCALATION_RE_REQUESTED: "tagEscalationReRequested",
  HQ_ACCEPTED: "tagHqAccepted",
  HQ_RETURNED: "tagHqReturned",
  HQ_ARRIVAL_SCHEDULED: "tagHqScheduled",
};

/** Priority reads at a glance: urgent levels carry the danger tone. */
function priorityTone(priority: string): BadgeTone {
  const value = priority.trim().toUpperCase();
  if (value === "CRITICAL") return "danger";
  if (value === "HIGH") return "warning";
  if (value === "LOW") return "neutral";
  return "info";
}

function formatWhen(value: string, locale: string): string {
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

/** One row of the intake log: who did what, when, at which priority, with the note. */
interface IntakeLogRow {
  key: string;
  code: string;
  actor: string | null;
  when: string | null;
  priority: string | null;
  note: string | null;
}

/**
 * SCR-CM-005 — Aggregate create confirmation (DEC-020 read path).
 * Does not use foundation `/api/v1/complaints/{id}`.
 */
export function CmBatch1ConfirmationView({
  complaintId,
}: {
  complaintId: string;
}) {
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const tPriority = useTranslations("priority");
  const tTable = useTranslations("table");
  const tValidation = useTranslations("validation");
  const locale = useLocale();
  const router = useRouter();
  const searchParams = useSearchParams();
  const intakeEscalate = searchParams.get("intake") === "escalate";
  const intakeClosed = searchParams.get("intake") === "closed";
  const focusPenanganan =
    searchParams.get("focus") === PENANGANAN_FOCUS_QUERY;
  const actionEscalate =
    searchParams.get("action") === CASE_ESCALATE_ACTION_QUERY;
  const { hasPermission, user, roles } = useAuth();
  const { pushSuccess, pushError } = useToast();
  const canRead =
    hasPermission("complaints:read") || hasPermission("complaints:create");
  const canDecideEscalation = hasPermission("complaints:escalate");
  const canRequestEscalation =
    hasPermission("complaints:create") ||
    hasPermission("complaints:escalate");
  const [unitCode, setUnitCode] = useState<string | null>(null);
  const [branches, setBranches] = useState<Branch[]>([]);
  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const res = await fetchBranches(100);
        if (cancelled) return;
        setBranches(res.data ?? []);
        const branchId = user?.branchId?.trim();
        if (!branchId) {
          setUnitCode(null);
          return;
        }
        const mine = res.data.find((b) => b.id === branchId);
        setUnitCode(mine?.code ?? null);
      } catch {
        if (!cancelled) {
          setBranches([]);
          setUnitCode(null);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [user?.branchId]);
  const isPusatUnitMember = isCmBatch1PusatUnitCode(unitCode);
  const canHqReview = canCmBatch1HqReview({
    roles,
    hasPermission,
    unitCode,
  });

  const [data, setData] = useState<CmBatch1ComplaintResponse | null>(null);
  const [history, setHistory] = useState<CmBatch1IntakeHistoryEntry[]>([]);
  const [historyError, setHistoryError] = useState(false);
  const [logPage, setLogPage] = useState(1);
  const [openLogKeys, setOpenLogKeys] = useState<Set<string>>(new Set());
  const [manageRequestToken, setManageRequestToken] = useState(0);
  const [penangananSnapshot, setPenangananSnapshot] = useState<{
    loading: boolean;
    openCount: number;
    totalCount: number;
  }>({ loading: true, openCount: 0, totalCount: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [approveOpen, setApproveOpen] = useState(false);
  const [rejectOpen, setRejectOpen] = useState(false);
  const [cancelOpen, setCancelOpen] = useState(false);
  const [reRequestOpen, setReRequestOpen] = useState(false);
  const [hqAcceptOpen, setHqAcceptOpen] = useState(false);
  const [hqReturnOpen, setHqReturnOpen] = useState(false);
  const [hqScheduleOpen, setHqScheduleOpen] = useState(false);
  const [approveNote, setApproveNote] = useState("");
  const [approvePriority, setApprovePriority] = useState("");
  const [rejectNote, setRejectNote] = useState("");
  const [cancelNote, setCancelNote] = useState("");
  const [reRequestReason, setReRequestReason] = useState("");
  const [reRequestPriority, setReRequestPriority] = useState("");
  const [hqReturnNote, setHqReturnNote] = useState("");
  const [hqReturnReasonCode, setHqReturnReasonCode] =
    useState<CmBatch1HqReturnReasonCode>("MISSING_ATTACHMENT");
  const [arrivalDate, setArrivalDate] = useState("");
  const [arrivalTime, setArrivalTime] = useState("");
  const [arrivalNote, setArrivalNote] = useState("");
  const [deciding, setDeciding] = useState(false);
  const announcedIdRef = useRef<string | null>(null);
  /** One-shot guard for ?focus=penanganan deep-link (avoid router.replace thrash). */
  const focusPenangananHandledKeyRef = useRef<string | null>(null);

  useEffect(() => {
    if (!canRead || !complaintId.trim()) {
      setLoading(false);
      return;
    }
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetchCmBatch1Complaint(complaintId.trim());
        if (!cancelled) setData(res.data);
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof ApiError
              ? err.message
              : t("couldNotLoadComplaint"),
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [canRead, complaintId, t]);

  const reloadHistory = useCallback(async () => {
    if (!canRead || !complaintId.trim()) return;
    try {
      const res = await fetchCmBatch1ComplaintHistory(complaintId.trim());
      setHistory(res.data ?? []);
      setHistoryError(false);
    } catch {
      // History is a read model; its failure must not hide the Aggregate.
      setHistory([]);
      setHistoryError(true);
    }
  }, [canRead, complaintId]);

  useEffect(() => {
    void reloadHistory();
  }, [reloadHistory]);

  useEffect(() => {
    if (!data) return;
    if (announcedIdRef.current === data.complaintId) return;
    announcedIdRef.current = data.complaintId;
    const closed = intakeClosed || data.status === "CLOSED";
    if (closed) {
      pushSuccess(
        t("closedSuccess"),
        t("closedSuccessDescription", { number: data.complaintNumber }),
      );
      return;
    }
    if (intakeEscalate) {
      pushSuccess(
        t("escalateSuccess"),
        t("escalateSuccessDescription", { number: data.complaintNumber }),
      );
      return;
    }
    pushSuccess(
      t("createdSuccess"),
      t("registeredDescription", { number: data.complaintNumber }),
    );
  }, [data, intakeClosed, intakeEscalate, pushSuccess, t]);

  useEffect(() => {
    if (!focusPenanganan || loading || !data) return;
    if (intakeClosed || data.status === "CLOSED") return;
    const handledKey = `${data.complaintId}:penanganan`;
    if (focusPenangananHandledKeyRef.current === handledKey) return;
    focusPenangananHandledKeyRef.current = handledKey;

    scrollToPenangananSection();

    const disposition = data.intakeDisposition;
    const canOpenReRequest =
      actionEscalate &&
      canRequestEscalation &&
      data.status === "REGISTERED" &&
      (disposition === "ESCALATE_CANCELLED" ||
        disposition === "ESCALATE_REJECTED" ||
        disposition === "RETURNED_TO_BRANCH") &&
      !data.hqAcceptedAt &&
      !data.caseCreated;
    if (canOpenReRequest) {
      const current = (data.priority || "MEDIUM").toUpperCase();
      setReRequestPriority(
        (APPROVE_PRIORITIES as readonly string[]).includes(current)
          ? current
          : "MEDIUM",
      );
      setReRequestReason("");
      setReRequestOpen(true);
    }

    // Do not call router.replace / history.replaceState to strip ?focus=.
    // Soft-nav replace on this page left App Router transitions pending and
    // blocked Sidebar Link navigation (Dasbor / menu lain) until full reload.
  }, [
    actionEscalate,
    canRequestEscalation,
    data,
    focusPenanganan,
    intakeClosed,
    loading,
  ]);

  async function submitDecision(
    decision: "APPROVE" | "REJECT" | "CANCEL",
  ): Promise<void> {
    if (!data) return;
    setDeciding(true);
    try {
      const note =
        decision === "APPROVE"
          ? approveNote.trim()
          : decision === "REJECT"
            ? rejectNote.trim()
            : cancelNote.trim();
      const res = await decideCmBatch1IntakeEscalation(data.complaintId, {
        decision,
        note,
        priority:
          decision === "APPROVE"
            ? (approvePriority.trim().toUpperCase() as
                | "LOW"
                | "MEDIUM"
                | "HIGH"
                | "CRITICAL")
            : undefined,
      });
      setData(res.data);
      void reloadHistory();
      setApproveOpen(false);
      setRejectOpen(false);
      setCancelOpen(false);
      setApproveNote("");
      setApprovePriority("");
      setRejectNote("");
      setCancelNote("");
      if (decision === "APPROVE") {
        pushSuccess(
          t("escalationApprovedToast"),
          t("escalationApprovedToastDescription", {
            number: res.data.complaintNumber,
          }),
        );
      } else if (decision === "REJECT") {
        pushSuccess(
          t("escalationRejectedToast"),
          t("escalationRejectedToastDescription", {
            number: res.data.complaintNumber,
          }),
        );
      } else {
        pushSuccess(
          t("escalationCancelledToast"),
          t("escalationCancelledToastDescription", {
            number: res.data.complaintNumber,
          }),
        );
      }
    } catch (err) {
      pushError(err, t("escalationDecisionFailed"));
    } finally {
      setDeciding(false);
    }
  }

  async function submitReRequest(): Promise<void> {
    if (!data || deciding) return;
    const reason = reRequestReason.trim();
    const priority = reRequestPriority.trim().toUpperCase();
    if (reason.length < REJECT_NOTE_MIN) return;
    if (!(APPROVE_PRIORITIES as readonly string[]).includes(priority)) return;
    setDeciding(true);
    try {
      const res = await requestCmBatch1IntakeEscalation(data.complaintId, {
        reason,
        priority: priority as "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
      });
      setData(res.data);
      void reloadHistory();
      setReRequestOpen(false);
      setReRequestReason("");
      setReRequestPriority("");
      pushSuccess(
        t("reRequestEscalationToast"),
        t("reRequestEscalationToastDescription", {
          number: res.data.complaintNumber,
        }),
      );
    } catch (err) {
      pushError(err, t("reRequestEscalationFailed"));
    } finally {
      setDeciding(false);
    }
  }

  function openReRequestModal(): void {
    const current = (data?.priority || "MEDIUM").toUpperCase();
    setReRequestPriority(
      (APPROVE_PRIORITIES as readonly string[]).includes(current)
        ? current
        : "MEDIUM",
    );
    setReRequestReason("");
    setReRequestOpen(true);
  }

  function openApproveModal(): void {
    const current = (data?.priority || "MEDIUM").toUpperCase();
    setApprovePriority(
      (APPROVE_PRIORITIES as readonly string[]).includes(current)
        ? current
        : "MEDIUM",
    );
    setApproveOpen(true);
  }

  async function submitHqAcceptAndSchedule(): Promise<void> {
    if (!data) return;
    const note = arrivalNote.trim();
    if (!arrivalDate.trim() || !arrivalTime.trim()) return;
    if (!isCmBatch1HqNoteReady(note)) return;
      setDeciding(true);
      try {
        const res = await acceptAndScheduleCmBatch1HqEscalation(data.complaintId, {
        arrivalDate: arrivalDate.trim(),
        arrivalTime: arrivalTime.trim(),
        note,
      });
      setData(res.data);
      void reloadHistory();
      setHqAcceptOpen(false);
      setArrivalDate("");
      setArrivalTime("");
      setArrivalNote("");
      pushSuccess(
        t("hqAcceptScheduledToast"),
        t("hqAcceptScheduledToastDescription", {
          number: res.data.complaintNumber,
          date: res.data.hqArrivalDate ?? arrivalDate,
          time: res.data.hqArrivalTime ?? arrivalTime,
        }),
      );
    } catch (err) {
      pushError(err, t("hqAcceptScheduleFailed"));
    } finally {
      setDeciding(false);
    }
  }

  async function submitHqReturn(): Promise<void> {
    if (!data) return;
    const note = hqReturnNote.trim();
    if (!isCmBatch1HqNoteReady(note)) return;
    setDeciding(true);
    try {
      const res = await returnCmBatch1HqEscalation(data.complaintId, {
        reasonCode: hqReturnReasonCode,
        note,
      });
      setData(res.data);
      void reloadHistory();
      setHqReturnOpen(false);
      setHqReturnNote("");
      pushSuccess(
        t("hqReturnedToast"),
        t("hqReturnedToastDescription", { number: res.data.complaintNumber }),
      );
    } catch (err) {
      pushError(err, t("hqReturnFailed"));
    } finally {
      setDeciding(false);
    }
  }

  async function submitHqSchedule(): Promise<void> {
    if (!data) return;
    if (!arrivalDate.trim() || !arrivalTime.trim()) return;
    setDeciding(true);
    try {
      const res = await scheduleCmBatch1HqArrival(data.complaintId, {
        arrivalDate: arrivalDate.trim(),
        arrivalTime: arrivalTime.trim(),
        note: arrivalNote.trim() || undefined,
      });
      setData(res.data);
      void reloadHistory();
      setHqScheduleOpen(false);
      setArrivalNote("");
      pushSuccess(
        t("hqScheduledToast"),
        t("hqScheduledToastDescription", {
          number: res.data.complaintNumber,
          date: arrivalDate.trim(),
          time: arrivalTime.trim(),
        }),
      );
    } catch (err) {
      pushError(err, t("hqScheduleFailed"));
    } finally {
      setDeciding(false);
    }
  }

  const onPenangananSnapshot = useCallback(
    (snapshot: {
      loading: boolean;
      openCount: number;
      totalCount: number;
    }) => {
      setPenangananSnapshot((prev) => {
        if (
          prev.loading === snapshot.loading &&
          prev.openCount === snapshot.openCount &&
          prev.totalCount === snapshot.totalCount
        ) {
          return prev;
        }
        return snapshot;
      });
    },
    [],
  );

  if (!canRead) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader
          title={t("complaintRegistered")}
          breadcrumbs={[
            { label: t("home"), href: "/dashboard" },
            { label: t("title"), href: "/complaints" },
            { label: t("confirmation") },
          ]}
        />
        <Empty
          title={t("accessRestricted")}
          description={t("confirmationAccessDescription")}
          primaryAction={{
            label: tCommon("goHome"),
            onClick: () => router.push("/dashboard"),
          }}
        />
      </PageContainer>
    );
  }

  const statusLabel =
    data?.status === "CLOSED"
      ? t("statusClosed")
      : data?.status === "IN_PROGRESS"
        ? t("statusInProgress")
        : data?.status === "REGISTERED"
          ? t("registered")
          : (data?.status ?? "");

  const disposition = (data?.intakeDisposition || "").toUpperCase();
  const pendingEscalation =
    data?.status === "REGISTERED" &&
    disposition === "ESCALATE_PENDING_APPROVAL";
  const hqActions = resolveCmBatch1HqActionVisibility(
    {
      status: data?.status,
      intakeDisposition: data?.intakeDisposition,
      hqAcceptedAt: data?.hqAcceptedAt,
      hqArrivalDate: data?.hqArrivalDate,
      caseCreated: data?.caseCreated,
    },
    canHqReview,
  );
  const {
    approvedEscalation,
    showHqAcceptAndSchedule,
    showHqReturn,
    showHqReschedule,
    showBranchNotifyBanner,
  } = hqActions;
  const showSupervisorActions = pendingEscalation && canDecideEscalation;
  const showCancelEscalation =
    approvedEscalation &&
    canDecideEscalation &&
    !data?.hqAcceptedAt &&
    !data?.caseCreated;
  const canReRequestDisposition =
    data?.status === "REGISTERED" &&
    (disposition === "ESCALATE_CANCELLED" ||
      disposition === "ESCALATE_REJECTED" ||
      disposition === "RETURNED_TO_BRANCH");
  const showReRequestEscalation =
    Boolean(canReRequestDisposition) &&
    canRequestEscalation &&
    !data?.hqAcceptedAt &&
    !data?.caseCreated;
  const showManageCases =
    !intakeClosed &&
    data?.status !== "CLOSED" &&
    disposition !== "BRANCH_CLOSED" &&
    !pendingEscalation &&
    !intakeEscalate &&
    !canHqReview &&
    !isPusatUnitMember;
  /** Bottom CTA only when belum ada penanganan sama sekali. */
  const showTanganiCta =
    showManageCases &&
    !penangananSnapshot.loading &&
    penangananSnapshot.totalCount === 0;

  const hqReturnNoteOk = isCmBatch1HqNoteReady(hqReturnNote);
  const hqAcceptScheduleReady = isCmBatch1HqAcceptScheduleReady({
    arrivalDate,
    arrivalTime,
    arrivalNote,
  });
  const hqScheduleReady = isCmBatch1HqRescheduleReady({
    arrivalDate,
    arrivalTime,
    arrivalNote,
  });

  const priorityRaw = (data?.priority || "").toUpperCase();
  const priorityKnown = ["LOW", "MEDIUM", "HIGH", "CRITICAL"] as const;
  const priorityLabel =
    (priorityKnown as readonly string[]).includes(priorityRaw)
      ? tPriority(priorityRaw as (typeof priorityKnown)[number])
      : priorityRaw || tCommon("emDash");

  const pageTitle =
    intakeClosed || data?.status === "CLOSED"
      ? t("intakeClosedBannerTitle")
      : approvedEscalation
        ? t("escalationApproved")
        : pendingEscalation || intakeEscalate
          ? t("intakeEscalateBannerTitle")
          : t("complaintRegistered");

  const rejectNoteOk = rejectNote.trim().length >= REJECT_NOTE_MIN;
  const cancelNoteOk = cancelNote.trim().length >= REJECT_NOTE_MIN;
  const reRequestReasonOk = reRequestReason.trim().length >= REJECT_NOTE_MIN;
  const reRequestPriorityOk = (APPROVE_PRIORITIES as readonly string[]).includes(
    reRequestPriority.trim().toUpperCase(),
  );
  const reRequestReady = reRequestReasonOk && reRequestPriorityOk;
  const approveNoteOk = approveNote.trim().length >= REJECT_NOTE_MIN;
  const approvePriorityOk = (APPROVE_PRIORITIES as readonly string[]).includes(
    approvePriority.trim().toUpperCase(),
  );
  const approveReady = approveNoteOk && approvePriorityOk;

  const intakeHistory = (() => {
    if (!data) {
      return {
        narrative: "",
        branchResolution: null as string | null,
        escalationReason: null as string | null,
        supervisorNote: null as string | null,
        rejectionNote: null as string | null,
        cancellationNote: null as string | null,
      };
    }
    if (
      data.intakeNarrative ||
      data.branchResolution ||
      data.escalationReason ||
      data.supervisorNote ||
      data.rejectionNote ||
      data.cancellationNote
    ) {
      return {
        narrative: (data.intakeNarrative ?? "").trim(),
        branchResolution: data.branchResolution?.trim() || null,
        escalationReason: data.escalationReason?.trim() || null,
        supervisorNote: data.supervisorNote?.trim() || null,
        rejectionNote: data.rejectionNote?.trim() || null,
        cancellationNote: data.cancellationNote?.trim() || null,
      };
    }
    const parsed = parseCmBatch1Description(data.description);
    return {
      narrative: parsed.narrative,
      branchResolution: parsed.branchResolution,
      escalationReason: parsed.escalationReason,
      supervisorNote: parsed.supervisorNote,
      rejectionNote: parsed.rejectionNote,
      cancellationNote: parsed.cancellationNote,
    };
  })();

  /** Note carried by the blob — the only source for events logged before API-517. */
  function blobNoteFor(code: string): string | null {
    switch (code) {
      case "REGISTERED":
        return formatRegisteredIntakeNote(
          intakeHistory.narrative,
          intakeHistory.branchResolution,
          {
            description: t("intakeHistoryDescriptionLabel"),
            note: t("intakeHistoryNoteLabel"),
          },
        );
      case "ESCALATION_REQUESTED":
      case "ESCALATION_RE_REQUESTED":
        return intakeHistory.escalationReason;
      case "BRANCH_CLOSED":
        return intakeHistory.branchResolution;
      case "ESCALATION_APPROVED":
        return intakeHistory.supervisorNote;
      case "ESCALATION_REJECTED":
        return intakeHistory.rejectionNote;
      case "ESCALATION_CANCELLED":
        return intakeHistory.cancellationNote;
      case "HQ_ACCEPTED":
        return data?.hqAcceptanceNote?.trim() || null;
      case "HQ_RETURNED":
        return data?.hqReturnNote?.trim() || null;
      case "HQ_ARRIVAL_SCHEDULED":
        return data?.hqArrivalDate && data?.hqArrivalTime
          ? t("hqArrivalValue", {
              date: data.hqArrivalDate,
              time: data.hqArrivalTime,
            }) + (data.hqArrivalNote ? `\n${data.hqArrivalNote}` : "")
          : null;
      default:
        return null;
    }
  }

  /** Rows reconstructed from the blob when no event log exists (pre-API-517 rows). */
  function blobOnlyRows(): IntakeLogRow[] {
    if (!data) return [];
    const codes = cmBatch1BlobEventCodes({
      intakeDisposition: data.intakeDisposition,
      escalationReason: intakeHistory.escalationReason,
      branchResolution: intakeHistory.branchResolution,
      supervisorNote: intakeHistory.supervisorNote,
      rejectionNote: intakeHistory.rejectionNote,
      cancellationNote: intakeHistory.cancellationNote,
      hqReturnNote: data.hqReturnNote,
      hqAcceptedAt: data.hqAcceptedAt,
      hqArrivalDate: data.hqArrivalDate,
      hqArrivalTime: data.hqArrivalTime,
      intakeClosed,
    });
    return codes.map((code) => ({
      key: `blob-${code}`,
      code,
      actor: code === "REGISTERED" ? (data.createdByName ?? null) : null,
      when: code === "REGISTERED" ? formatWhen(data.createdAt ?? "", locale) : null,
      priority: null,
      note: blobNoteFor(code),
    }));
  }

  const logRows: IntakeLogRow[] =
    history.length > 0
      ? history.map((entry) => ({
          key: entry.entryId,
          code: entry.eventCode,
          actor: entry.actorName?.trim() || null,
          when: formatWhen(entry.occurredAt, locale),
          priority: entry.priority?.trim() || null,
          // Prefer structured Deskripsi+Catatan for REGISTERED (timeline note is narrative-only).
          note:
            entry.eventCode === "REGISTERED"
              ? blobNoteFor("REGISTERED")
              : entry.note?.trim() || blobNoteFor(entry.eventCode),
        }))
      : blobOnlyRows();

  const logTotalPages = Math.max(
    1,
    Math.ceil(logRows.length / LOG_PAGE_SIZE),
  );
  const safeLogPage = Math.min(logPage, logTotalPages);
  const pagedLogRows = logRows.slice(
    (safeLogPage - 1) * LOG_PAGE_SIZE,
    safeLogPage * LOG_PAGE_SIZE,
  );
  const allOnPageOpen =
    pagedLogRows.length > 0 &&
    pagedLogRows.every((row) => openLogKeys.has(row.key));

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
      for (const row of pagedLogRows) {
        if (allOnPageOpen) next.delete(row.key);
        else next.add(row.key);
      }
      return next;
    });
  }

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={pageTitle}
        breadcrumbs={[
          { label: t("home"), href: "/dashboard" },
          { label: t("title"), href: "/complaints" },
          { label: t("confirmation") },
        ]}
        description={
          intakeClosed || data?.status === "CLOSED"
            ? t("intakeClosedBannerDescription")
            : pendingEscalation || intakeEscalate
              ? t("intakeEscalateBannerDescription")
              : t("confirmationDescription")
        }
      />

      {intakeClosed ? (
        <Alert
          tone="info"
          title={t("intakeClosedBannerTitle")}
          description={t("intakeClosedBannerDescription")}
        />
      ) : null}

      {pendingEscalation || intakeEscalate ? (
        <Alert
          tone="info"
          title={t("intakeEscalateBannerTitle")}
          description={t("intakeEscalateBannerDescription")}
        />
      ) : null}

      {showBranchNotifyBanner ? (
        <Alert
          tone="warning"
          title={t("hqScheduledBranchNotifyTitle")}
          description={t("hqScheduledBranchNotifyBody", {
            date: data?.hqArrivalDate ?? "",
            time: data?.hqArrivalTime ?? "",
          })}
        />
      ) : null}

      {!intakeClosed && data?.intakeDisposition === "RETURNED_TO_BRANCH" ? (
        <Alert
          tone="warning"
          title={t("returnedToBranchBannerTitle")}
          description={t("returnedToBranchBannerDescription")}
        />
      ) : null}

      {loading ? <Skeleton rows={5} /> : null}

      {!loading && error ? (
        <ErrorState
          title={t("couldNotLoadComplaint")}
          message={error}
          onRetry={() => {
            setLoading(true);
            setError(null);
            void fetchCmBatch1Complaint(complaintId.trim())
              .then((res) => setData(res.data))
              .catch((err) =>
                setError(
                  err instanceof ApiError
                    ? err.message
                    : t("couldNotLoadComplaint"),
                ),
              )
              .finally(() => setLoading(false));
          }}
        />
      ) : null}

      {!loading && data ? (
        <>
          <section className="space-y-[var(--ecmp-panel-gap)]">
            <SectionHeader
              title={t("registrationDetails")}
              description={
                intakeClosed || data.status === "CLOSED"
                  ? t("registrationDetailsDescriptionClosed")
                  : pendingEscalation || intakeEscalate
                    ? t("registrationDetailsDescriptionEscalate")
                    : t("registrationDetailsDescription")
              }
            />
            <Card>
              <CardBody>
                <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] md:grid-cols-2">
                  {data.subject ? (
                    <div className="md:col-span-2">
                      <dt className="sr-only">{t("subject")}</dt>
                      <dd className="text-[length:var(--ecmp-font-title-size)] font-[number:var(--ecmp-font-title-weight)] leading-[var(--ecmp-font-title-line)] tracking-tight text-ecmp-text-primary">
                        {data.subject}
                      </dd>
                    </div>
                  ) : null}
                  <div className="space-y-1">
                    <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                      {t("complaintNumber")}
                    </dt>
                    <dd className="text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary">
                      {data.complaintNumber}
                    </dd>
                  </div>
                  <div className="space-y-1">
                    <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                      {t("status")}
                    </dt>
                    <dd className="flex flex-wrap items-center gap-2">
                      <Badge
                        tone={
                          data.status === "CLOSED" ? "success" : "info"
                        }
                      >
                        {statusLabel}
                      </Badge>
                      {data.intakeDisposition ===
                      "ESCALATE_PENDING_APPROVAL" ? (
                        <Badge tone="warning">{t("awaitingApproval")}</Badge>
                      ) : null}
                      {data.intakeDisposition === "ESCALATE_APPROVED" ? (
                        <Badge tone="info">{t("escalationApproved")}</Badge>
                      ) : null}
                      {data.intakeDisposition === "ESCALATE_REJECTED" ? (
                        <Badge tone="neutral">{t("escalationRejected")}</Badge>
                      ) : null}
                      {data.intakeDisposition === "ESCALATE_CANCELLED" ? (
                        <Badge tone="neutral">{t("escalationCancelled")}</Badge>
                      ) : null}
                      {data.intakeDisposition === "RETURNED_TO_BRANCH" ? (
                        <Badge tone="warning">{t("returnedToBranch")}</Badge>
                      ) : null}
                      {data.intakeDisposition === "HQ_SCHEDULED" ? (
                        <Badge tone="warning">{t("hqScheduled")}</Badge>
                      ) : null}
                    </dd>
                  </div>
                  <div className="space-y-1">
                    <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                      {t("registrationUnitLabel")}
                    </dt>
                    <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                      {resolveCmBatch1RegistrationUnitLabel(
                        data.owningUnitId,
                        branches,
                      ) || tCommon("emDash")}
                    </dd>
                  </div>
                  <div className="space-y-1">
                    <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                      {t("registeredAtLabel")}
                    </dt>
                    <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                      {data.createdAt
                        ? formatWhen(data.createdAt, locale)
                        : tCommon("emDash")}
                    </dd>
                  </div>
                  <div className="space-y-1">
                    <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                      {t("registeredByLabel")}
                    </dt>
                    <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                      {data.createdByName?.trim() ||
                        data.createdBy?.trim() ||
                        tCommon("emDash")}
                    </dd>
                  </div>
                  <div className="space-y-1">
                    <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                      {t("customer")}
                    </dt>
                    <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                      {formatCmBatch1CustomerLabel(
                        data.customerDisplayName,
                        data.customerNumber,
                        data.customerId,
                      ) || tCommon("emDash")}
                    </dd>
                  </div>
                  {intakeEscalate ||
                  pendingEscalation ||
                  (data.priority && data.status !== "CLOSED") ? (
                    <div className="space-y-1">
                      <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                        {t("priority")}
                      </dt>
                      <dd>
                        <Badge
                          tone={
                            ["CRITICAL", "HIGH"].includes(
                              (data.priority || "").toUpperCase(),
                            )
                              ? "danger"
                              : "neutral"
                          }
                        >
                          {priorityLabel}
                        </Badge>
                      </dd>
                    </div>
                  ) : null}
                  {data.replayed ? (
                    <div className="space-y-1">
                      <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                        {t("replayed")}
                      </dt>
                      <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                        {tCommon("yes")}
                      </dd>
                    </div>
                  ) : null}
                  {shouldShowCmBatch1Category(data.category) ? (
                    <div className="space-y-1">
                      <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                        {t("category")}
                      </dt>
                      <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                        {data.category}
                      </dd>
                    </div>
                  ) : null}
                </dl>
              </CardBody>
            </Card>
          </section>

          <section className="space-y-[var(--ecmp-panel-gap)]">
            <SectionHeader
              title={t("intakeHistoryTitle")}
              description={t("intakeEventLogDescription")}
            />
            <Card>
              <CardBody className="space-y-[var(--ecmp-panel-gap)]">
                {historyError ? (
                  <Alert
                    tone="warning"
                    title={t("intakeEventLogUnavailable")}
                    description={t("intakeEventLogUnavailableDescription")}
                  />
                ) : null}
                {logRows.length === 0 ? (
                  <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                    {t("intakeEventLogEmpty")}
                  </p>
                ) : (
                  <>
                    <WorkspaceToolbar
                      summary={tTable("itemsInView", {
                        count: logRows.length,
                      })}
                      actions={
                        <Button
                          type="button"
                          size="sm"
                          variant="outline"
                          onClick={toggleAllOnPage}
                        >
                          {allOnPageOpen
                            ? t("intakeEventLogCollapseAll")
                            : t("intakeEventLogExpandAll")}
                        </Button>
                      }
                    />
                    <ol className="space-y-[var(--ecmp-form-gap)]">
                      {pagedLogRows.map((row, index) => {
                        const number = (safeLogPage - 1) * LOG_PAGE_SIZE + index + 1;
                        const open = openLogKeys.has(row.key);
                        return (
                          <li
                            key={row.key}
                            className={`rounded-[var(--ecmp-radius-md)] border border-ecmp-border ${
                              number % 2 === 1
                                ? "bg-ecmp-surface"
                                : "bg-ecmp-surface-sunken"
                            }`}
                          >
                            <button
                              type="button"
                              onClick={() => toggleLogRow(row.key)}
                              aria-expanded={open}
                              aria-controls={`intake-log-note-${row.key}`}
                              className="flex w-full items-start gap-3 rounded-[var(--ecmp-radius-md)] p-3 text-left hover:bg-ecmp-hover focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-primary"
                            >
                              <span
                                aria-hidden
                                className="min-w-6 shrink-0 text-[length:var(--ecmp-font-body-size)] font-[number:var(--ecmp-font-overline-weight)] tabular-nums text-ecmp-text-secondary"
                              >
                                {number}.
                              </span>
                              <span className="flex min-w-0 flex-1 flex-wrap items-center gap-x-3 gap-y-1">
                                <Badge tone={HISTORY_TONES[row.code] ?? "neutral"}>
                                  {HISTORY_LABEL_KEYS[row.code]
                                    ? t(HISTORY_LABEL_KEYS[row.code])
                                    : row.code}
                                </Badge>
                                <span className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                                  {row.actor || tCommon("emDash")}
                                </span>
                                <span className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                                  {row.when || tCommon("emDash")}
                                </span>
                                {row.priority ? (
                                  <Badge
                                    tone={priorityTone(row.priority)}
                                    variant="solid"
                                  >
                                    {t("priorityTag", {
                                      value: tPriority.has(row.priority)
                                        ? tPriority(
                                            row.priority as (typeof priorityKnown)[number],
                                          )
                                        : row.priority,
                                    })}
                                  </Badge>
                                ) : null}
                              </span>
                              <span className="shrink-0 text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                                {open
                                  ? t("intakeEventLogHideNote")
                                  : t("intakeEventLogShowNote")}
                              </span>
                            </button>
                            {open ? (
                              <div
                                id={`intake-log-note-${row.key}`}
                                className="break-words border-t border-ecmp-border px-3 pb-3 pt-2 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary"
                              >
                                {row.code === "REGISTERED" ? (
                                  <div className="space-y-3">
                                    <div className="space-y-1">
                                      <p className="font-semibold text-ecmp-text-primary">
                                        {t("intakeHistoryDescriptionLabel")}
                                      </p>
                                      <div className="whitespace-pre-wrap">
                                        <KnowledgeReferenceText
                                          text={
                                            intakeHistory.narrative.trim() ||
                                            "—"
                                          }
                                        />
                                      </div>
                                    </div>
                                    <div className="space-y-1">
                                      <p className="font-semibold text-ecmp-text-primary">
                                        {t("intakeHistoryNoteLabel")}
                                      </p>
                                      <div className="whitespace-pre-wrap">
                                        <KnowledgeReferenceText
                                          text={
                                            (
                                              intakeHistory.branchResolution ??
                                              ""
                                            ).trim() || "—"
                                          }
                                        />
                                      </div>
                                    </div>
                                  </div>
                                ) : row.note ? (
                                  <div className="whitespace-pre-wrap">
                                    <KnowledgeReferenceText text={row.note} />
                                  </div>
                                ) : (
                                  t("intakeEventNoteEmpty")
                                )}
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
                              from: (safeLogPage - 1) * LOG_PAGE_SIZE + 1,
                              to: Math.min(
                                safeLogPage * LOG_PAGE_SIZE,
                                logRows.length,
                              ),
                              total: logRows.length,
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
                )}
              </CardBody>
            </Card>
          </section>

          <CmBatch1BoundAttachmentsCard
            complaintId={data.complaintId}
            customerId={data.customerId}
            allowUpload={
              !(intakeClosed || data.status === "CLOSED")
            }
            allowVoid={!(intakeClosed || data.status === "CLOSED")}
          />

          {!intakeClosed && data.status !== "CLOSED" ? (
            <ComplaintPenangananSection
              complaintId={data.complaintId}
              complaintStatus={data.status}
              intakeDisposition={data.intakeDisposition}
              allowStart={showManageCases}
              allowEscalate={showReRequestEscalation}
              manageRequestToken={manageRequestToken}
              onPenangananSnapshot={onPenangananSnapshot}
              seed={{
                category: data.category,
                subject: data.subject,
                description:
                  intakeHistory.narrative ||
                  data.intakeNarrative ||
                  data.description,
                priority: data.priority,
                destinationUnitId: data.owningUnitId || unitCode,
              }}
              onRequestHqEscalation={
                showReRequestEscalation
                  ? () => openReRequestModal()
                  : undefined
              }
            />
          ) : null}

          <div className="flex flex-wrap gap-[var(--ecmp-form-gap)]">
            {showSupervisorActions ? (
              <>
                <Button
                  type="button"
                  onClick={() => openApproveModal()}
                  disabled={deciding}
                >
                  {t("approveEscalation")}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setRejectOpen(true)}
                  disabled={deciding}
                >
                  {t("rejectEscalation")}
                </Button>
              </>
            ) : null}
            {showCancelEscalation ? (
              <Button
                type="button"
                variant="outline"
                onClick={() => setCancelOpen(true)}
                disabled={deciding}
              >
                {t("cancelEscalation")}
              </Button>
            ) : null}
            {showReRequestEscalation ? (
              <Button
                type="button"
                onClick={() => openReRequestModal()}
                disabled={deciding}
              >
                {t("reRequestEscalation")}
              </Button>
            ) : null}
            {showHqAcceptAndSchedule ? (
              <Button
                type="button"
                onClick={() => {
                  setArrivalDate("");
                  setArrivalTime("");
                  setArrivalNote("");
                  setHqAcceptOpen(true);
                }}
                disabled={deciding}
              >
                {t("hqAcceptAndSchedule")}
              </Button>
            ) : null}
            {showHqReturn ? (
              <Button
                type="button"
                variant="outline"
                onClick={() => setHqReturnOpen(true)}
                disabled={deciding}
              >
                {t("hqReturn")}
              </Button>
            ) : null}
            {showHqReschedule ? (
              <Button
                type="button"
                onClick={() => {
                  setArrivalDate(data?.hqArrivalDate ?? "");
                  setArrivalTime(data?.hqArrivalTime ?? "");
                  setArrivalNote("");
                  setHqScheduleOpen(true);
                }}
                disabled={deciding}
              >
                {data?.hqArrivalDate
                  ? t("hqRescheduleArrival")
                  : t("hqScheduleArrival")}
              </Button>
            ) : null}
            {intakeEscalate && !showSupervisorActions ? (
              <Button
                type="button"
                onClick={() => router.push(CM_BATCH1_ESCALATION_PENDING_HREF)}
              >
                {t("awaitingApproval")}
              </Button>
            ) : null}
            {showTanganiCta ? (
              <div className="flex w-full flex-col gap-1 sm:w-auto">
                <Button
                  type="button"
                  onClick={() => setManageRequestToken((n) => n + 1)}
                >
                  {t("manageCases")}
                </Button>
                <p className="max-w-sm text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                  {t("manageCasesHint")}
                </p>
              </div>
            ) : null}
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push("/complaints/new")}
            >
              {t("registerAnother")}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push("/complaints")}
            >
              {t("backToComplaints")}
            </Button>
          </div>
        </>
      ) : null}

      <Modal
        open={approveOpen}
        onClose={() => (!deciding ? setApproveOpen(false) : undefined)}
        title={t("approveEscalationTitle")}
        size="sm"
        footer={
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setApproveOpen(false)}
              disabled={deciding}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              loading={deciding}
              disabled={!approveReady}
              onClick={() => void submitDecision("APPROVE")}
            >
              {t("approveEscalation")}
            </Button>
          </div>
        }
      >
        <div className="space-y-3">
          <p className="text-ecmp-text-primary">
            {t("approveEscalationBody", {
              number: data?.complaintNumber ?? "",
            })}
          </p>
          <Textarea
            label={t("approveEscalationNoteLabel")}
            hint={t("approveEscalationNoteHint")}
            value={approveNote}
            onChange={(e) => setApproveNote(e.target.value)}
            rows={4}
            maxLength={2000}
            disabled={deciding}
            required
            aria-required="true"
          />
          <Select
            name="approvePriority"
            id="approvePriority"
            label={t("approveEscalationPriorityLabel")}
            hint={t("approveEscalationPriorityHint")}
            placeholder={t("selectPriorityPlaceholder")}
            options={PRIORITY_OPTIONS.map((opt) => ({
              value: opt.value,
              label: tPriority(opt.value),
            }))}
            value={approvePriority}
            onChange={(e) => setApprovePriority(e.target.value)}
            error={
              approveOpen && approveNoteOk && !approvePriorityOk
                ? tValidation("priorityRequired")
                : undefined
            }
            required
            aria-required="true"
            disabled={deciding}
          />
        </div>
      </Modal>

      <Modal
        open={rejectOpen}
        onClose={() => (!deciding ? setRejectOpen(false) : undefined)}
        title={t("rejectEscalationTitle")}
        size="sm"
        footer={
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setRejectOpen(false)}
              disabled={deciding}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              variant="danger"
              loading={deciding}
              disabled={!rejectNoteOk}
              onClick={() => void submitDecision("REJECT")}
            >
              {t("rejectEscalation")}
            </Button>
          </div>
        }
      >
        <div className="space-y-3">
          <p className="text-ecmp-text-primary">
            {t("rejectEscalationBody", {
              number: data?.complaintNumber ?? "",
            })}
          </p>
          <Textarea
            label={t("rejectEscalationNoteLabel")}
            hint={t("rejectEscalationNoteHint")}
            value={rejectNote}
            onChange={(e) => setRejectNote(e.target.value)}
            rows={4}
            maxLength={2000}
            disabled={deciding}
          />
        </div>
      </Modal>

      <Modal
        open={cancelOpen}
        onClose={() => (!deciding ? setCancelOpen(false) : undefined)}
        title={t("cancelEscalationTitle")}
        size="sm"
        footer={
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setCancelOpen(false)}
              disabled={deciding}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              variant="danger"
              loading={deciding}
              disabled={!cancelNoteOk}
              onClick={() => void submitDecision("CANCEL")}
            >
              {t("cancelEscalation")}
            </Button>
          </div>
        }
      >
        <div className="space-y-3">
          <p className="text-ecmp-text-primary">
            {t("cancelEscalationBody", {
              number: data?.complaintNumber ?? "",
            })}
          </p>
          <Textarea
            label={t("cancelEscalationNoteLabel")}
            hint={t("cancelEscalationNoteHint")}
            value={cancelNote}
            onChange={(e) => setCancelNote(e.target.value)}
            rows={4}
            maxLength={2000}
            disabled={deciding}
            required
            aria-required="true"
          />
        </div>
      </Modal>

      <Modal
        open={reRequestOpen}
        onClose={() => (!deciding ? setReRequestOpen(false) : undefined)}
        title={t("reRequestEscalationTitle")}
        size="sm"
        footer={
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setReRequestOpen(false)}
              disabled={deciding}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              loading={deciding}
              disabled={!reRequestReady || deciding}
              onClick={() => void submitReRequest()}
            >
              {t("reRequestEscalation")}
            </Button>
          </div>
        }
      >
        <div className="space-y-3">
          <p className="text-ecmp-text-primary">
            {t("reRequestEscalationBody", {
              number: data?.complaintNumber ?? "",
            })}
          </p>
          <Textarea
            label={t("reRequestEscalationReasonLabel")}
            hint={t("reRequestEscalationReasonHint")}
            value={reRequestReason}
            onChange={(e) => setReRequestReason(e.target.value)}
            rows={4}
            maxLength={2000}
            disabled={deciding}
            required
            aria-required="true"
          />
          <Select
            name="reRequestPriority"
            id="reRequestPriority"
            label={t("reRequestEscalationPriorityLabel")}
            hint={t("reRequestEscalationPriorityHint")}
            placeholder={t("selectPriorityPlaceholder")}
            options={PRIORITY_OPTIONS.map((opt) => ({
              value: opt.value,
              label: tPriority(opt.value),
            }))}
            value={reRequestPriority}
            onChange={(e) => setReRequestPriority(e.target.value)}
            error={
              reRequestOpen && reRequestReasonOk && !reRequestPriorityOk
                ? tValidation("priorityRequired")
                : undefined
            }
            required
            aria-required="true"
            disabled={deciding}
          />
        </div>
      </Modal>

      <Modal
        open={hqAcceptOpen}
        onClose={() => (!deciding ? setHqAcceptOpen(false) : undefined)}
        title={t("hqAcceptAndScheduleTitle")}
        size="sm"
        footer={
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setHqAcceptOpen(false)}
              disabled={deciding}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              loading={deciding}
              disabled={!hqAcceptScheduleReady || deciding}
              onClick={() => void submitHqAcceptAndSchedule()}
            >
              {t("hqAcceptAndSchedule")}
            </Button>
          </div>
        }
      >
        <div className="space-y-3">
          <p className="text-ecmp-text-primary">
            {t("hqAcceptAndScheduleBody", {
              number: data?.complaintNumber ?? "",
            })}
          </p>
          <Input
            type="date"
            label={t("hqArrivalDateLabel")}
            value={arrivalDate}
            onChange={(e) => setArrivalDate(e.target.value)}
            disabled={deciding}
            required
          />
          <Input
            type="time"
            label={t("hqArrivalTimeLabel")}
            value={arrivalTime}
            onChange={(e) => setArrivalTime(e.target.value)}
            disabled={deciding}
            required
          />
          <Textarea
            label={t("hqAcceptScheduleNoteLabel")}
            hint={t("hqAcceptScheduleNoteHint")}
            value={arrivalNote}
            onChange={(e) => setArrivalNote(e.target.value)}
            rows={4}
            maxLength={2000}
            disabled={deciding}
            required
            aria-required="true"
          />
        </div>
      </Modal>

      <Modal
        open={hqReturnOpen}
        onClose={() => (!deciding ? setHqReturnOpen(false) : undefined)}
        title={t("hqReturnTitle")}
        size="sm"
        footer={
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setHqReturnOpen(false)}
              disabled={deciding}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              loading={deciding}
              disabled={!hqReturnNoteOk || deciding}
              onClick={() => void submitHqReturn()}
            >
              {t("hqReturn")}
            </Button>
          </div>
        }
      >
        <div className="space-y-3">
          <p className="text-ecmp-text-primary">
            {t("hqReturnBody", { number: data?.complaintNumber ?? "" })}
          </p>
          <Select
            name="hqReturnReasonCode"
            label={t("hqReturnReasonLabel")}
            options={HQ_RETURN_REASON_CODES.map((code) => ({
              value: code,
              label: t(`hqReturnReason_${code}`),
            }))}
            value={hqReturnReasonCode}
            onChange={(e) =>
              setHqReturnReasonCode(e.target.value as CmBatch1HqReturnReasonCode)
            }
            disabled={deciding}
            required
          />
          <Textarea
            label={t("hqReturnNoteLabel")}
            hint={t("hqReturnNoteHint")}
            value={hqReturnNote}
            onChange={(e) => setHqReturnNote(e.target.value)}
            rows={4}
            maxLength={2000}
            disabled={deciding}
            required
            aria-required="true"
          />
        </div>
      </Modal>

      <Modal
        open={hqScheduleOpen}
        onClose={() => (!deciding ? setHqScheduleOpen(false) : undefined)}
        title={t("hqScheduleTitle")}
        size="sm"
        footer={
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setHqScheduleOpen(false)}
              disabled={deciding}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              loading={deciding}
              disabled={!hqScheduleReady}
              onClick={() => void submitHqSchedule()}
            >
              {t("hqScheduleSave")}
            </Button>
          </div>
        }
      >
        <div className="space-y-3">
          <p className="text-ecmp-text-primary">
            {t("hqScheduleBody", { number: data?.complaintNumber ?? "" })}
          </p>
          <Input
            name="arrivalDate"
            id="arrivalDate"
            type="date"
            label={t("hqArrivalDateLabel")}
            value={arrivalDate}
            onChange={(e) => setArrivalDate(e.target.value)}
            required
            aria-required="true"
            disabled={deciding}
          />
          <Input
            name="arrivalTime"
            id="arrivalTime"
            type="time"
            label={t("hqArrivalTimeLabel")}
            value={arrivalTime}
            onChange={(e) => setArrivalTime(e.target.value)}
            required
            aria-required="true"
            disabled={deciding}
          />
          <Textarea
            label={t("hqArrivalNoteLabel")}
            hint={t("hqArrivalNoteHint")}
            value={arrivalNote}
            onChange={(e) => setArrivalNote(e.target.value)}
            rows={3}
            maxLength={2000}
            disabled={deciding}
          />
        </div>
      </Modal>
    </PageContainer>
  );
}
