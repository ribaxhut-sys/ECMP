"use client";

import {
  useCallback,
  useEffect,
  useState,
  type FormEvent,
} from "react";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  fetchFinalResolution,
  submitFinalResolution,
} from "@/lib/api";
import type { FinalResolutionDetail } from "@/lib/api/types";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Textarea,
  Toast,
} from "@/shared/ui";

function formatWhen(value: string | null | undefined): string {
  if (!value) return "—";
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

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
          err instanceof ApiError
            ? err.message
            : "Unable to load final resolution.",
        );
      }
    } finally {
      setLoading(false);
    }
  }, [canRead, complaintId]);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!canSubmit || detail) return;

    const nextErrors: { summary?: string; notes?: string } = {};
    if (!summary.trim()) nextErrors.summary = "Summary is required.";
    if (!notes.trim()) nextErrors.notes = "Notes are required.";
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
        err instanceof ApiError
          ? err.message
          : "Unable to submit final resolution.",
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
      <Card>
        <CardHeader>
          <CardTitle>Final Resolution</CardTitle>
        </CardHeader>
        <CardBody className="space-y-4">
          {loading ? (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              Loading final resolution…
            </p>
          ) : loadError ? (
            <Alert tone="danger" title="Could not load final resolution">
              {loadError}
            </Alert>
          ) : detail ? (
            <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <DetailField label="Summary" value={detail.summary} />
              <DetailField
                label="Follow-up required"
                value={detail.followUpRequired ? "Yes" : "No"}
              />
              <DetailField label="Notes" value={detail.notes} />
              <DetailField
                label="Submitted by"
                value={detail.submittedByName?.trim() || "—"}
              />
              <DetailField
                label="Submitted at"
                value={formatWhen(detail.submittedAt)}
              />
              <DetailField label="Status" value={detail.status} />
            </dl>
          ) : canSubmit ? (
            <form className="space-y-4" onSubmit={onSubmit}>
              <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                Submit Final Resolution after the appointment is COMPLETED.
                Complaint stays IN_PROGRESS until later closure approval.
              </p>
              <div className="space-y-1">
                <label
                  htmlFor="final-resolution-summary"
                  className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary"
                >
                  Summary
                </label>
                <Textarea
                  id="final-resolution-summary"
                  name="summary"
                  rows={3}
                  value={summary}
                  onChange={(e) => setSummary(e.target.value)}
                  aria-invalid={Boolean(fieldErrors.summary)}
                />
                {fieldErrors.summary ? (
                  <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-danger">
                    {fieldErrors.summary}
                  </p>
                ) : null}
              </div>
              <div className="space-y-1">
                <label
                  htmlFor="final-resolution-notes"
                  className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary"
                >
                  Notes
                </label>
                <Textarea
                  id="final-resolution-notes"
                  name="notes"
                  rows={4}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  aria-invalid={Boolean(fieldErrors.notes)}
                />
                {fieldErrors.notes ? (
                  <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-danger">
                    {fieldErrors.notes}
                  </p>
                ) : null}
              </div>
              <label className="flex items-center gap-2 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                <input
                  type="checkbox"
                  checked={followUpRequired}
                  onChange={(e) => setFollowUpRequired(e.target.checked)}
                  className="size-4 accent-[var(--ecmp-color-primary)]"
                />
                Follow-up required
              </label>
              {submitError ? (
                <Alert tone="danger" title="Submit failed">
                  {submitError}
                </Alert>
              ) : null}
              <div className="flex justify-end">
                <Button type="submit" disabled={submitting}>
                  {submitting ? "Submitting…" : "Submit Final Resolution"}
                </Button>
              </div>
            </form>
          ) : (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              No final resolution submitted yet.
            </p>
          )}
        </CardBody>
      </Card>
      <Toast
        open={toastOpen}
        onClose={() => setToastOpen(false)}
        tone="success"
        title="Final resolution submitted"
        description="Complaint remains IN_PROGRESS. Escalation remains APPROVED."
      />
    </>
  );
}
