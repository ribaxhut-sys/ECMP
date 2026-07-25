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
  Input,
  PageContainer,
  PageHeader,
  Select,
  Skeleton,
  Textarea,
} from "@/shared/ui";
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
            err instanceof ApiError
              ? err.message
              : "Unable to load complaint.",
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [complaintId]);

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
    setErrors(nextErrors);
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
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Unable to update complaint.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <PageContainer className="space-y-6">
        <PageHeader
          title="Edit Complaint"
          breadcrumbs={[
            { label: "Home", href: "/dashboard" },
            { label: "Complaints", href: "/complaints" },
            { label: "Edit" },
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
          title="Edit Complaint"
          breadcrumbs={[
            { label: "Home", href: "/dashboard" },
            { label: "Complaints", href: "/complaints" },
            { label: "Edit" },
          ]}
        />
        <Empty
          title="404"
          description="Complaint not found."
          action={
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push("/complaints")}
            >
              Back to Complaint List
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
          title="Edit Complaint"
          breadcrumbs={[
            { label: "Home", href: "/dashboard" },
            { label: "Complaints", href: "/complaints" },
            { label: "Edit" },
          ]}
        />
        <Empty
          title="Could not load complaint"
          description={loadError ?? "Unexpected error."}
          action={
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push(`/complaints/${complaintId}`)}
            >
              Back to Detail
            </Button>
          }
        />
      </PageContainer>
    );
  }

  if (!canUpdate) {
    return (
      <PageContainer className="space-y-6">
        <PageHeader
          title="Edit Complaint"
          breadcrumbs={[
            { label: "Home", href: "/dashboard" },
            { label: "Complaints", href: "/complaints" },
            { label: complaint.complaintNumber, href: `/complaints/${complaint.id}` },
            { label: "Edit" },
          ]}
        />
        <Alert
          tone="warning"
          title="Edit not permitted"
          description="Your account does not have complaints:update permission."
        />
        <Button
          type="button"
          variant="outline"
          onClick={() => router.push(`/complaints/${complaint.id}`)}
        >
          Back to Detail
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
        title={`Edit ${complaint.complaintNumber}`}
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Complaints", href: "/complaints" },
          { label: complaint.complaintNumber, href: `/complaints/${complaint.id}` },
          { label: "Edit" },
        ]}
        description="Update mutable fields only. Status changes use dedicated workflow APIs."
      />

      <form
        noValidate
        onSubmit={(event) => void onSubmit(event)}
        aria-label="Edit complaint form"
        className="space-y-6"
      >
        {submitError ? (
          <Alert
            tone="danger"
            title="Could not update complaint"
            description={submitError}
          />
        ) : null}

        <Card>
          <CardHeader>
            <CardTitle>Complaint Information</CardTitle>
            <CardDescription>
              Subject, description, and priority (API-204).
            </CardDescription>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
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
                />
              </div>
              <Select
                name="priority"
                id="priority"
                label="Priority"
                required
                options={[...PRIORITY_OPTIONS]}
                value={values.priority}
                onChange={onTextChange("priority")}
                error={errors.priority}
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
                  hint={`${values.description.trim().length}/5000`}
                />
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Location & classification</CardTitle>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
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
                disabled={branchesLoading}
              />
              <Select
                name="channel"
                id="channel"
                label="Channel"
                placeholder="Select channel (optional)"
                options={[...CHANNEL_OPTIONS]}
                value={values.channel}
                onChange={onTextChange("channel")}
                error={errors.channel}
              />
              <Input
                name="category"
                id="category"
                label="Category"
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
          title="Not editable here"
          description="Customer, complaint number, and status are immutable on this screen. Use status / assignment workflows for lifecycle changes."
        />

        <div className="flex flex-col-reverse gap-3 border-t border-ecmp-border pt-4 sm:flex-row sm:justify-end">
          <Button
            type="button"
            variant="outline"
            disabled={submitting}
            onClick={() => router.push(`/complaints/${complaint.id}`)}
          >
            Cancel
          </Button>
          <Button type="submit" loading={submitting}>
            {submitting ? "Saving…" : "Save changes"}
          </Button>
        </div>
      </form>
    </PageContainer>
  );
}
