"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { useLocale, useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  fetchComplaintResolution,
  resolveComplaint,
} from "@/lib/api";
import type {
  ComplaintStatus,
  Resolution,
  ResolutionCategory,
} from "@/lib/api/types";
import { formatDateTime } from "@/i18n/formatting";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Input,
  Select,
  Textarea,
  Toast,
} from "@/shared/ui";

const CATEGORY_VALUES: readonly ResolutionCategory[] = [
  "SOLVED",
  "WORKAROUND",
  "DUPLICATE",
  "INVALID_REQUEST",
  "USER_ERROR",
  "THIRD_PARTY",
];

function DetailField({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 space-y-1">
      <dt className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary">
        {label}
      </dt>
      <dd className="whitespace-pre-wrap break-words text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
        {value}
      </dd>
    </div>
  );
}

export function ResolutionCard({
  complaintId,
  status,
  onResolved,
}: {
  complaintId: string;
  status: ComplaintStatus;
  onResolved?: () => void;
}) {
  const { hasPermission, userId } = useAuth();
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const tCategory = useTranslations("resolutionCategory");
  const locale = useLocale();
  const canUpdate = hasPermission("complaints:update");

  const categoryOptions = CATEGORY_VALUES.map((value) => ({
    value,
    label: tCategory(value),
  }));

  const [resolution, setResolution] = useState<Resolution | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [category, setCategory] = useState<ResolutionCategory | "">("");
  const [rootCause, setRootCause] = useState("");
  const [notes, setNotes] = useState("");
  const [fieldErrors, setFieldErrors] = useState<{
    category?: string;
    rootCause?: string;
    notes?: string;
  }>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [toastOpen, setToastOpen] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const res = await fetchComplaintResolution(complaintId);
      setResolution(res.data);
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setResolution(null);
      } else {
        setResolution(null);
        setLoadError(
          err instanceof ApiError
            ? err.message
            : err instanceof Error
              ? err.message
              : t("unableToLoadResolution"),
        );
      }
    } finally {
      setLoading(false);
    }
  }, [complaintId, t]);

  useEffect(() => {
    void load();
  }, [load, status]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitError(null);

    const nextErrors: typeof fieldErrors = {};
    if (!category) nextErrors.category = t("categoryRequired");
    if (!rootCause.trim()) nextErrors.rootCause = t("rootCauseRequired");
    if (!notes.trim()) nextErrors.notes = t("resolutionNotesRequired");
    setFieldErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    setSubmitting(true);
    try {
      const res = await resolveComplaint(complaintId, {
        resolutionCategory: category as ResolutionCategory,
        rootCause: rootCause.trim(),
        resolutionNotes: notes.trim(),
        resolvedBy: userId ?? undefined,
      });
      setResolution(res.data.resolution);
      setCategory("");
      setRootCause("");
      setNotes("");
      setToastOpen(true);
      onResolved?.();
    } catch (err) {
      setSubmitError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : t("resolveFailed"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  const showForm = canUpdate && status === "IN_PROGRESS";

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>{t("resolutionCard")}</CardTitle>
        </CardHeader>
        <CardBody className="space-y-4">
          {loading ? (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              {t("loadingResolution")}
            </p>
          ) : loadError ? (
            <Alert
              tone="danger"
              title={t("couldNotLoadResolution")}
              description={loadError}
              actionLabel={tCommon("retry")}
              onAction={() => void load()}
            />
          ) : resolution ? (
            <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <DetailField
                label={t("category")}
                value={tCategory(resolution.resolutionCategory)}
              />
              <DetailField
                label={t("resolvedBy")}
                value={resolution.resolvedByName?.trim() || tCommon("emDash")}
              />
              <DetailField label={t("rootCause")} value={resolution.rootCause} />
              <DetailField
                label={t("resolvedAt")}
                value={formatDateTime(resolution.resolvedAt, locale)}
              />
              <div className="sm:col-span-2">
                <DetailField
                  label={t("resolutionNotes")}
                  value={resolution.resolutionNotes}
                />
              </div>
            </dl>
          ) : showForm ? null : (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              {t("noResolutionYet")}
            </p>
          )}

          {showForm ? (
            <form className="space-y-4 border-t border-ecmp-border pt-4" onSubmit={onSubmit}>
              <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                {t("resolutionFormHint")}
              </p>
              {submitError ? (
                <Alert
                  tone="danger"
                  title={t("resolveFailed")}
                  description={submitError}
                />
              ) : null}
              <Select
                label={t("category")}
                name="resolutionCategory"
                required
                placeholder={t("selectCategoryPlaceholder")}
                options={categoryOptions}
                value={category}
                error={fieldErrors.category}
                onChange={(event) =>
                  setCategory(event.target.value as ResolutionCategory | "")
                }
              />
              <Input
                label={t("rootCause")}
                name="rootCause"
                required
                value={rootCause}
                error={fieldErrors.rootCause}
                onChange={(event) => setRootCause(event.target.value)}
              />
              <Textarea
                label={t("resolutionNotes")}
                name="resolutionNotes"
                required
                rows={4}
                value={notes}
                error={fieldErrors.notes}
                onChange={(event) => setNotes(event.target.value)}
              />
              <div className="flex justify-end">
                <Button type="submit" variant="primary" disabled={submitting}>
                  {submitting ? t("resolving") : t("recordResolution")}
                </Button>
              </div>
            </form>
          ) : null}
        </CardBody>
      </Card>
      <Toast
        open={toastOpen}
        onClose={() => setToastOpen(false)}
        tone="success"
        title={t("complaintResolved")}
        description={t("statusNowResolved")}
      />
    </>
  );
}
