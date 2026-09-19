"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  addCmCase,
  createCmCase,
  fetchCmBatch1Complaint,
  fetchCmCases,
  type CmBatch1ComplaintResponse,
} from "@/lib/api";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Input,
  PageContainer,
  PageHeader,
  Select,
  Skeleton,
} from "@/shared/ui";
import { KnowledgeMentionTextarea } from "./KnowledgeMentionTextarea";
import {
  CASE_PRIORITY_OPTIONS,
  emptyCreateCaseForm,
  mergeCreateCaseForm,
  toAddCaseRequest,
  toCreateCaseRequest,
  validateCreateCaseForm,
  type CreateCaseFormValues,
} from "@/features/cases/caseForms";
import { rememberCaseId, markCaseHandleClaimed } from "@/features/cases/caseSessionRegistry";
import { useToast } from "@/shared/providers";
import {
  isHqIntakeDisposition,
  isComplaintHandlingClosed,
} from "./penangananGroups";
import { MAX_CASES_PER_COMPLAINT } from "./addCaseToComplaint";

type BlockReason = "missing_id" | "closed" | "hq_waiting" | "max_cases" | "forbidden";

/**
 * Full-page Add Case onto an existing open Complaint (FR-002).
 * Does not create a new Aggregate — submit uses addCmCase / createCmCase only.
 */
export function AddCaseToComplaintView({
  complaintId,
}: {
  complaintId: string;
}) {
  const router = useRouter();
  const t = useTranslations("complaints");
  const tCases = useTranslations("cases");
  const tCommon = useTranslations("common");
  const tValidation = useTranslations("validation");
  const tErrors = useTranslations("errors");
  const { hasPermission, user } = useAuth();
  const { pushSuccess } = useToast();
  const canCreate = hasPermission("complaints:create");

  const id = complaintId.trim();
  const [loading, setLoading] = useState(Boolean(id));
  const [loadError, setLoadError] = useState<string | null>(null);
  const [complaint, setComplaint] = useState<CmBatch1ComplaintResponse | null>(
    null,
  );
  const [caseCount, setCaseCount] = useState(0);
  const [blockReason, setBlockReason] = useState<BlockReason | null>(
    id ? null : "missing_id",
  );
  const [values, setValues] = useState<CreateCaseFormValues>(emptyCreateCaseForm());
  const [fieldErrors, setFieldErrors] = useState<
    ReturnType<typeof validateCreateCaseForm>
  >({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    if (!id) {
      setBlockReason("missing_id");
      setLoading(false);
      return;
    }
    if (!canCreate) {
      setBlockReason("forbidden");
      setLoading(false);
      return;
    }
    setLoading(true);
    setLoadError(null);
    setBlockReason(null);
    try {
      const [complaintRes, casesRes] = await Promise.all([
        fetchCmBatch1Complaint(id),
        fetchCmCases({ complaintId: id, pageSize: 50 }),
      ]);
      const data = complaintRes.data;
      const rows = casesRes.data ?? [];
      setComplaint(data);
      setCaseCount(rows.length);

      if (
        isComplaintHandlingClosed({
          complaintStatus: data.status,
          intakeDisposition: data.intakeDisposition,
        })
      ) {
        setBlockReason("closed");
        return;
      }
      if (isHqIntakeDisposition(data.intakeDisposition)) {
        setBlockReason("hq_waiting");
        return;
      }
      if (rows.length >= MAX_CASES_PER_COMPLAINT) {
        setBlockReason("max_cases");
        return;
      }

      const destinationUnitId =
        data.owningUnitId?.trim() || user?.branchId?.trim() || "";
      setValues(
        mergeCreateCaseForm({
          caseType: data.category?.trim() || "GENERAL",
          category: data.category?.trim() || "",
          subject: data.subject?.trim() || "",
          description:
            data.intakeNarrative?.trim() ||
            data.description?.trim() ||
            data.subject?.trim() ||
            "",
          priority: data.priority?.trim() || "MEDIUM",
          destinationUnitId,
        }),
      );
    } catch (err) {
      setLoadError(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : t("unableToLoadDetail"),
      );
    } finally {
      setLoading(false);
    }
  }, [id, canCreate, user?.branchId, t, tErrors, tCommon]);

  useEffect(() => {
    void load();
  }, [load]);

  function setField<K extends keyof CreateCaseFormValues>(
    key: K,
    value: CreateCaseFormValues[K],
  ) {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  function goBackToComplaint() {
    if (id) {
      router.push(`/complaints/cm/${encodeURIComponent(id)}`);
      return;
    }
    router.push("/complaints");
  }

  async function submit() {
    if (!id || blockReason || submitting) return;
    const errors = validateCreateCaseForm(values);
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setSubmitting(true);
    setSubmitError(null);
    try {
      const idempotencyKey =
        typeof crypto !== "undefined" && crypto.randomUUID
          ? crypto.randomUUID()
          : undefined;
      const res =
        caseCount > 0
          ? await addCmCase(id, toAddCaseRequest(values), { idempotencyKey })
          : await createCmCase(toCreateCaseRequest(id, values), {
              idempotencyKey,
            });
      rememberCaseId(id, res.data.caseId);
      markCaseHandleClaimed(res.data.caseId);
      pushSuccess(
        tCommon("success"),
        t("penangananCreated", { number: res.data.caseNumber }),
      );
      router.push(`/complaints/cm/${encodeURIComponent(id)}`);
    } catch (err) {
      setSubmitError(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : tCases("unableToLoad"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  const statusLabel =
    complaint?.status === "CLOSED"
      ? t("statusClosed")
      : complaint?.status === "IN_PROGRESS"
        ? t("statusInProgress")
        : complaint?.status === "REGISTERED"
          ? t("registered")
          : (complaint?.status ?? "");

  const branchUnitLocked = Boolean(values.destinationUnitId.trim());
  const formEnabled = !loading && !loadError && !blockReason && canCreate;

  const blockDescription =
    blockReason === "missing_id"
      ? t("addCaseMissingId")
      : blockReason === "closed"
        ? t("addCaseBlockedClosed")
        : blockReason === "hq_waiting"
          ? t("addCaseBlockedHq")
          : blockReason === "max_cases"
            ? t("addCaseBlockedMax", { max: MAX_CASES_PER_COMPLAINT })
            : blockReason === "forbidden"
              ? t("createAccessRestrictedDescription")
              : null;

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("addCasePageTitle")}
        description={t("addCasePageDescription")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title"), href: "/complaints" },
          ...(id
            ? [
                {
                  label: complaint?.complaintNumber ?? id,
                  href: `/complaints/cm/${encodeURIComponent(id)}`,
                },
              ]
            : []),
          { label: t("penangananAddCase") },
        ]}
      />

      {loading ? <Skeleton rows={4} /> : null}

      {!loading && loadError ? (
        <Alert
          tone="danger"
          title={t("unableToLoadDetail")}
          description={loadError}
          actionLabel={tCommon("retry")}
          onAction={() => void load()}
        />
      ) : null}

      {!loading && blockDescription ? (
        <Alert
          tone={blockReason === "closed" ? "success" : "warning"}
          title={
            blockReason === "forbidden"
              ? t("createRestrictedTitle")
              : t("addCaseBlockedTitle")
          }
          description={blockDescription}
          actionLabel={
            id ? t("addCaseBackToComplaint") : t("createComplaint")
          }
          onAction={
            id ? goBackToComplaint : () => router.push("/complaints/new")
          }
        />
      ) : null}

      {formEnabled && complaint ? (
        <Card>
          <CardBody className="space-y-[var(--ecmp-panel-gap)]">
            <Alert
              tone="info"
              title={t("addCaseParentBannerTitle")}
              description={t("addCaseParentBannerDescription", {
                number: complaint.complaintNumber,
                status: statusLabel,
                count: caseCount,
                max: MAX_CASES_PER_COMPLAINT,
              })}
            />

            <dl className="grid gap-3 sm:grid-cols-2">
              <div className="space-y-1">
                <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("complaintNumber")}
                </dt>
                <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                  {complaint.complaintNumber}
                </dd>
              </div>
              <div className="space-y-1">
                <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("statusLabel")}
                </dt>
                <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                  {statusLabel}
                </dd>
              </div>
            </dl>

            {submitError ? (
              <Alert
                tone="danger"
                title={tCases("unableToLoad")}
                description={submitError}
              />
            ) : null}

            <Input
              name="caseType"
              label={tCases("caseType")}
              value={values.caseType}
              onChange={(e) => setField("caseType", e.target.value)}
              error={
                fieldErrors.caseType
                  ? tValidation(fieldErrors.caseType)
                  : undefined
              }
              required
              disabled={submitting}
            />
            <Input
              name="category"
              label={tCases("category")}
              value={values.category}
              onChange={(e) => setField("category", e.target.value)}
              disabled={submitting}
            />
            <Input
              name="subject"
              label={tCases("subject")}
              value={values.subject}
              onChange={(e) => setField("subject", e.target.value)}
              error={
                fieldErrors.subject
                  ? tValidation(fieldErrors.subject)
                  : undefined
              }
              required
              disabled={submitting}
            />
            <KnowledgeMentionTextarea
              name="description"
              label={tCases("description")}
              value={values.description}
              onChange={(next) => setField("description", next)}
              error={
                fieldErrors.description
                  ? tValidation(fieldErrors.description)
                  : undefined
              }
              required
              disabled={submitting}
            />
            <Select
              name="priority"
              label={tCases("priority")}
              value={values.priority}
              onChange={(e) => setField("priority", e.target.value)}
              options={CASE_PRIORITY_OPTIONS.map((option) => ({
                ...option,
                label: tCases(option.label),
              }))}
              error={
                fieldErrors.priority
                  ? tValidation(fieldErrors.priority)
                  : undefined
              }
              disabled={submitting}
            />
            {branchUnitLocked ? (
              <Alert
                tone="success"
                title={tCases("branchUnitAssignedTitle")}
                description={tCases("branchUnitAssignedDescription")}
              />
            ) : (
              <Input
                name="destinationUnitId"
                label={tCases("destinationUnitOptional")}
                value={values.destinationUnitId}
                onChange={(e) => setField("destinationUnitId", e.target.value)}
                hint={tCases("destinationUnitHint")}
                disabled={submitting}
              />
            )}

            <div className="flex flex-col-reverse gap-[var(--ecmp-form-gap)] border-t border-ecmp-border pt-[var(--ecmp-panel-gap)] sm:flex-row sm:justify-end">
              <Button
                type="button"
                variant="outline"
                onClick={goBackToComplaint}
                disabled={submitting}
              >
                {tCommon("cancel")}
              </Button>
              <Button
                type="button"
                onClick={() => void submit()}
                loading={submitting}
              >
                {t("penangananAddCase")}
              </Button>
            </div>
          </CardBody>
        </Card>
      ) : null}
    </PageContainer>
  );
}
