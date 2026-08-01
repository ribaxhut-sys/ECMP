"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ChangeEvent,
  type FormEvent,
} from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  fetchBranches,
  fetchComplaint,
  updateComplaint,
  type Branch,
} from "@/lib/api";
import type { Complaint } from "@/lib/api/types";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardDescription,
  CardHeader,
  CardTitle,
  Empty,
  ErrorState,
  Input,
  PageContainer,
  PageHeader,
  Select,
  Skeleton,
  Textarea,
} from "@/shared/ui";
import {
  resolveApiErrorMessage,
  translateValidationErrors,
} from "@/shared/i18n/resolveApiErrorMessage";
import {
  CHANNEL_OPTIONS,
  PRIORITY_OPTIONS,
  formFromComplaint,
  toUpdateComplaintRequest,
  validateEditComplaintForm,
  type EditComplaintFieldErrors,
  type EditComplaintFormValues,
} from "./editComplaintForm";

export function EditComplaintView({ complaintId }: { complaintId: string }) {
  const router = useRouter();
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const tPriority = useTranslations("priority");
  const tValidation = useTranslations("validation");
  const tErrors = useTranslations("errors");
  const { hasPermission } = useAuth();
  const canUpdate = hasPermission("complaints:update") || hasPermission("*");

  const [complaint, setComplaint] = useState<Complaint | null>(null);
  const [values, setValues] = useState<EditComplaintFormValues | null>(null);
  const [errors, setErrors] = useState<EditComplaintFieldErrors>({});
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [branchesLoading, setBranchesLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setNotFound(false);
      setLoadError(null);
      try {
        const res = await fetchComplaint(complaintId);
        if (cancelled) return;
        setComplaint(res.data);
        setValues(formFromComplaint(res.data));
      } catch (err) {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 404) {
          setNotFound(true);
        } else {
          setLoadError(
            resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToLoadDetail"),
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [complaintId, t, tCommon, tErrors]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setBranchesLoading(true);
      try {
        const res = await fetchBranches(100);
        if (!cancelled) setBranches(res.data);
      } catch {
        if (!cancelled) setBranches([]);
      } finally {
        if (!cancelled) setBranchesLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const updateField = useCallback(
    <K extends keyof EditComplaintFormValues>(
      key: K,
      value: EditComplaintFormValues[K],
    ) => {
      setValues((prev) => (prev ? { ...prev, [key]: value } : prev));
      setErrors((prev) => {
        if (!prev[key]) return prev;
        const next = { ...prev };
        delete next[key];
        return next;
      });
    },
    [],
  );

  const priorityOptions = useMemo(
    () => PRIORITY_OPTIONS.map(({ value }) => ({ value, label: tPriority(value) })),
    [tPriority],
  );
  const channelOptions = useMemo(
    () =>
      CHANNEL_OPTIONS.map(({ value }) => ({
        value,
        label: t(`channel${value.charAt(0)}${value.slice(1).toLowerCase()}`),
      })),
    [t],
  );

  function onTextChange(
    key: keyof EditComplaintFormValues,
  ): (
    event: ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => void {
    return (event) => {
      updateField(
        key,
        event.target.value as EditComplaintFormValues[typeof key],
      );
    };
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (!values || !canUpdate) return;
    setSubmitError(null);

    const nextErrors = validateEditComplaintForm(values);
    setErrors(translateValidationErrors(nextErrors, tValidation));
    if (Object.keys(nextErrors).length > 0) {
      const firstKey = Object.keys(nextErrors)[0];
      const el = firstKey ? document.getElementById(firstKey) : null;
      el?.focus();
      return;
    }

    setSubmitting(true);
    try {
      const res = await updateComplaint(
        complaintId,
        toUpdateComplaintRequest(values),
      );
      router.push(`/complaints/${res.data.id}`);
    } catch (err) {
      setSubmitError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToUpdate"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <PageContainer className="space-y-6">
        <PageHeader
          title={t("editTitle")}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: t("title"), href: "/complaints" },
            { label: t("editTitle") },
          ]}
        />
        <Skeleton rows={8} />
      </PageContainer>
    );
  }

  if (notFound) {
    return (
      <PageContainer className="space-y-6">
        <PageHeader
          title={t("editTitle")}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: t("title"), href: "/complaints" },
            { label: t("editTitle") },
          ]}
        />
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

  if (loadError || !complaint || !values) {
    return (
      <PageContainer className="space-y-6">
        <PageHeader
          title={t("editTitle")}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: t("title"), href: "/complaints" },
            { label: t("editTitle") },
          ]}
        />
        <ErrorState
          title={t("couldNotLoadComplaint")}
          message={loadError ?? tCommon("unexpectedErrorDescription")}
          onRetry={() => router.push(`/complaints/${complaintId}`)}
        />
      </PageContainer>
    );
  }

  if (!canUpdate) {
    return (
      <PageContainer className="space-y-6">
        <PageHeader
          title={t("editTitle")}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: t("title"), href: "/complaints" },
            { label: complaint.complaintNumber, href: `/complaints/${complaint.id}` },
            { label: t("editTitle") },
          ]}
        />
        <Alert
          tone="warning"
          title={t("editNotPermittedTitle")}
          description={t("editNotPermittedDescription")}
        />
        <Button
          type="button"
          variant="outline"
          onClick={() => router.push(`/complaints/${complaint.id}`)}
        >
          {t("backToDetail")}
        </Button>
      </PageContainer>
    );
  }

  const branchOptions = branches.map((b) => ({
    value: b.id,
    label: b.name,
  }));

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title={t("editTitleWithNumber", { number: complaint.complaintNumber })}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title"), href: "/complaints" },
          { label: complaint.complaintNumber, href: `/complaints/${complaint.id}` },
          { label: t("editTitle") },
        ]}
        description={t("editComplaintDescription")}
      />

      <form
        noValidate
        onSubmit={(event) => void onSubmit(event)}
        aria-label={t("editFormAriaLabel")}
        className="space-y-6"
      >
        {submitError ? (
          <Alert
            tone="danger"
            title={t("couldNotUpdate")}
            description={submitError}
          />
        ) : null}

        <Card>
          <CardHeader>
            <CardTitle>{t("complaintInformation")}</CardTitle>
            <CardDescription>
              {t("editComplaintInformationDescription")}
            </CardDescription>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div className="md:col-span-2">
                <Input
                  name="subject"
                  id="subject"
                  label={t("subject")}
                  required
                  maxLength={200}
                  value={values.subject}
                  onChange={onTextChange("subject")}
                  error={errors.subject}
                />
              </div>
              <Select
                name="priority"
                id="priority"
                label={tCommon("priority")}
                required
                options={priorityOptions}
                value={values.priority}
                onChange={onTextChange("priority")}
                error={errors.priority}
              />
              <div className="md:col-span-2">
                <Textarea
                  name="description"
                  id="description"
                  label={t("description")}
                  required
                  rows={5}
                  maxLength={5000}
                  value={values.description}
                  onChange={onTextChange("description")}
                  error={errors.description}
                  hint={`${values.description.trim().length}/5000`}
                />
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t("locationAndClassification")}</CardTitle>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <Select
                name="branchId"
                id="branchId"
                label={t("branch")}
                placeholder={
                  branchesLoading ? t("loadingBranches") : t("selectBranchPlaceholder")
                }
                options={branchOptions}
                value={values.branchId}
                onChange={onTextChange("branchId")}
                error={errors.branchId}
                disabled={branchesLoading}
              />
              <Select
                name="channel"
                id="channel"
                label={t("channel")}
                placeholder={t("selectChannelOptional")}
                options={channelOptions}
                value={values.channel}
                onChange={onTextChange("channel")}
                error={errors.channel}
              />
              <Input
                name="category"
                id="category"
                label={t("category")}
                maxLength={64}
                value={values.category}
                onChange={onTextChange("category")}
                error={errors.category}
              />
            </div>
          </CardBody>
        </Card>

        <Alert
          tone="info"
          title={t("notEditableTitle")}
          description={t("notEditableDescription")}
        />

        <div className="flex flex-col-reverse gap-3 border-t border-ecmp-border pt-4 sm:flex-row sm:justify-end">
          <Button
            type="button"
            variant="outline"
            disabled={submitting}
            onClick={() => router.push(`/complaints/${complaint.id}`)}
          >
            {tCommon("cancel")}
          </Button>
          <Button type="submit" loading={submitting}>
            {submitting ? tCommon("saving") : t("saveChanges")}
          </Button>
        </div>
      </form>
    </PageContainer>
  );
}
