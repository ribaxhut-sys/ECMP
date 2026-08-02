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
  Badge,
  Button,
  Card,
  CardBody,
  Empty,
  PageContainer,
  PageHeader,
  SectionHeader,
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
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
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
            >
              {t("backToComplaints")}
            </Button>
          }
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
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

          <section className="space-y-[var(--ecmp-panel-gap)]">
            <SectionHeader
              title={t("registrationDetails")}
              description={t("registrationDetailsDescription")}
            />
            <Card>
              <CardBody>
                <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] md:grid-cols-2">
                  <div className="space-y-1">
                    <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                      {t("complaintNumber")}
                    </dt>
                    <dd className="text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary">
                      {data.complaintNumber}
                    </dd>
                  </div>
                  <div className="space-y-1">
                    <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                      {t("complaintId")}
                    </dt>
                    <dd className="break-all font-mono text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-primary">
                      {data.complaintId}
                    </dd>
                  </div>
                  <div className="space-y-1">
                    <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                      {t("status")}
                    </dt>
                    <dd>
                      <Badge tone="info">{data.status}</Badge>
                    </dd>
                  </div>
                  <div className="space-y-1">
                    <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                      {t("customerId")}
                    </dt>
                    <dd className="break-all font-mono text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-primary">
                      {data.customerId}
                    </dd>
                  </div>
                  <div className="space-y-1">
                    <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                      {tCases("title")}
                    </dt>
                    <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                      {data.caseCreated ? tCommon("yes") : tCommon("no")}
                    </dd>
                  </div>
                  <div className="space-y-1">
                    <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                      {t("replayed")}
                    </dt>
                    <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                      {data.replayed ? tCommon("yes") : tCommon("no")}
                    </dd>
                  </div>
                  {data.category ? (
                    <div className="space-y-1">
                      <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                        {t("category")}
                      </dt>
                      <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                        {data.category}
                      </dd>
                    </div>
                  ) : null}
                  {data.channel ? (
                    <div className="space-y-1">
                      <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                        {t("channel")}
                      </dt>
                      <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                        {data.channel}
                      </dd>
                    </div>
                  ) : null}
                  {data.subject ? (
                    <div className="space-y-1 md:col-span-2">
                      <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                        {t("subject")}
                      </dt>
                      <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                        {data.subject}
                      </dd>
                    </div>
                  ) : null}
                </dl>
              </CardBody>
            </Card>
          </section>

          <CmBatch1BoundAttachmentsCard complaintId={data.complaintId} />

          <div className="flex flex-wrap gap-[var(--ecmp-form-gap)]">
            <Button
              type="button"
              onClick={() =>
                router.push(
                  `/complaints/cm/${encodeURIComponent(data.complaintId)}/cases`,
                )
              }
            >
              {t("manageCases")}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push("/complaints/new")}
            >
              {t("registerAnother")}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push("/complaints")}
            >
              {t("backToFoundationList")}
            </Button>
          </div>
        </>
      ) : null}
    </PageContainer>
  );
}
