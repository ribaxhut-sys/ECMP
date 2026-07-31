"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  fetchCmBatch1Complaint,
  type CmBatch1ComplaintResponse,
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
  PageContainer,
  PageHeader,
  Skeleton,
} from "@/shared/ui";
import { CmBatch1BoundAttachmentsCard } from "./CmBatch1BoundAttachmentsCard";

/**
 * SCR-CM-005 — Aggregate create confirmation (DEC-020 read path).
 * Does not use foundation `/api/v1/complaints/{id}`.
 */
export function CmBatch1ConfirmationView({
  complaintId,
}: {
  complaintId: string;
}) {
  const router = useRouter();
  const { hasPermission } = useAuth();
  const canRead =
    hasPermission("complaints:read") || hasPermission("complaints:create");

  const [data, setData] = useState<CmBatch1ComplaintResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!canRead || !complaintId.trim()) {
      setLoading(false);
      return;
    }
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetchCmBatch1Complaint(complaintId.trim());
        if (!cancelled) setData(res.data);
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof ApiError
              ? err.message
              : "Unable to load Aggregate complaint.",
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [canRead, complaintId]);

  if (!canRead) {
    return (
      <PageContainer className="space-y-6">
        <PageHeader
          title="Complaint registered"
          breadcrumbs={[
            { label: "Home", href: "/dashboard" },
            { label: "Complaints", href: "/complaints" },
            { label: "Confirmation" },
          ]}
        />
        <Empty
          title="Access restricted"
          description="You need complaints:read or complaints:create to view this confirmation."
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

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title="Complaint registered"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Complaints", href: "/complaints" },
          { label: "Confirmation" },
        ]}
        description="Batch-1 Aggregate confirmation (API-501). No Case is created at intake."
      />

      {loading ? <Skeleton rows={5} /> : null}

      {!loading && error ? (
        <Alert tone="danger" title="Could not load complaint" description={error} />
      ) : null}

      {!loading && data ? (
        <>
          <Alert
            tone="success"
            title="Registered"
            description={`Complaint ${data.complaintNumber} is REGISTERED on the Aggregate SoT. It will not appear on the foundation list (/api/v1/complaints) until dual-SoT convergence.`}
          />
          <Card>
            <CardHeader>
              <CardTitle>Registration details</CardTitle>
              <CardDescription>
                Status is fixed to REGISTERED; caseCreated is always false for
                Batch-1 intake.
              </CardDescription>
            </CardHeader>
            <CardBody>
              <dl className="grid grid-cols-1 gap-3 text-sm md:grid-cols-2">
                <div>
                  <dt className="text-ecmp-text-secondary">Complaint number</dt>
                  <dd className="font-medium">{data.complaintNumber}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">Complaint ID</dt>
                  <dd className="font-mono text-xs">{data.complaintId}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">Status</dt>
                  <dd className="font-medium">{data.status}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">Customer ID</dt>
                  <dd className="font-mono text-xs">{data.customerId}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">Case created</dt>
                  <dd>{data.caseCreated ? "Yes" : "No"}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">Replayed (idempotent)</dt>
                  <dd>{data.replayed ? "Yes" : "No"}</dd>
                </div>
                {data.category ? (
                  <div>
                    <dt className="text-ecmp-text-secondary">Category</dt>
                    <dd>{data.category}</dd>
                  </div>
                ) : null}
                {data.channel ? (
                  <div>
                    <dt className="text-ecmp-text-secondary">Channel</dt>
                    <dd>{data.channel}</dd>
                  </div>
                ) : null}
                {data.subject ? (
                  <div className="md:col-span-2">
                    <dt className="text-ecmp-text-secondary">Subject</dt>
                    <dd>{data.subject}</dd>
                  </div>
                ) : null}
              </dl>
            </CardBody>
          </Card>
          <CmBatch1BoundAttachmentsCard complaintId={data.complaintId} />
          <div className="flex flex-wrap gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push("/complaints/new")}
            >
              Register another
            </Button>
            <Button type="button" onClick={() => router.push("/complaints")}>
              Back to foundation list
            </Button>
          </div>
        </>
      ) : null}
    </PageContainer>
  );
}
