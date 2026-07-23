"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
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

const CATEGORY_OPTIONS: ReadonlyArray<{
  value: ResolutionCategory;
  label: string;
}> = [
  { value: "SOLVED", label: "Solved" },
  { value: "WORKAROUND", label: "Workaround" },
  { value: "DUPLICATE", label: "Duplicate" },
  { value: "INVALID_REQUEST", label: "Invalid Request" },
  { value: "USER_ERROR", label: "User Error" },
  { value: "THIRD_PARTY", label: "Third Party" },
];

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

function categoryLabel(value: ResolutionCategory): string {
  return (
    CATEGORY_OPTIONS.find((option) => option.value === value)?.label ??
    value.replaceAll("_", " ")
  );
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
  const canUpdate = hasPermission("complaints:update");

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
              : "Unable to load resolution.",
        );
      }
    } finally {
      setLoading(false);
    }
  }, [complaintId]);

  useEffect(() => {
    void load();
  }, [load, status]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitError(null);

    const nextErrors: typeof fieldErrors = {};
    if (!category) nextErrors.category = "Category is required.";
    if (!rootCause.trim()) nextErrors.rootCause = "Root cause is required.";
    if (!notes.trim()) nextErrors.notes = "Resolution notes are required.";
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
            : "Resolve failed.",
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
          <CardTitle>Resolution</CardTitle>
        </CardHeader>
        <CardBody className="space-y-4">
          {loading ? (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              Loading resolution…
            </p>
          ) : loadError ? (
            <Alert
              tone="danger"
              title="Could not load resolution"
              description={loadError}
              actionLabel="Retry"
              onAction={() => void load()}
            />
          ) : resolution ? (
            <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <DetailField
                label="Category"
                value={categoryLabel(resolution.resolutionCategory)}
              />
              <DetailField
                label="Resolved By"
                value={resolution.resolvedByName?.trim() || "—"}
              />
              <DetailField label="Root Cause" value={resolution.rootCause} />
              <DetailField
                label="Resolved At"
                value={formatWhen(resolution.resolvedAt)}
              />
              <div className="sm:col-span-2">
                <DetailField label="Notes" value={resolution.resolutionNotes} />
              </div>
            </dl>
          ) : showForm ? null : (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              No resolution recorded yet.
            </p>
          )}

          {showForm ? (
            <form className="space-y-4 border-t border-ecmp-border pt-4" onSubmit={onSubmit}>
              <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                Complete the resolution form to move this complaint to RESOLVED.
                Closing requires a resolution first.
              </p>
              {submitError ? (
                <Alert
                  tone="danger"
                  title="Resolve failed"
                  description={submitError}
                />
              ) : null}
              <Select
                label="Category"
                name="resolutionCategory"
                required
                placeholder="Select category"
                options={CATEGORY_OPTIONS}
                value={category}
                error={fieldErrors.category}
                onChange={(event) =>
                  setCategory(event.target.value as ResolutionCategory | "")
                }
              />
              <Input
                label="Root Cause"
                name="rootCause"
                required
                value={rootCause}
                error={fieldErrors.rootCause}
                onChange={(event) => setRootCause(event.target.value)}
              />
              <Textarea
                label="Resolution Notes"
                name="resolutionNotes"
                required
                rows={4}
                value={notes}
                error={fieldErrors.notes}
                onChange={(event) => setNotes(event.target.value)}
              />
              <div className="flex justify-end">
                <Button type="submit" variant="primary" disabled={submitting}>
                  {submitting ? "Resolving…" : "Resolve"}
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
        title="Complaint resolved"
        description="Status is now RESOLVED."
      />
    </>
  );
}
