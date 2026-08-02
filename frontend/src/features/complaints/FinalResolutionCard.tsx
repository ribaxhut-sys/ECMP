"use client";

import {
  useCallback,
  useEffect,
  useState,
  type FormEvent,
} from "react";
import { useLocale, useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  fetchFinalResolution,
  submitFinalResolution,
} from "@/lib/api";
import type { FinalResolutionDetail } from "@/lib/api/types";
import { formatDateTime } from "@/i18n/formatting";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Checkbox,
  Empty,
  SectionHeader,
  Skeleton,
  Textarea,
  Toast,
} from "@/shared/ui";

function DetailField({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 space-y-1">
      <dt className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
        {label}
      </dt>
      <dd className="whitespace-pre-wrap break-words text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
        {value}
      </dd>
    </div>
  );
}

export function FinalResolutionCard({
  complaintId,
  refreshKey = 0,
  onSubmitted,
}: {
  complaintId: string;
  refreshKey?: number;
  onSubmitted?: () => void;
}) {
  const { hasPermission } = useAuth();
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const locale = useLocale();
  const canSubmit = hasPermission("appointments:complete");
  const canRead = hasPermission("complaints:read");

  const [detail, setDetail] = useState<FinalResolutionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [summary, setSummary] = useState("");
  const [notes, setNotes] = useState("");
  const [followUpRequired, setFollowUpRequired] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<{
    summary?: string;
    notes?: string;
  }>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [toastOpen, setToastOpen] = useState(false);

  const load = useCallback(async () => {
    if (!canRead) {
      setLoading(false);
      setDetail(null);
      setLoadError(null);
      return;
    }
    setLoading(true);
    setLoadError(null);
    try {
      const res = await fetchFinalResolution(complaintId);
      setDetail(res.data);
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setDetail(null);
      } else {
        setDetail(null);
        setLoadError(
          err instanceof ApiError ? err.message : t("unableToLoadFinalResolution"),
        );
      }
    } finally {
      setLoading(false);
    }
  }, [canRead, complaintId, t]);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!canSubmit || detail) return;

    const nextErrors: { summary?: string; notes?: string } = {};
    if (!summary.trim()) nextErrors.summary = t("summaryRequired");
    if (!notes.trim()) nextErrors.notes = t("notesRequired");
    setFieldErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    setSubmitting(true);
    setSubmitError(null);
    try {
      await submitFinalResolution(complaintId, {
        summary: summary.trim(),
        notes: notes.trim(),
        followUpRequired,
      });
      setToastOpen(true);
      await load();
      onSubmitted?.();
    } catch (err) {
      setSubmitError(
        err instanceof ApiError ? err.message : t("unableToSubmitFinalResolution"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (!canRead) {
    return null;
  }

  return (
    <>
      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader title={t("finalResolutionCard")} />
        <Card>
          <CardBody className="space-y-[var(--ecmp-panel-gap)]">
            {loading ? (
              <Skeleton rows={4} />
            ) : loadError ? (
              <Alert
                tone="danger"
                title={t("couldNotLoadFinalResolution")}
                description={loadError}
              />
            ) : detail ? (
              <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-2">
                <DetailField label={t("summary")} value={detail.summary} />
                <DetailField
                  label={t("followUpRequired")}
                  value={detail.followUpRequired ? tCommon("yes") : tCommon("no")}
                />
                <DetailField label={t("notes")} value={detail.notes} />
                <DetailField
                  label={t("submittedBy")}
                  value={detail.submittedByName?.trim() || tCommon("emDash")}
                />
                <DetailField
                  label={t("submittedAt")}
                  value={formatDateTime(detail.submittedAt, locale)}
                />
                <DetailField label={t("status")} value={detail.status} />
              </dl>
            ) : canSubmit ? (
              <form
                className="space-y-[var(--ecmp-form-gap)]"
                onSubmit={onSubmit}
              >
                <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                  {t("submitFinalResolutionHint")}
                </p>
                <Textarea
                  id="final-resolution-summary"
                  name="summary"
                  label={t("summary")}
                  rows={3}
                  value={summary}
                  onChange={(e) => setSummary(e.target.value)}
                  error={fieldErrors.summary}
                />
                <Textarea
                  id="final-resolution-notes"
                  name="notes"
                  label={t("notes")}
                  rows={4}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  error={fieldErrors.notes}
                />
                <Checkbox
                  name="followUpRequired"
                  label={t("followUpRequired")}
                  checked={followUpRequired}
                  onChange={(e) => setFollowUpRequired(e.target.checked)}
                />
                {submitError ? (
                  <Alert
                    tone="danger"
                    title={t("submitFailed")}
                    description={submitError}
                  />
                ) : null}
                <div className="flex justify-end">
                  <Button type="submit" loading={submitting}>
                    {submitting
                      ? tCommon("submitting")
                      : t("submitFinalResolution")}
                  </Button>
                </div>
              </form>
            ) : (
              <Empty
                title={t("noFinalResolutionYet")}
                description={t("submitFinalResolutionHint")}
              />
            )}
          </CardBody>
        </Card>
      </section>
      <Toast
        open={toastOpen}
        onClose={() => setToastOpen(false)}
        tone="success"
        title={t("finalResolutionSubmitted")}
        description={t("finalResolutionSubmittedHint")}
      />
    </>
  );
}
