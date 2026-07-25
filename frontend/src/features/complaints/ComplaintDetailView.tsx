"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  fetchBranches,
  fetchComplaint,
  fetchComplaintResolution,
  fetchCustomers,
  type Branch,
  type Customer,
} from "@/lib/api";
import type { Complaint, ComplaintStatus, Priority } from "@/lib/api/types";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Empty,
  PageContainer,
  PageHeader,
  Skeleton,
  type BadgeTone,
} from "@/shared/ui";
import { AssignmentCard } from "./AssignmentCard";
import { AppointmentCard } from "./AppointmentCard";
import { CloseComplaintCard } from "./CloseComplaintCard";
import { CloseEscalationCard } from "./CloseEscalationCard";
import { ComplaintAttachmentsCard } from "./ComplaintAttachmentsCard";
import { EscalationCard } from "./EscalationCard";
import { FinalResolutionCard } from "./FinalResolutionCard";
import { ResolutionCard } from "./ResolutionCard";
import { SlaCard } from "./SlaCard";
import { StatusActionsCard } from "./StatusActionsCard";
import { TimelineCard } from "./TimelineCard";

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

function statusTone(status: ComplaintStatus): BadgeTone {
  switch (status) {
    case "RESOLVED":
      return "success";
    case "CLOSED":
      return "neutral";
    case "ESCALATED":
      return "danger";
    case "PENDING":
      return "warning";
    case "IN_PROGRESS":
      return "warning";
    case "ASSIGNED":
      return "primary";
    default:
      return "info";
  }
}

function priorityTone(priority: Priority): BadgeTone {
  switch (priority) {
    case "CRITICAL":
      return "danger";
    case "HIGH":
      return "warning";
    case "MEDIUM":
      return "info";
    default:
      return "neutral";
  }
}

function DetailField({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
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

export function ComplaintDetailView({ complaintId }: { complaintId: string }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { hasPermission } = useAuth();
  const canUpdate = hasPermission("complaints:update");
  const failedAttachmentCount = Number(
    searchParams.get("attachmentUploadFailed") ?? "0",
  );
  const [complaint, setComplaint] = useState<Complaint | null>(null);
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [branch, setBranch] = useState<Branch | null>(null);
  const [hasResolution, setHasResolution] = useState(false);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [timelineKey, setTimelineKey] = useState(0);

  const load = useCallback(async () => {
    setLoading(true);
    setNotFound(false);
    setError(null);
    setComplaint(null);
    setCustomer(null);
    setBranch(null);
    setHasResolution(false);

    try {
      const res = await fetchComplaint(complaintId);
      const data = res.data;
      setComplaint(data);

      const [customersRes, branchesRes, resolutionRes] = await Promise.all([
        fetchCustomers(100).catch(() => null),
        fetchBranches(100).catch(() => null),
        fetchComplaintResolution(complaintId).catch((err) => {
          if (err instanceof ApiError && err.status === 404) return null;
          return null;
        }),
      ]);

      if (customersRes) {
        setCustomer(
          customersRes.data.find((c) => c.id === data.customerId) ?? null,
        );
      }
      if (branchesRes && data.branchId) {
        setBranch(
          branchesRes.data.find((b) => b.id === data.branchId) ?? null,
        );
      }
      setHasResolution(resolutionRes !== null);
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setNotFound(true);
      } else {
        setError(
          err instanceof ApiError
            ? err.message
            : err instanceof Error
              ? err.message
              : "Unable to load complaint.",
        );
      }
    } finally {
      setLoading(false);
    }
  }, [complaintId]);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading) {
    return (
      <PageContainer className="space-y-6">
        <PageHeader
          title="Complaint Detail"
          breadcrumbs={[
            { label: "Home", href: "/dashboard" },
            { label: "Complaints", href: "/complaints" },
            { label: "Complaint Detail" },
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
          title="Complaint Detail"
          breadcrumbs={[
            { label: "Home", href: "/dashboard" },
            { label: "Complaints", href: "/complaints" },
            { label: "Complaint Detail" },
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

  if (error || !complaint) {
    return (
      <PageContainer className="space-y-6">
        <PageHeader
          title="Complaint Detail"
          breadcrumbs={[
            { label: "Home", href: "/dashboard" },
            { label: "Complaints", href: "/complaints" },
            { label: "Complaint Detail" },
          ]}
        />
        <Empty
          title="Could not load complaint"
          description={error ?? "Unexpected error."}
          action={
            <Button type="button" variant="outline" onClick={() => void load()}>
              Retry
            </Button>
          }
        />
      </PageContainer>
    );
  }

  const customerName = customer?.fullName ?? "—";
  const customerPhone = customer?.phone?.trim() || null;
  const branchName = branch?.name ?? (complaint.branchId ? "—" : "Unassigned");

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title={complaint.complaintNumber}
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Complaints", href: "/complaints" },
          { label: "Complaint Detail" },
        ]}
        description={
          <div className="flex flex-wrap items-center gap-2 pt-1">
            <Badge tone={statusTone(complaint.status)}>
              {complaint.status.replaceAll("_", " ")}
            </Badge>
            <Badge tone={priorityTone(complaint.priority)}>
              {complaint.priority}
            </Badge>
          </div>
        }
        actions={
          <div className="flex flex-wrap gap-2">
            {canUpdate ? (
              <Button
                type="button"
                variant="outline"
                onClick={() => router.push(`/complaints/${complaint.id}/edit`)}
              >
                Edit
              </Button>
            ) : null}
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push("/complaints")}
            >
              Back to Complaints
            </Button>
          </div>
        }
      />

      {failedAttachmentCount > 0 ? (
        <Alert
          tone="warning"
          title="Complaint created successfully."
          description={
            <>
              <p>
                {failedAttachmentCount} attachment
                {failedAttachmentCount === 1 ? "" : "s"} failed to upload.
              </p>
              <p className="mt-1">
                You can upload them later from the Complaint Detail page.
              </p>
            </>
          }
        />
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Current status</CardTitle>
        </CardHeader>
        <CardBody>
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <DetailField
              label="Status"
              value={complaint.status.replaceAll("_", " ")}
            />
            <DetailField label="Priority" value={complaint.priority} />
            <DetailField
              label="Reported at"
              value={formatWhen(complaint.reportedAt)}
            />
          </dl>
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Information</CardTitle>
        </CardHeader>
        <CardBody>
          <dl className="grid grid-cols-1 gap-4">
            <DetailField label="Subject" value={complaint.subject} />
            <DetailField label="Description" value={complaint.description} />
            <DetailField
              label="Channel"
              value={complaint.channel?.trim() || "—"}
            />
            <DetailField
              label="Category"
              value={complaint.category?.trim() || "—"}
            />
          </dl>
        </CardBody>
      </Card>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Customer</CardTitle>
          </CardHeader>
          <CardBody>
            <dl className="grid grid-cols-1 gap-4">
              <DetailField label="Name" value={customerName} />
              {customerPhone ? (
                <DetailField label="Phone" value={customerPhone} />
              ) : null}
            </dl>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Branch</CardTitle>
          </CardHeader>
          <CardBody>
            <dl className="grid grid-cols-1 gap-4">
              <DetailField label="Branch Name" value={branchName} />
            </dl>
          </CardBody>
        </Card>
      </div>

      <AssignmentCard
        complaintId={complaint.id}
        onAssigned={() => {
          setTimelineKey((key) => key + 1);
          void load();
        }}
      />

      <StatusActionsCard
        complaintId={complaint.id}
        status={complaint.status}
        onStatusChanged={() => {
          setTimelineKey((key) => key + 1);
          void load();
        }}
      />

      <ResolutionCard
        complaintId={complaint.id}
        status={complaint.status}
        onResolved={() => {
          setTimelineKey((key) => key + 1);
          void load();
        }}
      />

      <EscalationCard
        complaintId={complaint.id}
        status={complaint.status}
        hasResolution={hasResolution}
        onRequested={() => {
          setTimelineKey((key) => key + 1);
          void load();
        }}
        onReviewed={() => {
          setTimelineKey((key) => key + 1);
          void load();
        }}
      />

      <AppointmentCard
        complaintId={complaint.id}
        refreshKey={timelineKey}
        onBooked={() => {
          setTimelineKey((key) => key + 1);
          void load();
        }}
      />

      <FinalResolutionCard
        complaintId={complaint.id}
        refreshKey={timelineKey}
        onSubmitted={() => {
          setTimelineKey((key) => key + 1);
          void load();
        }}
      />

      <CloseComplaintCard
        complaint={complaint}
        onClosed={() => {
          setTimelineKey((key) => key + 1);
          void load();
        }}
      />

      <CloseEscalationCard
        complaintId={complaint.id}
        complaintStatus={complaint.status}
        refreshKey={timelineKey}
        onClosed={() => {
          setTimelineKey((key) => key + 1);
          void load();
        }}
      />

      <SlaCard complaintId={complaint.id} refreshKey={timelineKey} />

      <ComplaintAttachmentsCard
        complaintId={complaint.id}
        refreshKey={timelineKey}
        allowUpload
      />

      <TimelineCard complaintId={complaint.id} refreshKey={timelineKey} />

      <Card>
        <CardHeader>
          <CardTitle>Metadata</CardTitle>
        </CardHeader>
        <CardBody>
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <DetailField
              label="Created By"
              value={complaint.createdBy ?? "—"}
            />
            <DetailField
              label="Created At"
              value={formatWhen(complaint.createdAt)}
            />
            <DetailField
              label="Updated At"
              value={formatWhen(complaint.updatedAt)}
            />
          </dl>
        </CardBody>
      </Card>

      <div className="flex justify-start border-t border-ecmp-border pt-4 sm:justify-end">
        <Button
          type="button"
          variant="outline"
          onClick={() => router.push("/complaints")}
        >
          Back to Complaints
        </Button>
      </div>
    </PageContainer>
  );
}
