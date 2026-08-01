"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { ApiError, fetchCmCase, type CmCase } from "@/lib/api";
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
  PageContainer,
  PageHeader,
  Skeleton,
  Toast,
} from "@/shared/ui";
import { CaseStatusBadge } from "./CaseStatusBadge";
import { CloseCaseDialog } from "./CloseCaseDialog";
import { ResolveCaseDialog } from "./ResolveCaseDialog";
import { UpdateStatusDialog } from "./UpdateStatusDialog";
import { rememberCaseId } from "./caseSessionRegistry";
import { allowedStatusTargets, canClose, canResolve } from "./caseStatus";

export function CaseDetailView({ caseId }: { caseId: string }) {
  const t = useTranslations("cases");
  const router = useRouter();
  const { hasPermission } = useAuth();
  const canRead = hasPermission("complaints:read");
  const canUpdate = hasPermission("complaints:update");

  const [data, setData] = useState<CmCase | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusOpen, setStatusOpen] = useState(false);
  const [resolveOpen, setResolveOpen] = useState(false);
  const [closeOpen, setCloseOpen] = useState(false);
  const [toastOpen, setToastOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState("");

  const reload = useCallback(async () => {
    if (!canRead || !caseId.trim()) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetchCmCase(caseId.trim());
      setData(res.data);
      rememberCaseId(res.data.complaintId, res.data.caseId);
    } catch (err) {
      setData(null);
      setError(
        err instanceof ApiError ? err.message : t("unableToLoad"),
      );
    } finally {
      setLoading(false);
    }
  }, [canRead, caseId]);

  useEffect(() => {
    void reload();
  }, [reload]);

  function showSuccess(message: string) {
    setToastMessage(message);
    setToastOpen(true);
  }

  if (!canRead) {
    return (
      <PageContainer className="space-y-6">
        <PageHeader
          title={t("title")}
          breadcrumbs={[
            { label: t("back"), href: "/dashboard" },
            { label: t("confirmation"), href: "/complaints" },
            { label: t("title") },
          ]}
        />
        <Empty
          title={t("accessDenied")}
          description={t("readPermission")}
        />
      </PageContainer>
    );
  }

  const statusTargets = data ? allowedStatusTargets(data.status) : [];
  const showStatus = Boolean(data && canUpdate && statusTargets.length > 0);
  const showResolve = Boolean(data && canUpdate && canResolve(data.status));
  const showClose = Boolean(data && canUpdate && canClose(data.status));

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title={data?.caseNumber ?? t("title")}
        description={data?.subject}
        breadcrumbs={[
          { label: t("back"), href: "/dashboard" },
          { label: t("confirmation"), href: "/complaints" },
          ...(data
            ? [
                {
                  label: t("list"),
                  href: `/complaints/cm/${encodeURIComponent(data.complaintId)}/cases`,
                },
              ]
            : []),
          { label: data?.caseNumber ?? t("detailFallback") },
        ]}
        actions={
          <div className="flex flex-wrap gap-2">
            {data ? (
              <Button
                type="button"
                variant="outline"
                onClick={() =>
                  router.push(
                    `/complaints/cm/${encodeURIComponent(data.complaintId)}/cases`,
                  )
                }
              >{t("caseList")}              </Button>
            ) : null}
            {showStatus ? (
              <Button type="button" onClick={() => setStatusOpen(true)}>{t("updateStatus")}              </Button>
            ) : null}
            {showResolve ? (
              <Button type="button" onClick={() => setResolveOpen(true)}>{t("resolve")}              </Button>
            ) : null}
            {showClose ? (
              <Button type="button" onClick={() => setCloseOpen(true)}>{t("close")}              </Button>
            ) : null}
          </div>
        }
      />

      {loading ? <Skeleton rows={6} /> : null}
      {!loading && error ? (
        <ErrorState title={t("unableToLoad")} message={error} />
      ) : null}

      {!loading && data ? (
        <>
          <Card>
            <CardHeader className="flex flex-row flex-wrap items-start justify-between gap-3">
              <div className="space-y-1">
                <CardTitle>{data.caseNumber}</CardTitle>
                <CardDescription>
                  {t("identitySummary", {
                    caseId: data.caseId,
                    complaintId: data.complaintId,
                  })}
                </CardDescription>
              </div>
              <CaseStatusBadge status={data.status} />
            </CardHeader>
            <CardBody>
              <dl className="grid gap-3 text-[length:var(--ecmp-font-body-size)] sm:grid-cols-2">
                <div>
                  <dt className="text-ecmp-text-secondary">{t("type")}</dt>
                  <dd>{data.caseType}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">{t("priority")}</dt>
                  <dd>{data.priority}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">{t("category")}</dt>
                  <dd>{data.category ?? "—"}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">{t("owningUnit")}</dt>
                  <dd>{data.owningUnitId ?? "—"}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">{t("customer")}</dt>
                  <dd className="font-mono text-xs">{data.customerId}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">{t("createdAt")}</dt>
                  <dd>{data.createdAt}</dd>
                </div>
                <div className="sm:col-span-2">
                  <dt className="text-ecmp-text-secondary">{t("subject")}</dt>
                  <dd>{data.subject}</dd>
                </div>
                <div className="sm:col-span-2">
                  <dt className="text-ecmp-text-secondary">{t("description")}</dt>
                  <dd className="whitespace-pre-wrap">{data.description}</dd>
                </div>
                {data.cancelReason ? (
                  <div>
                    <dt className="text-ecmp-text-secondary">{t("cancelReason")}</dt>
                    <dd>{data.cancelReason}</dd>
                  </div>
                ) : null}
                {data.closedAt ? (
                  <div>
                    <dt className="text-ecmp-text-secondary">{t("closedAt")}</dt>
                    <dd>{data.closedAt}</dd>
                  </div>
                ) : null}
              </dl>
            </CardBody>
          </Card>

          {data.resolution ? (
            <Card>
              <CardHeader>
                <CardTitle>{t("resolution")}</CardTitle>
                <CardDescription>
                  {data.resolution.status} · {data.resolution.resolutionCode}
                </CardDescription>
              </CardHeader>
              <CardBody className="space-y-2 text-[length:var(--ecmp-font-body-size)]">
                <p>{data.resolution.summary}</p>
                {data.resolution.detail ? (
                  <p className="text-ecmp-text-secondary whitespace-pre-wrap">
                    {data.resolution.detail}
                  </p>
                ) : null}
                <p className="text-ecmp-text-secondary">
                  {t("comment")}: {data.resolution.comment}
                </p>
              </CardBody>
            </Card>
          ) : null}

          {!canUpdate ? (
            <Alert
              tone="info"
              title={t("readOnly")}
              description={t("updatePermission")}
            />
          ) : null}
        </>
      ) : null}

      {data ? (
        <>
          <UpdateStatusDialog
            open={statusOpen}
            onClose={() => setStatusOpen(false)}
            caseData={data}
            onUpdated={(next) => {
              setData(next);
              showSuccess(t("statusUpdated", { status: next.status }));
            }}
          />
          <ResolveCaseDialog
            open={resolveOpen}
            onClose={() => setResolveOpen(false)}
            caseId={data.caseId}
            onResolved={(next) => {
              setData(next);
              showSuccess(t("caseCreated", { number: next.caseNumber, status: next.status }));
            }}
          />
          <CloseCaseDialog
            open={closeOpen}
            onClose={() => setCloseOpen(false)}
            caseId={data.caseId}
            onClosed={(next) => {
              setData(next);
              showSuccess(t("closed", { number: next.caseNumber }));
            }}
          />
        </>
      ) : null}

      <Toast
        open={toastOpen}
        onClose={() => setToastOpen(false)}
        title={t("success")}
        description={toastMessage}
        tone="success"
      />
    </PageContainer>
  );
}
