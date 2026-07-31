"use client";

import {
  useCallback,
  useEffect,
  useState,
  type ChangeEvent,
  type FormEvent,
} from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  checkCmBatch1Duplicates,
  createCmBatch1Complaint,
  fetchBranches,
  recordCmBatch1DuplicateDecision,
  type Branch,
  type CmBatch1DuplicateCheckResponse,
} from "@/lib/api";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardDescription,
  CardHeader,
  CardTitle,
  Empty,
  Input,
  PageContainer,
  PageHeader,
  Select,
  Textarea,
} from "@/shared/ui";
import { CustomerSearchPanel } from "./CustomerSearchPanel";
import { DuplicateWarningPanel } from "./DuplicateWarningPanel";
import { StagingAttachmentsPanel } from "./StagingAttachmentsPanel";
import {
  CHANNEL_OPTIONS,
  createEmptyComplaintForm,
  newCmBatch1IdempotencyKey,
  newCmBatch1StagingToken,
  PRIORITY_OPTIONS,
  toCmBatch1CreateRequest,
  validateCmBatch1CreateForm,
  type CreateComplaintFieldErrors,
  type CreateComplaintFormValues,
} from "./createComplaintForm";

/**
 * Create Complaint — Mode A Batch-1 Aggregate intake (API-500).
 * Dual SoT (DEC-020): posts to `/api/v1/cm/complaints`, not foundation.
 * Confirmation lands on `/complaints/cm/[id]` (Aggregate read path).
 */
export function CreateComplaintView() {
  const router = useRouter();
  const { user, hasPermission } = useAuth();
  const canCreate = hasPermission("complaints:create");
  const agentBranchId = user?.branchId ?? null;

  const [values, setValues] = useState<CreateComplaintFormValues>(() =>
    createEmptyComplaintForm({ branchId: agentBranchId }),
  );
  const [errors, setErrors] = useState<CreateComplaintFieldErrors>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [infoMessage, setInfoMessage] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [branchesLoading, setBranchesLoading] = useState(true);
  const [branchesError, setBranchesError] = useState<string | null>(null);

  const [duplicateOpen, setDuplicateOpen] = useState(false);
  const [duplicateResult, setDuplicateResult] =
    useState<CmBatch1DuplicateCheckResponse | null>(null);
  const [duplicateBusy, setDuplicateBusy] = useState(false);
  const [overrideJustification, setOverrideJustification] = useState<
    string | null
  >(null);
  const [stagingToken, setStagingToken] = useState(() =>
    newCmBatch1StagingToken(),
  );

  useEffect(() => {
    if (!canCreate) {
      setBranchesLoading(false);
      return;
    }
    let cancelled = false;
    (async () => {
      setBranchesLoading(true);
      setBranchesError(null);
      try {
        const res = await fetchBranches(100);
        if (!cancelled) {
          setBranches(res.data);
          if (agentBranchId) {
            const match = res.data.find((b) => b.id === agentBranchId);
            if (match) {
              setValues((prev) =>
                prev.branchId ? prev : { ...prev, branchId: match.id },
              );
            }
          }
        }
      } catch (err) {
        if (!cancelled) {
          setBranchesError(
            err instanceof ApiError
              ? err.message
              : "Unable to load branches.",
          );
        }
      } finally {
        if (!cancelled) setBranchesLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [agentBranchId, canCreate]);

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
      setDuplicateResult(null);
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
    setOverrideJustification(null);
    setDuplicateResult(null);
  }, []);

  if (!canCreate) {
    return (
      <PageContainer className="space-y-6">
        <PageHeader
          title="Create Complaint"
          breadcrumbs={[
            { label: "Home", href: "/dashboard" },
            { label: "Complaints", href: "/complaints" },
            { label: "Create" },
          ]}
        />
        <Empty
          title="Access restricted"
          description="You need the complaints:create permission to register a complaint."
          action={
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push("/complaints")}
            >
              Back to Complaints
            </Button>
          }
        />
      </PageContainer>
    );
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
    router.push("/complaints");
  }

  async function createAggregate(
    justification: string | null,
  ): Promise<void> {
    const response = await createCmBatch1Complaint(
      toCmBatch1CreateRequest(values, {
        duplicateOverrideJustification: justification,
        stagingToken,
      }),
      { idempotencyKey: newCmBatch1IdempotencyKey() },
    );
    router.push(`/complaints/cm/${response.data.complaintId}`);
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setSubmitError(null);
    setInfoMessage(null);

    const nextErrors = validateCmBatch1CreateForm(values);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) {
      const firstKey = Object.keys(nextErrors)[0];
      const el = firstKey ? document.getElementById(firstKey) : null;
      el?.focus();
      return;
    }

    setSubmitting(true);
    try {
      if (overrideJustification) {
        await createAggregate(overrideJustification);
        return;
      }

      const dup = await checkCmBatch1Duplicates({
        customerId: values.customerId.trim(),
        category: values.category.trim(),
        subject: values.subject.trim(),
        channel: values.channel.trim(),
      });
      setDuplicateResult(dup.data);

      if (dup.data.warning) {
        setDuplicateOpen(true);
        return;
      }

      await createAggregate(null);
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Unable to create complaint.";
      setSubmitError(message);
    } finally {
      setSubmitting(false);
    }
  }

  async function onDuplicateDecide(payload: {
    decision: "link_existing" | "override" | "recommend_only" | "blocked";
    survivingComplaintId?: string;
    justification?: string;
  }): Promise<void> {
    setDuplicateBusy(true);
    setSubmitError(null);
    try {
      if (payload.decision === "recommend_only") {
        await recordCmBatch1DuplicateDecision({
          decision: "recommend_only",
          customerId: values.customerId.trim(),
          survivingComplaintId: payload.survivingComplaintId,
        });
        setDuplicateOpen(false);
        setInfoMessage(
          "Recommendation recorded: continue on the existing complaint. Case create is Batch 2 — not available here.",
        );
        return;
      }

      if (payload.decision === "link_existing") {
        const surviving = payload.survivingComplaintId?.trim();
        if (!surviving) {
          setSubmitError("Surviving complaint ID is required to link.");
          return;
        }
        await recordCmBatch1DuplicateDecision({
          decision: "link_existing",
          customerId: values.customerId.trim(),
          survivingComplaintId: surviving,
          stagingToken,
        });
        setDuplicateOpen(false);
        router.push(`/complaints/cm/${surviving}`);
        return;
      }

      if (payload.decision === "override") {
        const justification = payload.justification?.trim() ?? "";
        // Create path (API-500) records override + audit when justification is present.
        setOverrideJustification(justification);
        setDuplicateOpen(false);
        setSubmitting(true);
        try {
          await createAggregate(justification);
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
        setSubmitError("Create is blocked by duplicate policy.");
      }
    } catch (err) {
      setSubmitError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Unable to record duplicate decision.",
      );
    } finally {
      setDuplicateBusy(false);
    }
  }

  const branchOptions = branches.map((b) => ({
    value: b.id,
    label: b.name,
  }));

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title="Create Complaint"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Complaints", href: "/complaints" },
          { label: "Create" },
        ]}
        description="Batch-1 Aggregate intake (/api/v1/cm): search & confirm customer, duplicate check, then register. Dual SoT — not listed on foundation /api/v1/complaints."
      />

      <form
        noValidate
        onSubmit={(event) => void onSubmit(event)}
        aria-label="Create complaint form"
        className="space-y-6"
      >
        {submitError ? (
          <Alert
            tone="danger"
            title="Could not create complaint"
            description={submitError}
          />
        ) : null}

        {infoMessage ? (
          <Alert tone="info" title="Notice" description={infoMessage} />
        ) : null}

        {branchesError ? (
          <Alert
            tone="danger"
            title="Could not load branches"
            description={branchesError}
          />
        ) : null}

        <CustomerSearchPanel
          confirmedCustomerId={values.customerId}
          confirmedDisplayName={values.customerName}
          onConfirmed={onCustomerConfirmed}
          onCleared={onCustomerCleared}
          disabled={submitting}
        />

        {(errors.customerId || errors.customerName) && !values.customerId ? (
          <Alert
            tone="danger"
            title="Customer required"
            description={
              errors.customerId ||
              errors.customerName ||
              "Confirm a customer before creating."
            }
          />
        ) : null}

        <Card>
          <CardHeader>
            <CardTitle id="section-complaint-info">
              Complaint Information
            </CardTitle>
            <CardDescription>
              Subject, narrative, category, and channel (API-500 required
              fields).
            </CardDescription>
          </CardHeader>
          <CardBody>
            <fieldset
              aria-labelledby="section-complaint-info"
              className="grid grid-cols-1 gap-4 md:grid-cols-2"
            >
              <legend className="sr-only">Complaint Information</legend>
              <div className="md:col-span-2">
                <Input
                  name="subject"
                  id="subject"
                  label="Subject"
                  required
                  maxLength={200}
                  value={values.subject}
                  onChange={onTextChange("subject")}
                  error={errors.subject}
                  aria-required="true"
                  autoComplete="off"
                />
              </div>
              <Select
                name="priority"
                id="priority"
                label="Priority"
                placeholder="Select priority (optional)"
                options={PRIORITY_OPTIONS}
                value={values.priority}
                onChange={onTextChange("priority")}
                error={errors.priority}
              />
              <Select
                name="channel"
                id="channel"
                label="Channel"
                required
                placeholder="Select channel"
                options={CHANNEL_OPTIONS}
                value={values.channel}
                onChange={onTextChange("channel")}
                error={errors.channel}
                aria-required="true"
              />
              <Input
                name="category"
                id="category"
                label="Category"
                required
                maxLength={64}
                value={values.category}
                onChange={onTextChange("category")}
                error={errors.category}
                aria-required="true"
                autoComplete="off"
              />
              <div className="md:col-span-2">
                <Textarea
                  name="description"
                  id="description"
                  label="Description"
                  required
                  rows={5}
                  maxLength={5000}
                  value={values.description}
                  onChange={onTextChange("description")}
                  error={errors.description}
                  aria-required="true"
                  hint={`${values.description.trim().length}/5000`}
                />
              </div>
            </fieldset>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle id="section-location">Recording unit</CardTitle>
            <CardDescription>
              Optional recording unit (branch) mapped to Aggregate
              recordingUnitId.
            </CardDescription>
          </CardHeader>
          <CardBody>
            <fieldset
              aria-labelledby="section-location"
              className="grid grid-cols-1 gap-4 md:grid-cols-2"
            >
              <legend className="sr-only">Recording unit</legend>
              <Select
                name="branchId"
                id="branchId"
                label="Branch"
                placeholder={
                  branchesLoading ? "Loading branches…" : "Select branch"
                }
                options={branchOptions}
                value={values.branchId}
                onChange={onTextChange("branchId")}
                error={errors.branchId}
                disabled={branchesLoading || branchOptions.length === 0}
                hint={
                  branchOptions.length === 0 && !branchesLoading
                    ? "No active branches available"
                    : "Optional — Mode A lab branches"
                }
              />
            </fieldset>
          </CardBody>
        </Card>

        {overrideJustification ? (
          <Alert
            tone="warning"
            title="Duplicate override armed"
            description="Create will proceed with the recorded override justification."
          />
        ) : null}

        <StagingAttachmentsPanel
          stagingToken={stagingToken}
          disabled={submitting || duplicateBusy}
          onStagingTokenResolved={setStagingToken}
        />

        <div className="flex flex-col-reverse gap-3 border-t border-ecmp-border pt-4 sm:flex-row sm:justify-end">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={submitting || duplicateBusy}
            aria-label="Cancel and return to complaints"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            loading={submitting}
            disabled={duplicateBusy}
            aria-label="Create complaint"
          >
            {submitting ? "Creating…" : "Create Complaint"}
          </Button>
        </div>
      </form>

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
