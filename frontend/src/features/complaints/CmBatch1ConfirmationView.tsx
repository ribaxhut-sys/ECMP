"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
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
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const tCases = useTranslations("cases");
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
              : t("couldNotLoadComplaint"),
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [canRead, complaintId, t]);

  if (!canRead) {
    return (
      <PageContainer className="space-y-6">
        <PageHeader
          title={t("complaintRegistered")}
          breadcrumbs={[
            { label: t("home"), href: "/dashboard" },
            { label: t("title"), href: "/complaints" },
            { label: t("confirmation") },
          ]}
        />
        <Empty
          title={t("accessRestricted")}
          description={t("confirmationAccessDescription")}
          action={
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push("/complaints")}
            >{t("backToComplaints")}            </Button>
          }
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title={t("complaintRegistered")}
        breadcrumbs={[
          { label: t("home"), href: "/dashboard" },
          { label: t("title"), href: "/complaints" },
          { label: t("confirmation") },
        ]}
        description={t("confirmationDescription")}
      />

      {loading ? <Skeleton rows={5} /> : null}

      {!loading && error ? (
        <Alert tone="danger" title={t("couldNotLoadComplaint")} description={error} />
      ) : null}

      {!loading && data ? (
        <>
          <Alert
            tone="success"
            title={t("createdSuccess")}
            description={t("registeredDescription", { number: data.complaintNumber })}
          />
          <Card>
            <CardHeader>
              <CardTitle>{t("registrationDetails")}</CardTitle>
              <CardDescription>
                {t("registrationDetailsDescription")}
              </CardDescription>
            </CardHeader>
            <CardBody>
              <dl className="grid grid-cols-1 gap-3 text-sm md:grid-cols-2">
                <div>
                  <dt className="text-ecmp-text-secondary">{t("complaintNumber")}</dt>
                  <dd className="font-medium">{data.complaintNumber}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">{t("complaintId")}</dt>
                  <dd className="font-mono text-xs">{data.complaintId}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">{t("status")}</dt>
                  <dd className="font-medium">{data.status}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">{t("customerId")}</dt>
                  <dd className="font-mono text-xs">{data.customerId}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">{tCases("title")}</dt>
                  <dd>{data.caseCreated ? tCommon("yes") : tCommon("no")}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">{t("replayed")}</dt>
                  <dd>{data.replayed ? tCommon("yes") : tCommon("no")}</dd>
                </div>
                {data.category ? (
                  <div>
                    <dt className="text-ecmp-text-secondary">{t("category")}</dt>
                    <dd>{data.category}</dd>
                  </div>
                ) : null}
                {data.channel ? (
                  <div>
                    <dt className="text-ecmp-text-secondary">{t("channel")}</dt>
                    <dd>{data.channel}</dd>
                  </div>
                ) : null}
                {data.subject ? (
                  <div className="md:col-span-2">
                    <dt className="text-ecmp-text-secondary">{t("subject")}</dt>
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
              onClick={() =>
                router.push(
                  `/complaints/cm/${encodeURIComponent(data.complaintId)}/cases`,
                )
              }
            >{t("manageCases")}            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push("/complaints/new")}
            >{t("registerAnother")}            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push("/complaints")}
            >{t("backToFoundationList")}            </Button>
          </div>
        </>
      ) : null}
    </PageContainer>
  );
}
