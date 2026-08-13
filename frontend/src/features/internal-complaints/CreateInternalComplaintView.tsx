"use client";

import { useEffect, useMemo, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Empty,
  Input,
  PageContainer,
  PageHeader,
  Select,
  SectionHeader,
  Textarea,
  Toast,
  type SelectOption,
} from "@/shared/ui";
import { fetchBranches, type Branch } from "@/lib/api/branches";
import { fetchCmBatch1Complaints } from "@/lib/api/cmBatch1";
import {
  createInternalComplaint,
} from "@/lib/api/internalComplaints";
import {
  defaultInternalComplaintForm,
  isInternalComplaintFormValid,
  validateInternalComplaintForm,
  type InternalComplaintFormValues,
} from "./internalComplaintForm";
import {
  CATEGORY_LABEL_KEY,
  INTERNAL_CATEGORIES,
  INTERNAL_PRIORITIES,
  isInternalAgentFamily,
} from "./types";
import {
  filterTransferDestinations,
  formatUnitOptionLabel,
} from "./transferDirection";

const RELATED_DATALIST_ID = "internal-related-complaint-numbers";

export function CreateInternalComplaintView() {
  const router = useRouter();
  const t = useTranslations("internalComplaints");
  const tCommon = useTranslations("common");
  const tPriority = useTranslations("priority");
  const { user, userId, roles, hasPermission } = useAuth();
  const canCreate = hasPermission("complaints:create");

  const [values, setValues] = useState<InternalComplaintFormValues>(() =>
    defaultInternalComplaintForm(),
  );
  const [errors, setErrors] = useState<
    ReturnType<typeof validateInternalComplaintForm>
  >({});
  const [branches, setBranches] = useState<Branch[]>([]);
  const [relatedSuggestions, setRelatedSuggestions] = useState<
    { id: string; number: string }[]
  >([]);
  const [saving, setSaving] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [toastOpen, setToastOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState("");

  useEffect(() => {
    fetchBranches(100)
      .then((res) => setBranches(res.data ?? []))
      .catch(() => setBranches([]));
  }, []);

  useEffect(() => {
    const agentOnly = isInternalAgentFamily(roles);
    const filters: {
      status: string;
      pageSize: number;
      createdBy?: string;
    } = { status: "REGISTERED", pageSize: 20 };
    if (agentOnly && userId) {
      filters.createdBy = userId;
    }
    fetchCmBatch1Complaints(filters)
      .then((res) => {
        setRelatedSuggestions(
          (res.data ?? []).map((row) => ({
            id: row.complaintId,
            number: row.complaintNumber,
          })),
        );
      })
      .catch(() => setRelatedSuggestions([]));
  }, [roles, userId]);

  function setField<K extends keyof InternalComplaintFormValues>(
    key: K,
    value: InternalComplaintFormValues[K],
  ): void {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  const categoryOptions: SelectOption[] = INTERNAL_CATEGORIES.map((category) => ({
    value: category,
    label: t(CATEGORY_LABEL_KEY[category]),
  }));
  const priorityOptions: SelectOption[] = INTERNAL_PRIORITIES.map((priority) => ({
    value: priority,
    label: tPriority(priority),
  }));
  const actorUnitCode = useMemo(() => {
    const branchId = user?.branchId;
    if (!branchId) return null;
    return branches.find((b) => b.id === branchId)?.code ?? null;
  }, [branches, user?.branchId]);

  const transferDestinations = useMemo(
    () => filterTransferDestinations(branches, actorUnitCode),
    [branches, actorUnitCode],
  );

  const unitOptions: SelectOption[] = [
    { value: "", label: t("keepAtOwnerUnit") },
    ...transferDestinations.map((b) => ({
      value: b.code,
      label: formatUnitOptionLabel(b.code, b.name),
    })),
  ];

  /** Resolve typed number to Aggregate id when it matches a suggestion. */
  function resolveRelatedPayload(): string | null {
    const raw = values.relatedComplaintId.trim();
    if (!raw) return null;
    const hit = relatedSuggestions.find(
      (row) =>
        row.number.toUpperCase() === raw.toUpperCase() || row.id === raw,
    );
    return hit?.id ?? raw;
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    const fieldErrors = validateInternalComplaintForm(values);
    setErrors(fieldErrors);
    if (!isInternalComplaintFormValid(fieldErrors)) return;

    setSaving(true);
    setSubmitError(null);
    try {
      const dest = values.destinationUnitId.trim();
      const created = await createInternalComplaint({
        subject: values.title.trim(),
        description: values.description.trim(),
        category: values.category || "OTHER",
        priority: values.priority,
        chronology: values.chronology.trim() || null,
        impact: values.impact.trim() || null,
        relatedComplaintId: resolveRelatedPayload(),
        handlingUnitId: dest || null,
      });
      const id = created.data.complaintId;
      setToastMessage(t("submitted"));
      setToastOpen(true);
      router.push(`/internal/complaints/${encodeURIComponent(id)}`);
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : t("submitFailed"));
    } finally {
      setSaving(false);
    }
  }

  if (!canCreate) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader
          title={t("createTitle")}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: t("title"), href: "/internal" },
            { label: t("create") },
          ]}
        />
        <Empty
          title={tCommon("accessRestricted")}
          description={t("createAccessRestrictedDescription")}
          primaryAction={{
            label: tCommon("goHome"),
            onClick: () => router.push("/dashboard"),
          }}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <div className="mx-auto w-full max-w-4xl space-y-[var(--ecmp-section-gap)]">
        <PageHeader
          className="text-center md:flex-col md:items-center [&_ol]:justify-center [&_h1+div]:mx-auto"
          title={t("createTitle")}
          description={t("createDescription")}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: t("title"), href: "/internal" },
            { label: t("listTitle"), href: "/internal/complaints" },
            { label: t("createTitle") },
          ]}
        />

        {submitError ? <Alert tone="danger" title={submitError} /> : null}

        <Card className="w-full">
          <CardBody>
            <form className="space-y-6" onSubmit={onSubmit}>
              <SectionHeader title={t("sectionBasics")} />
              <Input
                label={t("titleField")}
                value={values.title}
                onChange={(e) => setField("title", e.target.value)}
                error={errors.title ? t(errors.title) : undefined}
                required
              />
              <div className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-2">
                <Select
                  label={t("category")}
                  options={categoryOptions}
                  value={values.category}
                  onChange={(e) =>
                    setField(
                      "category",
                      e.target.value as InternalComplaintFormValues["category"],
                    )
                  }
                  error={errors.category ? t(errors.category) : undefined}
                  required
                />
                <Select
                  label={t("priority")}
                  options={priorityOptions}
                  value={values.priority}
                  onChange={(e) =>
                    setField(
                      "priority",
                      e.target.value as InternalComplaintFormValues["priority"],
                    )
                  }
                />
              </div>
              <Input
                label={t("relatedComplaint")}
                value={values.relatedComplaintId}
                onChange={(e) => setField("relatedComplaintId", e.target.value)}
                hint={t("relatedComplaintHint")}
                list={RELATED_DATALIST_ID}
                placeholder={t("relatedComplaintPlaceholder")}
                autoComplete="off"
              />
              <datalist id={RELATED_DATALIST_ID}>
                {relatedSuggestions.map((row) => (
                  <option key={row.id} value={row.number} />
                ))}
              </datalist>
              <Select
                label={t("initialTransferUnit")}
                options={unitOptions}
                value={values.destinationUnitId}
                onChange={(e) => setField("destinationUnitId", e.target.value)}
                hint={t("initialTransferHint")}
              />

              <SectionHeader title={t("sectionNarrative")} />
              <Textarea
                label={t("description")}
                value={values.description}
                onChange={(e) => setField("description", e.target.value)}
                error={errors.description ? t(errors.description) : undefined}
                required
              />
              <Textarea
                label={t("chronology")}
                value={values.chronology}
                onChange={(e) => setField("chronology", e.target.value)}
              />
              <Textarea
                label={t("impact")}
                value={values.impact}
                onChange={(e) => setField("impact", e.target.value)}
              />

              <div className="flex flex-wrap justify-center gap-3">
                <Button type="submit" disabled={saving}>
                  {saving ? tCommon("loading") : t("submit")}
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => router.push("/internal/complaints")}
                >
                  {tCommon("cancel")}
                </Button>
              </div>
            </form>
          </CardBody>
        </Card>
      </div>

      <Toast
        open={toastOpen}
        onClose={() => setToastOpen(false)}
        title={toastMessage}
        tone="success"
      />
    </PageContainer>
  );
}
