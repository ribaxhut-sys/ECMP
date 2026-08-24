"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ChangeEvent,
} from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  checkCmBatch1Duplicates,
  createCmBatch1Complaint,
  fetchBranches,
  recordCmBatch1DuplicateDecision,
  type Branch,
  type CmBatch1ComplaintBrief,
  type CmBatch1DuplicateCheckResponse,
} from "@/lib/api";
import { translateValidationErrors, resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { cn } from "@/shared/utils";
import { IconChevronDown } from "@/shared/icons";
import { useReasonPresets } from "@/shared/hooks";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Input,
  Modal,
  PageContainer,
  PageHeader,
  RadioGroup,
  SectionHeader,
  Select,
} from "@/shared/ui";
import { CustomerSearchPanel } from "./CustomerSearchPanel";
import { ActiveComplaintsBanner } from "./ActiveComplaintsBanner";
import { KnowledgeMentionTextarea } from "./KnowledgeMentionTextarea";
import { StagingAttachmentsPanel } from "./StagingAttachmentsPanel";
import { DuplicateWarningPanel } from "./DuplicateWarningPanel";
import { PresetTextField } from "./PresetTextField";
import {
  HqArrivalSlotPicker,
  type HqArrivalSlotValue,
} from "./HqArrivalSlotPicker";
import {
  createEmptyComplaintForm,
  newCmBatch1IdempotencyKey,
  newCmBatch1StagingToken,
  toCmBatch1CreateRequest,
  validateCmBatch1CreateForm,
  type CreateComplaintFieldErrors,
  type CreateComplaintFormValues,
} from "./createComplaintForm";
import {
  clearEscalateIntakeDraft,
  consumeIntakeFormResume,
  peekEscalateIntakeDraft,
  stashEscalateIntakeDraft,
  type IntakePriorityDraftIntent,
} from "./escalateIntakeDraft";
import {
  ESCALATE_TO_PUSAT_REASON_MIN,
  MAX_EXTRA_INTAKE_CASES,
  buildIntakeDecisionRows,
  createIntakeCasesForRegisteredComplaint,
  emptyExtraCaseDraft,
  extraIntakeCaseIssues,
  extrasFromDecisionRows,
  filledExtraCaseDrafts,
  anyIntakeCaseEscalates,
  intakeDecisionLockSummary,
  intakeMayEscalateToPusat,
  parseIntakeCaseAction,
  parseIntakePriority,
  sanitizeExtraCaseDrafts,
  validateIntakeCaseRow,
  type IntakeCaseAction,
  type IntakeCaseDecisionRow,
  type IntakeCaseRowIssue,
  type IntakeExtraCaseDraft,
} from "./intakeCaseDrafts";

const INTAKE_CASE_NOTE_PRESET_KEY = "cm_batch1.intake_case_note_presets";
const PRESET_KEYS = [INTAKE_CASE_NOTE_PRESET_KEY];
const PRIMARY_CASE_ID = "primary";

/**
 * Create Complaint — Mode A Batch-1 Aggregate intake.
 * One page: uraian, catatan, then per-Case decision (register / escalate / close).
 */
export function CreateComplaintView() {
  const router = useRouter();
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const tValidation = useTranslations("validation");
  const tErrors = useTranslations("errors");
  const tPriority = useTranslations("priority");
  const { user, hasPermission } = useAuth();
  const canCreate = hasPermission("complaints:create");
  const officerBranchId = user?.branchId ?? null;
  const presets = useReasonPresets(PRESET_KEYS);

  const [values, setValues] = useState<CreateComplaintFormValues>(() =>
    createEmptyComplaintForm({ branchId: officerBranchId, channel: "BRANCH" }),
  );
  const [errors, setErrors] = useState<CreateComplaintFieldErrors>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [infoMessage, setInfoMessage] = useState<string | null>(null);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [branchesError, setBranchesError] = useState<string | null>(null);
  const [overrideJustification, setOverrideJustification] = useState<
    string | null
  >(null);
  const [stagingToken, setStagingToken] = useState(() =>
    newCmBatch1StagingToken(),
  );
  const [hasStagedAttachments, setHasStagedAttachments] = useState(false);
  const [stagingBusy, setStagingBusy] = useState(false);
  /** False until session draft restore (if any) has been applied. */
  const [formReady, setFormReady] = useState(false);
  const [activeComplaints, setActiveComplaints] = useState<
    CmBatch1ComplaintBrief[]
  >([]);
  const [extraCaseDrafts, setExtraCaseDrafts] = useState<
    IntakeExtraCaseDraft[]
  >([]);
  const [extraCaseErrors, setExtraCaseErrors] = useState<
    Record<string, { subject?: string; description?: string; note?: string }>
  >({});
  const [case1Action, setCase1Action] = useState<IntakeCaseAction>("register");
  const [case1Locked, setCase1Locked] = useState(false);
  const [proposedArrival, setProposedArrival] =
    useState<HqArrivalSlotValue | null>(null);
  const [proposedArrivalError, setProposedArrivalError] = useState<
    string | null
  >(null);
  const [expandedIds, setExpandedIds] = useState<Record<string, boolean>>({
    [PRIMARY_CASE_ID]: true,
  });
  const [priorityError, setPriorityError] = useState<string | null>(null);
  const [escalationReasonMissing, setEscalationReasonMissing] = useState(false);
  const [escalateReasonTooShort, setEscalateReasonTooShort] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [linkError, setLinkError] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [duplicateOpen, setDuplicateOpen] = useState(false);
  const [duplicateBusy, setDuplicateBusy] = useState(false);
  const [duplicateResult, setDuplicateResult] =
    useState<CmBatch1DuplicateCheckResponse | null>(null);
  const submitIntentRef = useRef<IntakePriorityDraftIntent>("register");

  useEffect(() => {
    const draft = peekEscalateIntakeDraft();
    if (draft) {
      setValues(draft.values);
      setStagingToken(
        draft.stagingToken.trim() || newCmBatch1StagingToken(),
      );
      setHasStagedAttachments(Boolean(draft.hasStagedAttachments));
      setOverrideJustification(draft.overrideJustification);
      const extras = sanitizeExtraCaseDrafts(draft.extraCaseDrafts);
      setExtraCaseDrafts(extras);
      setCase1Action(parseIntakeCaseAction(draft.case1Action));
      setCase1Locked(draft.case1Locked === true);
      const proposedDate = draft.proposedArrivalDate?.trim() ?? "";
      const proposedTime = draft.proposedArrivalTime?.trim() ?? "";
      setProposedArrival(
        proposedDate ? { date: proposedDate, time: proposedTime } : null,
      );
      setExpandedIds({
        [PRIMARY_CASE_ID]: draft.case1Locked !== true,
        ...Object.fromEntries(
          extras.map((item) => [item.id, item.locked !== true]),
        ),
      });
    }
    consumeIntakeFormResume();
    setFormReady(true);
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setBranchesError(null);
      try {
        const res = await fetchBranches(100);
        if (cancelled) return;
        setBranches(res.data);
        const locked =
          (officerBranchId
            ? res.data.find((b) => b.id === officerBranchId)
            : null) ??
          res.data.find((b) => b.code.toUpperCase() === "PUSAT") ??
          null;
        if (locked) {
          setValues((prev) => ({
            ...prev,
            branchId: locked.id,
            channel: prev.channel || "BRANCH",
          }));
        }
      } catch (err) {
        if (!cancelled) {
          setBranchesError(
            resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError") ||
              t("unableToLoadBranches"),
          );
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [officerBranchId, t, tCommon, tErrors]);

  const lockedBranch = useMemo(() => {
    if (officerBranchId) {
      return branches.find((b) => b.id === officerBranchId) ?? null;
    }
    return branches.find((b) => b.code.toUpperCase() === "PUSAT") ?? null;
  }, [officerBranchId, branches]);

  const updateField = useCallback(
    <K extends keyof CreateComplaintFormValues>(
      key: K,
      value: CreateComplaintFormValues[K],
    ) => {
      setValues((prev) => ({ ...prev, [key]: value }));
      setErrors((prev) => {
        if (!prev[key]) return prev;
        const next = { ...prev };
        delete next[key];
        return next;
      });
    },
    [],
  );

  const onCustomerConfirmed = useCallback(
    (payload: { customerId: string; displayName: string }) => {
      setValues((prev) => ({
        ...prev,
        customerId: payload.customerId,
        customerName: payload.displayName,
      }));
      setErrors((prev) => {
        const next = { ...prev };
        delete next.customerId;
        delete next.customerName;
        return next;
      });
      setOverrideJustification(null);
      setInfoMessage(null);
    },
    [],
  );

  const onCustomerCleared = useCallback(() => {
    setValues((prev) => ({
      ...prev,
      customerId: "",
      customerName: "",
    }));
    setActiveComplaints([]);
    setOverrideJustification(null);
  }, []);

  const mayEscalate = intakeMayEscalateToPusat(lockedBranch?.code);
  const busy = stagingBusy || submitting || duplicateBusy;
  const priorityOptions = useMemo(
    () => [
      { value: "LOW", label: tPriority("LOW") },
      { value: "MEDIUM", label: tPriority("MEDIUM") },
      { value: "HIGH", label: tPriority("HIGH") },
      { value: "CRITICAL", label: tPriority("CRITICAL") },
    ],
    [tPriority],
  );

  if (!formReady) {
    return null;
  }

  function onTextChange(
    key: keyof CreateComplaintFormValues,
  ): (
    event: ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => void {
    return (event) => {
      updateField(
        key,
        event.target.value as CreateComplaintFormValues[typeof key],
      );
      setOverrideJustification(null);
    };
  }

  function onCancel(): void {
    clearEscalateIntakeDraft();
    router.push("/complaints");
  }

  function extraIssueMessage(
    kind: "required" | "max" | undefined,
    field: "subject" | "description" | "note",
  ): string | undefined {
    if (!kind) return undefined;
    if (kind === "max") {
      return tValidation(field === "subject" ? "subjectMax" : "descriptionMax", {
        max: field === "subject" ? 200 : 5000,
      });
    }
    if (field === "subject") return tValidation("subjectRequired");
    return tValidation(
      field === "note" ? "intakeNoteRequired" : "descriptionRequired",
    );
  }

  function patchExtraCase(
    id: string,
    patch: Partial<
      Pick<
        IntakeExtraCaseDraft,
        "description" | "note" | "priority" | "action" | "locked" | "subject"
      >
    >,
  ): void {
    setExtraCaseDrafts((prev) =>
      prev.map((item) => (item.id === id ? { ...item, ...patch } : item)),
    );
    setExtraCaseErrors((prev) => {
      if (!prev[id]) return prev;
      const field = { ...prev[id] };
      if (patch.subject !== undefined) delete field.subject;
      if (patch.description !== undefined) delete field.description;
      if (patch.note !== undefined) delete field.note;
      const next = { ...prev };
      if (!field.subject && !field.description && !field.note) delete next[id];
      else next[id] = field;
      return next;
    });
  }

  function toggleCaseExpanded(id: string): void {
    setExpandedIds((prev) => ({ ...prev, [id]: !prev[id] }));
  }

  function expandCase(id: string): void {
    setExpandedIds((prev) => ({ ...prev, [id]: true }));
  }

  function collapseCase(id: string): void {
    setExpandedIds((prev) => ({ ...prev, [id]: false }));
  }

  function lockedDecisionLabel(action: IntakeCaseAction): string {
    if (action === "close") return t("intakeCaseLockedClose");
    if (action === "escalate") return t("intakeCaseLockedEscalate");
    return t("intakeCaseLockedRegister");
  }

  function lockCase(id: string): void {
    if (id === PRIMARY_CASE_ID) {
      if (!values.description.trim()) {
        setErrors((prev) => ({
          ...prev,
          description: extraIssueMessage("required", "description"),
        }));
        expandCase(PRIMARY_CASE_ID);
        document.getElementById("description")?.focus();
        return;
      }
      const row = buildIntakeDecisionRows(
        values,
        filledExtraCaseDrafts(extraCaseDrafts),
        case1Action,
      )[0];
      if (!row) return;
      const issue = validateIntakeCaseRow(row);
      if (issue) {
        applyRowIssue(row, issue);
        return;
      }
      if (!ensureProposedArrivalForEscalate(case1Action === "escalate")) {
        expandCase(PRIMARY_CASE_ID);
        return;
      }
      setCase1Locked(true);
      collapseCase(PRIMARY_CASE_ID);
      return;
    }

    const draft = extraCaseDrafts.find((item) => item.id === id);
    if (!draft) return;
    const extraIssues = extraIntakeCaseIssues([draft]);
    if (extraIssues.length > 0) {
      const issue = extraIssues[0]!;
      setExtraCaseErrors((prev) => ({
        ...prev,
        [id]: {
          subject: extraIssueMessage(issue.subject, "subject"),
          description: extraIssueMessage(issue.description, "description"),
          note: extraIssueMessage(issue.note, "note"),
        },
      }));
      expandCase(id);
      const focusId = issue.subject
        ? `extraCase-subject-${id}`
        : issue.description
          ? `extraCase-${id}`
          : `extraCase-note-${id}`;
      document.getElementById(focusId)?.focus();
      return;
    }
    const row = buildIntakeDecisionRows(
      values,
      filledExtraCaseDrafts(extraCaseDrafts),
      case1Action,
      case1Locked,
    ).find((item) => item.id === id);
    if (!row) {
      expandCase(id);
      return;
    }
    const issue = validateIntakeCaseRow(row);
    if (issue) {
      applyRowIssue(row, issue);
      return;
    }
    if (!ensureProposedArrivalForEscalate(row.action === "escalate")) {
      expandCase(id);
      return;
    }
    patchExtraCase(id, { locked: true });
    collapseCase(id);
  }

  function unlockCase(id: string): void {
    if (id === PRIMARY_CASE_ID) {
      setCase1Locked(false);
    } else {
      patchExtraCase(id, { locked: false });
    }
    expandCase(id);
  }

  function actionLabel(action: IntakeCaseAction): string {
    if (action === "close") return t("submitCloseCase");
    if (action === "escalate") return t("submitEscalateCase");
    return t("submitRegisterCase");
  }

  function proposedArrivalComplete(): boolean {
    return Boolean(proposedArrival?.date.trim() && proposedArrival?.time.trim());
  }

  function ensureProposedArrivalForEscalate(needsSlot: boolean): boolean {
    if (!needsSlot) return true;
    if (proposedArrivalComplete()) {
      setProposedArrivalError(null);
      return true;
    }
    setProposedArrivalError(t("intakeProposedArrivalRequired"));
    return false;
  }

  function proposedArrivalHostId(): string | null {
    if (case1Action === "escalate") return PRIMARY_CASE_ID;
    const extra = extraCaseDrafts.find(
      (item) => parseIntakeCaseAction(item.action) === "escalate",
    );
    return extra?.id ?? null;
  }

  function proposedArrivalPicker(locked: boolean) {
    return (
      <div className="space-y-2 rounded-[var(--ecmp-radius-md)] border border-ecmp-border p-3">
        <p className="text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary">
          {t("intakeProposedArrivalTitle")}
        </p>
        <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
          {t("intakeProposedArrivalHint")}
        </p>
        <HqArrivalSlotPicker
          value={proposedArrival}
          onChange={(next) => {
            setProposedArrival(next);
            if (next?.date.trim() && next?.time.trim()) {
              setProposedArrivalError(null);
            }
          }}
          disabled={busy || locked}
        />
        {proposedArrivalError ? (
          <Alert
            tone="danger"
            title={t("intakeProposedArrivalRequired")}
          />
        ) : null}
      </div>
    );
  }

  function proposedArrivalFollowNote() {
    return (
      <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
        {proposedArrivalComplete()
          ? t("intakeProposedArrivalFollow", {
              date: proposedArrival!.date,
              time: proposedArrival!.time,
            })
          : t("intakeProposedArrivalFollowPending")}
      </p>
    );
  }

  function currentRows(): IntakeCaseDecisionRow[] {
    const extras = filledExtraCaseDrafts(extraCaseDrafts);
    return buildIntakeDecisionRows(
      values,
      extras,
      case1Action,
      case1Locked,
    ).map(
      (row): IntakeCaseDecisionRow =>
        !mayEscalate && row.action === "escalate"
          ? { ...row, action: "register" }
          : row,
    );
  }

  function stashCurrentDraft(extras = filledExtraCaseDrafts(extraCaseDrafts)): void {
    stashEscalateIntakeDraft({
      values,
      stagingToken,
      hasStagedAttachments,
      overrideJustification,
      recordingUnitCode: lockedBranch?.code ?? null,
      extraCaseDrafts: extras,
      case1Action,
      case1Locked,
      proposedArrivalDate: proposedArrival?.date ?? null,
      proposedArrivalTime: proposedArrival?.time ?? null,
    });
  }

  function validateIntakeForm(): CreateComplaintFieldErrors {
    const nextErrors = translateValidationErrors(
      validateCmBatch1CreateForm(values),
      tValidation,
    );
    if (!values.resolution.trim() && !nextErrors.resolution) {
      nextErrors.resolution = tValidation("intakeNoteRequired");
    }
    return nextErrors;
  }

  function applyRowIssue(row: IntakeCaseDecisionRow, issue: IntakeCaseRowIssue): void {
    expandCase(row.id === "primary" ? PRIMARY_CASE_ID : row.id);
    if (issue === "priority") {
      setPriorityError(tValidation("priorityRequired"));
      setEscalationReasonMissing(false);
      setEscalateReasonTooShort(false);
      window.setTimeout(() => {
        document.getElementById(`case-priority-${row.id}`)?.focus();
      }, 0);
      return;
    }
    if (issue === "note") {
      setEscalationReasonMissing(true);
      setEscalateReasonTooShort(false);
      setPriorityError(null);
      window.setTimeout(() => {
        document
          .getElementById(row.id === "primary" ? "resolution" : `extraCase-note-${row.id}`)
          ?.focus();
      }, 0);
      return;
    }
    setEscalateReasonTooShort(true);
    setEscalationReasonMissing(false);
    setPriorityError(null);
    window.setTimeout(() => {
      document
        .getElementById(row.id === "primary" ? "resolution" : `extraCase-note-${row.id}`)
        ?.focus();
    }, 0);
  }

  function collectFormIssues(): boolean {
    const nextErrors = validateIntakeForm();
    const nextExtraIssues = extraIntakeCaseIssues(extraCaseDrafts);
    const nextExtraErrors: Record<
      string,
      { subject?: string; description?: string; note?: string }
    > = {};
    for (const issue of nextExtraIssues) {
      nextExtraErrors[issue.id] = {
        subject: extraIssueMessage(issue.subject, "subject"),
        description: extraIssueMessage(issue.description, "description"),
        note: extraIssueMessage(issue.note, "note"),
      };
    }
    setErrors(nextErrors);
    setExtraCaseErrors(nextExtraErrors);
    if (Object.keys(nextErrors).length > 0 || nextExtraIssues.length > 0) {
      const firstKey = Object.keys(nextErrors)[0];
      const firstExtra = nextExtraIssues[0];
      if (firstExtra) expandCase(firstExtra.id);
      const el = firstKey
        ? document.getElementById(firstKey)
        : firstExtra
          ? document.getElementById(
              firstExtra.subject
                ? `extraCase-subject-${firstExtra.id}`
                : firstExtra.description
                  ? `extraCase-${firstExtra.id}`
                  : `extraCase-note-${firstExtra.id}`,
            )
          : null;
      el?.focus();
      return false;
    }
    return true;
  }

  function ensureCaseDecisions(rows: IntakeCaseDecisionRow[]): boolean {
    for (const row of rows) {
      const issue = validateIntakeCaseRow(row);
      if (issue) {
        applyRowIssue(row, issue);
        return false;
      }
    }
    setPriorityError(null);
    setEscalationReasonMissing(false);
    setEscalateReasonTooShort(false);
    return true;
  }

  function withPriority(
    form: CreateComplaintFormValues,
    rows: IntakeCaseDecisionRow[],
  ): CreateComplaintFormValues {
    const p = parseIntakePriority(rows[0]?.priority);
    const nextPriority =
      p === "LOW" || p === "MEDIUM" || p === "HIGH" || p === "CRITICAL"
        ? p
        : form.priority;
    return {
      ...form,
      priority: nextPriority,
      resolution: rows[0]?.note ?? form.resolution,
    };
  }

  async function createAggregate(
    form: CreateComplaintFormValues,
    justification: string | null,
    token: string,
    rows: IntakeCaseDecisionRow[],
  ): Promise<void> {
    const prioritized = withPriority(form, rows);
    const escalate = anyIntakeCaseEscalates(rows);
    const escalateRow = rows.find((row) => row.action === "escalate");
    const payload =
      escalate && escalateRow
        ? { ...prioritized, resolution: escalateRow.note }
        : prioritized;
    const response = await createCmBatch1Complaint(
      toCmBatch1CreateRequest(payload, {
        duplicateOverrideJustification: justification,
        stagingToken: token.trim() || null,
        escalate,
        recordingUnitCode: lockedBranch?.code ?? null,
        proposedArrivalDate: escalate ? proposedArrival?.date ?? null : null,
        proposedArrivalTime: escalate ? proposedArrival?.time ?? null : null,
      }),
      { idempotencyKey: newCmBatch1IdempotencyKey() },
    );
    await createIntakeCasesForRegisteredComplaint({
      complaintId: response.data.complaintId,
      values: prioritized,
      extraDrafts: extrasFromDecisionRows(rows),
      destinationUnitId:
        lockedBranch?.code?.trim() || prioritized.branchId.trim() || "",
      rows,
    });
    clearEscalateIntakeDraft();
    router.push(
      `/complaints/cm/${encodeURIComponent(response.data.complaintId)}`,
    );
  }

  async function submitDecisions(): Promise<void> {
    if (!canCreate) return;
    const rows = currentRows();
    submitIntentRef.current = "register";
    setSubmitting(true);
    try {
      if (overrideJustification) {
        await createAggregate(values, overrideJustification, stagingToken, rows);
        return;
      }
      const dup = await checkCmBatch1Duplicates({
        customerId: values.customerId.trim(),
        category: values.category.trim() || "GENERAL",
        subject: values.subject.trim(),
        channel: values.channel.trim(),
      });
      setDuplicateResult(dup.data);
      if (dup.data.warning) {
        setDuplicateOpen(true);
        return;
      }
      await createAggregate(values, null, stagingToken, rows);
    } catch (err) {
      setLinkError(false);
      setSubmitError(
        resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError") ||
          t("unableToCreate"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  function requestConfirm(): void {
    if (!canCreate) return;
    setSubmitError(null);
    setLinkError(false);
    setEscalationReasonMissing(false);
    setEscalateReasonTooShort(false);
    setInfoMessage(null);
    if (!collectFormIssues()) return;
    const extras = filledExtraCaseDrafts(extraCaseDrafts);
    setExtraCaseDrafts(extras);
    const rows = buildIntakeDecisionRows(
      values,
      extras,
      case1Action,
      case1Locked,
    ).map(
      (row): IntakeCaseDecisionRow =>
        !mayEscalate && row.action === "escalate"
          ? { ...row, action: "register" }
          : row,
    );
    if (!ensureCaseDecisions(rows)) return;
    const lockSummary = intakeDecisionLockSummary(rows);
    if (lockSummary.requiresLock && !lockSummary.allLocked) return;
    if (!ensureProposedArrivalForEscalate(anyIntakeCaseEscalates(rows))) {
      const host = rows.find((row) => row.action === "escalate");
      if (host) expandCase(host.id === "primary" ? PRIMARY_CASE_ID : host.id);
      return;
    }
    stashCurrentDraft(extras);
    setConfirmOpen(true);
  }

  function closeConfirm(): void {
    if (submitting) return;
    setConfirmOpen(false);
  }

  function stagingTokenForLink(): string | null {
    if (!hasStagedAttachments) return null;
    return stagingToken.trim() || null;
  }

  async function onDuplicateDecide(payload: {
    decision: "link_existing" | "override" | "recommend_only" | "blocked";
    survivingComplaintId?: string;
    justification?: string;
  }): Promise<void> {
    const rows = currentRows();
    setDuplicateBusy(true);
    setSubmitError(null);
    setLinkError(false);
    try {
      if (payload.decision === "recommend_only") {
        await recordCmBatch1DuplicateDecision({
          decision: "recommend_only",
          customerId: values.customerId.trim(),
          survivingComplaintId: payload.survivingComplaintId,
        });
        setDuplicateOpen(false);
        setInfoMessage(t("recommendOnlyRecorded"));
        return;
      }
      if (payload.decision === "link_existing") {
        const surviving = payload.survivingComplaintId?.trim();
        if (!surviving) {
          setLinkError(true);
          setSubmitError(t("survivingIdRequired"));
          return;
        }
        await recordCmBatch1DuplicateDecision({
          decision: "link_existing",
          customerId: values.customerId.trim(),
          survivingComplaintId: surviving,
          stagingToken: stagingTokenForLink(),
        });
        clearEscalateIntakeDraft();
        setDuplicateOpen(false);
        router.replace(`/complaints/cm/${encodeURIComponent(surviving)}`);
        return;
      }
      if (payload.decision === "override") {
        const justification = payload.justification?.trim() ?? "";
        setOverrideJustification(justification);
        stashEscalateIntakeDraft({
          values,
          stagingToken,
          hasStagedAttachments,
          overrideJustification: justification,
          recordingUnitCode: lockedBranch?.code ?? null,
          extraCaseDrafts: filledExtraCaseDrafts(extraCaseDrafts),
          case1Action,
          case1Locked,
          proposedArrivalDate: proposedArrival?.date ?? null,
          proposedArrivalTime: proposedArrival?.time ?? null,
        });
        setDuplicateOpen(false);
        setSubmitting(true);
        try {
          await createAggregate(values, justification, stagingToken, rows);
        } finally {
          setSubmitting(false);
        }
        return;
      }
      if (payload.decision === "blocked") {
        await recordCmBatch1DuplicateDecision({
          decision: "blocked",
          customerId: values.customerId.trim(),
        });
        setDuplicateOpen(false);
        setSubmitError(t("createBlockedByDuplicate"));
      }
    } catch (err) {
      setLinkError(payload.decision === "link_existing");
      setSubmitError(
        resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError") ||
          t("unableToRecordDuplicateDecision"),
      );
    } finally {
      setDuplicateBusy(false);
    }
  }

  async function onLinkExistingActive(payload: {
    survivingComplaintId: string;
    label: string;
  }): Promise<void> {
    if (!canCreate) return;
    const surviving = payload.survivingComplaintId.trim();
    if (!surviving) {
      setLinkError(true);
      setSubmitError(t("survivingIdRequired"));
      return;
    }
    setDuplicateBusy(true);
    setSubmitError(null);
    setLinkError(true);
    try {
      await recordCmBatch1DuplicateDecision({
        decision: "link_existing",
        customerId: values.customerId.trim(),
        survivingComplaintId: surviving,
        stagingToken: stagingTokenForLink(),
      });
      clearEscalateIntakeDraft();
      router.replace(`/complaints/cm/${encodeURIComponent(surviving)}`);
    } catch (err) {
      setSubmitError(
        resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError") ||
          t("unableToRecordDuplicateDecision"),
      );
    } finally {
      setDuplicateBusy(false);
    }
  }

  const lockSummary = intakeDecisionLockSummary(currentRows());
  const applyBlockedByLock = lockSummary.requiresLock && !lockSummary.allLocked;

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("create")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title"), href: "/complaints" },
          { label: tCommon("create") },
        ]}
        description={t("batch1IntakeDescription")}
      />

      {!canCreate ? (
        <Alert
          tone="warning"
          title={t("createRestrictedTitle")}
          description={t("createAccessRestrictedDescription")}
        />
      ) : null}

      <form
        noValidate
        onSubmit={(event) => {
          event.preventDefault();
        }}
        aria-label={t("createFormAriaLabel")}
        className="space-y-[var(--ecmp-section-gap)]"
      >
        {escalationReasonMissing ? (
          <Alert
            tone="danger"
            title={t("intakeNoteMissingTitle")}
            description={t("intakeNoteMissingDescription")}
          />
        ) : null}

        {escalateReasonTooShort ? (
          <Alert
            tone="danger"
            title={t("intakeEscalateReasonMinTitle")}
            description={t("intakeEscalateReasonMinDescription", {
              min: ESCALATE_TO_PUSAT_REASON_MIN,
            })}
          />
        ) : null}

        {submitError ? (
          <Alert
            tone="danger"
            title={
              linkError
                ? t("unableToRecordDuplicateDecision")
                : t("couldNotCreate")
            }
            description={submitError}
          />
        ) : null}

        {infoMessage ? (
          <Alert tone="info" title={t("notice")} description={infoMessage} />
        ) : null}

        {branchesError ? (
          <Alert
            tone="danger"
            title={t("couldNotLoadBranches")}
            description={branchesError}
          />
        ) : null}

        <fieldset
          disabled={!canCreate}
          className="min-w-0 space-y-[var(--ecmp-section-gap)] border-0 p-0"
        >
        <CustomerSearchPanel
          confirmedCustomerId={values.customerId}
          confirmedDisplayName={values.customerName}
          onConfirmed={onCustomerConfirmed}
          onCleared={onCustomerCleared}
          onActiveComplaintsChange={setActiveComplaints}
          disabled={stagingBusy}
        />

        {values.customerId.trim() ? (
          <ActiveComplaintsBanner
            complaints={activeComplaints}
            disabled={busy}
            linking={duplicateBusy}
            onLinkExisting={onLinkExistingActive}
          />
        ) : null}

        {(errors.customerId || errors.customerName) && !values.customerId ? (
          <Alert
            tone="danger"
            title={t("customerRequiredTitle")}
            description={
              errors.customerId ||
              errors.customerName ||
              t("confirmCustomerBeforeCreating")
            }
          />
        ) : null}

        <section className="space-y-[var(--ecmp-panel-gap)]">
          <SectionHeader
            id="section-complaint-info"
            title={t("complaintInformation")}
            description={t("complaintInformationDescription")}
          />
          <Card>
            <CardBody>
              <fieldset
                aria-labelledby="section-complaint-info"
                className="grid grid-cols-1 gap-[var(--ecmp-form-gap)]"
              >
                <legend className="sr-only">{t("complaintInformation")}</legend>
                <Input
                  name="subject"
                  id="subject"
                  label={t("subject")}
                  required
                  maxLength={200}
                  value={values.subject}
                  onChange={onTextChange("subject")}
                  error={errors.subject}
                  aria-required="true"
                  autoComplete="off"
                />
                <div className="space-y-3 rounded-[var(--ecmp-radius-md)] border border-ecmp-border p-3">
                  <div className="flex items-center justify-between gap-2">
                    <button
                      type="button"
                      className="flex min-w-0 flex-1 items-center gap-2 rounded-[var(--ecmp-radius-sm)] px-1 py-1 text-left hover:bg-ecmp-hover"
                      aria-expanded={expandedIds[PRIMARY_CASE_ID] !== false}
                      aria-controls="intake-case-panel-primary"
                      aria-label={t("intakeCaseToggleAria", {
                        n: 1,
                        action:
                          expandedIds[PRIMARY_CASE_ID] !== false
                            ? t("intakeCaseCollapse")
                            : t("intakeCaseExpand"),
                      })}
                      onClick={() => toggleCaseExpanded(PRIMARY_CASE_ID)}
                    >
                      <IconChevronDown
                        className={cn(
                          "size-4 shrink-0 text-ecmp-text-secondary transition-transform",
                          expandedIds[PRIMARY_CASE_ID] === false && "-rotate-90",
                        )}
                      />
                      <span className="min-w-0">
                        <h3 className="text-[length:var(--ecmp-font-body-size)] font-semibold text-ecmp-text-primary">
                          {case1Locked
                            ? t("intakeCaseDecisionHeadingLocked", {
                                n: 1,
                                decision: lockedDecisionLabel(case1Action),
                              })
                            : t("intakeCaseDecisionHeading", { n: 1 })}
                        </h3>
                        {expandedIds[PRIMARY_CASE_ID] === false ? (
                          <p className="truncate text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                            {actionLabel(case1Action)}
                            {values.description.trim()
                              ? ` · ${values.description.trim()}`
                              : ""}
                          </p>
                        ) : null}
                      </span>
                    </button>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      aria-expanded={expandedIds[PRIMARY_CASE_ID] !== false}
                      onClick={() => toggleCaseExpanded(PRIMARY_CASE_ID)}
                    >
                      {expandedIds[PRIMARY_CASE_ID] !== false
                        ? t("intakeCaseCollapse")
                        : t("intakeCaseExpand")}
                    </Button>
                  </div>
                  {expandedIds[PRIMARY_CASE_ID] !== false ? (
                    <div id="intake-case-panel-primary" className="space-y-3">
                  <KnowledgeMentionTextarea
                    name="description"
                    id="description"
                    label={t("intakeCaseDescriptionLabel")}
                    required
                    rows={5}
                    maxLength={5000}
                    value={values.description}
                    onChange={(next) => updateField("description", next)}
                    error={errors.description}
                    hint={t("intakeCase1Hint", {
                      count: values.description.trim().length,
                      max: 5000,
                    })}
                    disabled={busy || case1Locked}
                  />
                  <div className="max-w-xs">
                    <Select
                      name="case-priority-primary"
                      id="case-priority-primary"
                      label={t("priority")}
                      placeholder={t("selectPriorityPlaceholder")}
                      options={priorityOptions}
                      value={values.priority}
                      onChange={(event) => {
                        updateField(
                          "priority",
                          event.target.value as CreateComplaintFormValues["priority"],
                        );
                        setPriorityError(null);
                      }}
                      error={
                        priorityError && !parseIntakePriority(values.priority)
                          ? priorityError
                          : undefined
                      }
                      required
                      aria-required="true"
                      disabled={busy || case1Locked}
                    />
                  </div>
                  <PresetTextField
                    presets={presets[INTAKE_CASE_NOTE_PRESET_KEY] ?? []}
                    name="resolution"
                    id="resolution"
                    label={t("intakeNoteLabel")}
                    required
                    rows={4}
                    maxLength={5000}
                    value={values.resolution}
                    onChange={(next) => {
                      updateField("resolution", next);
                      setOverrideJustification(null);
                      if (next.trim()) setEscalationReasonMissing(false);
                      if (next.trim().length >= ESCALATE_TO_PUSAT_REASON_MIN) {
                        setEscalateReasonTooShort(false);
                      }
                    }}
                    error={
                      errors.resolution ||
                      (escalationReasonMissing && !values.resolution.trim()
                        ? tValidation("intakeNoteRequired")
                        : escalateReasonTooShort &&
                            case1Action === "escalate" &&
                            values.resolution.trim().length <
                              ESCALATE_TO_PUSAT_REASON_MIN
                          ? tValidation("escalationReasonMin", {
                              min: ESCALATE_TO_PUSAT_REASON_MIN,
                            })
                          : undefined)
                    }
                    hint={
                      case1Action === "escalate"
                        ? t("intakeEscalateReasonHint", {
                            min: ESCALATE_TO_PUSAT_REASON_MIN,
                          })
                        : t("intakeNoteHint", {
                            count: values.resolution.trim().length,
                            max: 5000,
                          })
                    }
                    disabled={busy || case1Locked}
                  />
                  <RadioGroup
                    name="case-action-primary"
                    label={t("intakeCaseActionLabel")}
                    orientation="horizontal"
                    required
                    disabled={busy || case1Locked}
                    value={case1Action}
                    onChange={(value) =>
                      setCase1Action(parseIntakeCaseAction(value))
                    }
                    options={[
                      { value: "register", label: t("submitRegisterCase") },
                      ...(mayEscalate
                        ? [
                            {
                              value: "escalate",
                              label: t("submitEscalateCase"),
                            },
                          ]
                        : []),
                      { value: "close", label: t("submitCloseCase") },
                    ]}
                  />
                  {proposedArrivalHostId() === PRIMARY_CASE_ID
                    ? proposedArrivalPicker(case1Locked)
                    : null}
                  <Button
                    type="button"
                    variant={case1Locked ? "outline" : "secondary"}
                    size="sm"
                    disabled={busy}
                    aria-label={
                      case1Locked
                        ? t("intakeUnlockCaseDecisionAria", { n: 1 })
                        : t("intakeLockCaseDecisionAria", { n: 1 })
                    }
                    onClick={() =>
                      case1Locked
                        ? unlockCase(PRIMARY_CASE_ID)
                        : lockCase(PRIMARY_CASE_ID)
                    }
                  >
                    {case1Locked
                      ? t("intakeUnlockCaseDecision")
                      : t("intakeLockCaseDecision")}
                  </Button>
                    </div>
                  ) : null}
                </div>
                {extraCaseDrafts.map((draft, index) => {
                  const extraExpanded = expandedIds[draft.id] !== false;
                  const extraAction = parseIntakeCaseAction(draft.action);
                  const extraLocked = draft.locked === true;
                  const extraN = index + 2;
                  return (
                  <div
                    key={draft.id}
                    className="space-y-3 rounded-[var(--ecmp-radius-md)] border border-ecmp-border p-3"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <button
                        type="button"
                        className="flex min-w-0 flex-1 items-center gap-2 rounded-[var(--ecmp-radius-sm)] px-1 py-1 text-left hover:bg-ecmp-hover"
                        aria-expanded={extraExpanded}
                        aria-controls={`intake-case-panel-${draft.id}`}
                        aria-label={t("intakeCaseToggleAria", {
                          n: extraN,
                          action: extraExpanded
                            ? t("intakeCaseCollapse")
                            : t("intakeCaseExpand"),
                        })}
                        onClick={() => toggleCaseExpanded(draft.id)}
                      >
                        <IconChevronDown
                          className={cn(
                            "size-4 shrink-0 text-ecmp-text-secondary transition-transform",
                            !extraExpanded && "-rotate-90",
                          )}
                        />
                        <span className="min-w-0">
                          <h3 className="text-[length:var(--ecmp-font-body-size)] font-semibold text-ecmp-text-primary">
                            {extraLocked
                              ? t("intakeCaseDecisionHeadingLocked", {
                                  n: extraN,
                                  decision: lockedDecisionLabel(extraAction),
                                })
                              : t("intakeCaseDecisionHeading", { n: extraN })}
                          </h3>
                          {!extraExpanded ? (
                            <p className="truncate text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                              {actionLabel(extraAction)}
                              {draft.description.trim()
                                ? ` · ${draft.description.trim()}`
                                : ""}
                            </p>
                          ) : null}
                        </span>
                      </button>
                      <div className="flex shrink-0 items-center gap-2">
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          aria-expanded={extraExpanded}
                          onClick={() => toggleCaseExpanded(draft.id)}
                        >
                          {extraExpanded
                            ? t("intakeCaseCollapse")
                            : t("intakeCaseExpand")}
                        </Button>
                        <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        disabled={busy}
                        onClick={() => {
                          const filled =
                            draft.description.trim().length > 0 ||
                            (draft.note ?? "").trim().length > 0;
                          if (
                            filled &&
                            !window.confirm(t("intakeExtraCaseDiscardConfirm"))
                          ) {
                            return;
                          }
                          setExtraCaseDrafts((prev) =>
                            prev.filter((item) => item.id !== draft.id),
                          );
                          setExtraCaseErrors((prev) => {
                            if (!prev[draft.id]) return prev;
                            const next = { ...prev };
                            delete next[draft.id];
                            return next;
                          });
                        }}
                      >
                        {tCommon("cancel")}
                      </Button>
                      </div>
                    </div>
                    {extraExpanded ? (
                    <div
                      id={`intake-case-panel-${draft.id}`}
                      className="space-y-3"
                    >
                    <Input
                      name={`extraCase-subject-${draft.id}`}
                      id={`extraCase-subject-${draft.id}`}
                      label={t("intakeCaseSubjectLabel")}
                      required
                      maxLength={200}
                      value={draft.subject ?? ""}
                      onChange={(event) =>
                        patchExtraCase(draft.id, { subject: event.target.value })
                      }
                      error={extraCaseErrors[draft.id]?.subject}
                      disabled={busy || extraLocked}
                    />
                    <KnowledgeMentionTextarea
                      name={`extraCase-${draft.id}`}
                      id={`extraCase-${draft.id}`}
                      label={t("intakeCaseDescriptionLabel")}
                      required
                      rows={4}
                      maxLength={5000}
                      value={draft.description}
                      onChange={(next) =>
                        patchExtraCase(draft.id, { description: next })
                      }
                      error={extraCaseErrors[draft.id]?.description}
                      hint={t("charCounter", {
                        count: draft.description.trim().length,
                        max: 5000,
                      })}
                      disabled={busy || extraLocked}
                    />
                    <div className="max-w-xs">
                      <Select
                        name={`case-priority-${draft.id}`}
                        id={`case-priority-${draft.id}`}
                        label={t("priority")}
                        placeholder={t("selectPriorityPlaceholder")}
                        options={priorityOptions}
                        value={draft.priority ?? ""}
                        onChange={(event) => {
                          patchExtraCase(draft.id, {
                            priority: event.target.value,
                          });
                          setPriorityError(null);
                        }}
                        error={
                          priorityError &&
                          !parseIntakePriority(draft.priority)
                            ? priorityError
                            : undefined
                        }
                        required
                        aria-required="true"
                        disabled={busy || extraLocked}
                      />
                    </div>
                    <PresetTextField
                      presets={presets[INTAKE_CASE_NOTE_PRESET_KEY] ?? []}
                      name={`extraCase-note-${draft.id}`}
                      id={`extraCase-note-${draft.id}`}
                      label={t("intakeNoteLabel")}
                      required
                      rows={4}
                      maxLength={5000}
                      value={draft.note ?? ""}
                      onChange={(next) => {
                        patchExtraCase(draft.id, { note: next });
                        if (next.trim()) setEscalationReasonMissing(false);
                        if (
                          next.trim().length >= ESCALATE_TO_PUSAT_REASON_MIN
                        ) {
                          setEscalateReasonTooShort(false);
                        }
                      }}
                      error={
                        extraCaseErrors[draft.id]?.note ||
                        (escalationReasonMissing && !(draft.note ?? "").trim()
                          ? tValidation("intakeNoteRequired")
                          : escalateReasonTooShort &&
                              extraAction === "escalate" &&
                              (draft.note ?? "").trim().length <
                                ESCALATE_TO_PUSAT_REASON_MIN
                            ? tValidation("escalationReasonMin", {
                                min: ESCALATE_TO_PUSAT_REASON_MIN,
                              })
                            : undefined)
                      }
                      hint={
                        extraAction === "escalate"
                          ? t("intakeEscalateReasonHint", {
                              min: ESCALATE_TO_PUSAT_REASON_MIN,
                            })
                          : t("intakeNoteHint", {
                              count: (draft.note ?? "").trim().length,
                              max: 5000,
                            })
                      }
                      disabled={busy || extraLocked}
                    />
                    <RadioGroup
                      name={`case-action-${draft.id}`}
                      label={t("intakeCaseActionLabel")}
                      orientation="horizontal"
                      required
                      disabled={busy || extraLocked}
                      value={extraAction}
                      onChange={(value) =>
                        patchExtraCase(draft.id, {
                          action: parseIntakeCaseAction(value),
                        })
                      }
                      options={[
                        { value: "register", label: t("submitRegisterCase") },
                        ...(mayEscalate
                          ? [
                              {
                                value: "escalate",
                                label: t("submitEscalateCase"),
                              },
                            ]
                          : []),
                        { value: "close", label: t("submitCloseCase") },
                      ]}
                    />
                    {proposedArrivalHostId() === draft.id
                      ? proposedArrivalPicker(extraLocked)
                      : extraAction === "escalate"
                        ? proposedArrivalFollowNote()
                        : null}
                    <Button
                      type="button"
                      variant={extraLocked ? "outline" : "secondary"}
                      size="sm"
                      disabled={busy}
                      aria-label={
                        extraLocked
                          ? t("intakeUnlockCaseDecisionAria", { n: extraN })
                          : t("intakeLockCaseDecisionAria", { n: extraN })
                      }
                      onClick={() =>
                        extraLocked
                          ? unlockCase(draft.id)
                          : lockCase(draft.id)
                      }
                    >
                      {extraLocked
                        ? t("intakeUnlockCaseDecision")
                        : t("intakeLockCaseDecision")}
                    </Button>
                    </div>
                    ) : null}
                  </div>
                  );
                })}
                {extraCaseDrafts.length < MAX_EXTRA_INTAKE_CASES ? (
                  <Button
                    type="button"
                    variant="outline"
                    disabled={busy}
                    onClick={() => {
                      const next = emptyExtraCaseDraft();
                      setExtraCaseDrafts((prev) => [...prev, next]);
                      setExpandedIds((prev) => ({ ...prev, [next.id]: true }));
                    }}
                  >
                    {t("penangananAddCase")}
                  </Button>
                ) : (
                  <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                    {t("intakeExtraCaseMax")}
                  </p>
                )}
                <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                  {t("intakeExtraCaseRegisterHint")}
                </p>
                {lockSummary.requiresLock ? (
                  <p
                    data-testid="intake-case-lock-summary"
                    className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary"
                  >
                    {t("intakeCaseLockSummary", {
                      total: lockSummary.total,
                      locked: lockSummary.locked,
                      escalate: lockSummary.escalate,
                    })}
                    {!lockSummary.allLocked
                      ? ` ${t("intakeCaseLockRequiredHint")}`
                      : ""}
                  </p>
                ) : null}
              </fieldset>
            </CardBody>
          </Card>
        </section>

        {overrideJustification ? (
          <Alert
            tone="warning"
            title={t("duplicateOverrideArmed")}
            description={t("duplicateOverrideArmedDescription")}
          />
        ) : null}

        <StagingAttachmentsPanel
          stagingToken={stagingToken}
          customerId={values.customerId}
          disabled={stagingBusy}
          onStagingTokenResolved={setStagingToken}
          onHasStagedChange={setHasStagedAttachments}
          onBusyChange={setStagingBusy}
        />
        </fieldset>

        <div className="flex flex-col-reverse gap-[var(--ecmp-form-gap)] border-t border-ecmp-border pt-[var(--ecmp-panel-gap)] sm:flex-row sm:flex-wrap sm:justify-end">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={busy}
            aria-label={t("backAriaLabel")}
          >
            {tCommon("back")}
          </Button>
          <Button
            type="button"
            loading={submitting}
            disabled={!canCreate || busy || applyBlockedByLock}
            onClick={requestConfirm}
            aria-label={t("submitCaseDecisionsAriaLabel")}
          >
            {submitting ? t("creating") : t("submitCaseDecisions")}
          </Button>
        </div>
      </form>

      <Modal
        open={confirmOpen}
        onClose={closeConfirm}
        title={t("confirmCaseDecisionsTitle")}
        size="sm"
        footer={
          <>
            <Button
              type="button"
              variant="outline"
              disabled={submitting}
              onClick={closeConfirm}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              variant="primary"
              disabled={submitting}
              onClick={() => {
                setConfirmOpen(false);
                void submitDecisions();
              }}
            >
              {t("confirmCaseDecisionsAction")}
            </Button>
          </>
        }
      >
        <div className="space-y-3 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
          <p>
            {t("confirmCaseDecisionsLead", {
              customer: values.customerName.trim() || values.customerId.trim(),
              subject: values.subject.trim(),
            })}
          </p>
          <ul className="list-none space-y-1.5 text-ecmp-text-primary">
            {currentRows().map((row) => (
              <li key={row.n}>
                <span className="font-medium">
                  {t("confirmCaseDecisionLabel", { n: row.n })}
                </span>
                {": "}
                {actionLabel(row.action)}
              </li>
            ))}
          </ul>
          {proposedArrivalComplete() ? (
            <p>
              {t("intakeProposedArrivalConfirm", {
                date: proposedArrival!.date,
                time: proposedArrival!.time,
              })}
            </p>
          ) : null}
          <p className="text-[length:var(--ecmp-font-helper-size)]">
            {t("confirmCaseDecisionsAutoClose")}
          </p>
        </div>
      </Modal>

      <DuplicateWarningPanel
        open={duplicateOpen}
        result={duplicateResult}
        busy={duplicateBusy || submitting}
        onClose={() => setDuplicateOpen(false)}
        onDecide={onDuplicateDecide}
      />
    </PageContainer>
  );
}
