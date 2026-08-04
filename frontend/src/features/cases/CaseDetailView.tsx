"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { ApiError, fetchCmCase, type CmCase } from "@/lib/api";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Empty,
  ErrorState,
  PageContainer,
  PageHeader,
  SectionHeader,
  Skeleton,
  Toast,
  type BadgeTone,
} from "@/shared/ui";
import {
  CwxContextAwareLayout,
  CwxContextHeader,
  CwxDecisionBar,
  CwxOperationalContextBlock,
  deriveContextLevel,
  deriveOperationalContext,
  type CwxDecisionAction,
} from "@/features/cwx";
import { CaseStatusBadge } from "./CaseStatusBadge";
import { CloseCaseDialog } from "./CloseCaseDialog";
import { ResolveCaseDialog } from "./ResolveCaseDialog";
import { UpdateStatusDialog } from "./UpdateStatusDialog";
import { rememberCaseId } from "./caseSessionRegistry";
import { allowedStatusTargets, canClose, canResolve } from "./caseStatus";

function priorityTone(priority: string): BadgeTone {
  switch (priority.toUpperCase()) {
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

/**
 * CWX-M1/M2 Aggregate wiring only.
 * Parent owns Aggregate SoT (`fetchCmCase`). No Evidence / Working Actions / History (M3/M4).
 */
export function CaseDetailView({ caseId }: { caseId: string }) {
  const t = useTranslations("cases");
  const tCwx = useTranslations("cwx");
  const tCommon = useTranslations("common");
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
      setError(err instanceof ApiError ? err.message : t("unableToLoad"));
    } finally {
      setLoading(false);
    }
  }, [canRead, caseId, t]);

  useEffect(() => {
    void reload();
  }, [reload]);

  function showSuccess(message: string) {
    setToastMessage(message);
    setToastOpen(true);
  }

  const breadcrumbs = useMemo(
    () => [
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
    ],
    [data, t],
  );

  if (!canRead) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader title={t("title")} breadcrumbs={breadcrumbs} />
        <Empty title={t("accessDenied")} description={t("readPermission")} />
      </PageContainer>
    );
  }

  const statusTargets = data ? allowedStatusTargets(data.status) : [];
  const showStatus = Boolean(data && canUpdate && statusTargets.length > 0);
  const showResolve = Boolean(data && canUpdate && canResolve(data.status));
  const showClose = Boolean(data && canUpdate && canClose(data.status));

  const level = data
    ? deriveContextLevel({
        status: data.status,
        priority: data.priority,
        slaBreached: false,
      })
    : 1;

  const decisionActions: CwxDecisionAction[] = [];
  if (data && showStatus) {
    decisionActions.push({
      id: "update-status",
      label: t("updateStatus"),
      emphasize: true,
      onClick: () => setStatusOpen(true),
    });
  }
  if (data && showResolve) {
    decisionActions.push({
      id: "resolve",
      label: t("resolve"),
      onClick: () => setResolveOpen(true),
    });
  }
  if (data && showClose) {
    decisionActions.push({
      id: "close",
      label: t("close"),
      onClick: () => setCloseOpen(true),
    });
  }
  if (data) {
    decisionActions.push({
      id: "case-list",
      label: t("caseList"),
      onClick: () =>
        router.push(
          `/complaints/cm/${encodeURIComponent(data.complaintId)}/cases`,
        ),
    });
    decisionActions.push({
      id: "queue",
      label: tCwx("backToQueue"),
      onClick: () => router.push("/queue"),
    });
  }

  const owner =
    data?.assignedUserId?.trim() ||
    data?.owningUnitId?.trim() ||
    data?.createdBy?.trim() ||
    tCommon("emDash");

  const slaLabel = data?.slaCountdownActive
    ? tCwx("slaOnTrack")
    : tCwx("slaUnavailable");

  const assignedToLabel = data?.assignedUserId?.trim() || null;

  const cwxM2 = data
    ? deriveOperationalContext({
        surface: "aggregate",
        status: data.status,
        priority: data.priority,
        assignedToLabel,
        lastUpdated: data.updatedAt ?? null,
        category: data.category,
        createdAt: data.createdAt,
        // Customer display name not on CmCase — omit (no invent / no Customer Master).
      })
    : null;

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader title={t("detail")} breadcrumbs={breadcrumbs} />

      {loading ? <Skeleton rows={6} /> : null}
      {!loading && error ? (
        <ErrorState title={t("unableToLoad")} message={error} />
      ) : null}

      {!loading && data ? (
        <CwxContextAwareLayout
          level={level}
          labels={{
            customerHistorySlot: tCwx("slotCustomerHistory"),
            decisionStatusSlot: tCwx("slotDecisionStatus"),
            slaAlertSlot: tCwx("slotSlaAlert"),
            reserved: tCwx("slotReserved"),
          }}
          header={
            <CwxContextHeader
              complaintId={data.caseNumber}
              customer={data.customerId}
              title={data.subject}
              priorityLabel={data.priority}
              priorityTone={priorityTone(data.priority)}
              currentWork={data.status}
              owner={owner}
              slaLabel={slaLabel}
              slaTone={data.slaCountdownActive ? "success" : "neutral"}
            />
          }
          decisionBar={
            <CwxDecisionBar
              actions={decisionActions}
              overflowLabel={tCwx("moreActions")}
              emptyLabel={tCwx("noActions")}
            />
          }
          main={
            <div className="space-y-[var(--ecmp-section-gap)]">
              {cwxM2 ? (
                <CwxOperationalContextBlock
                  derived={cwxM2}
                  operationalLabels={{
                    status: data.status,
                    assignedTo: assignedToLabel ?? undefined,
                    lastUpdated: data.updatedAt ?? undefined,
                  }}
                  caseSummaryStageLabel={data.status}
                  caseSummaryCreatedLabel={data.createdAt}
                  responsibleLabel={assignedToLabel ?? undefined}
                />
              ) : null}

              <section className="space-y-[var(--ecmp-panel-gap)]">
                <SectionHeader
                  title={data.caseNumber}
                  description={t("identitySummary", {
                    caseId: data.caseId,
                    complaintId: data.complaintId,
                  })}
                  actions={<CaseStatusBadge status={data.status} />}
                />
                <Card>
                  <CardBody>
                    <dl className="grid gap-[var(--ecmp-form-gap)] text-[length:var(--ecmp-font-body-size)] sm:grid-cols-2">
                      <div className="space-y-1">
                        <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                          {t("type")}
                        </dt>
                        <dd className="text-ecmp-text-primary">{data.caseType}</dd>
                      </div>
                      <div className="space-y-1">
                        <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                          {t("priority")}
                        </dt>
                        <dd className="text-ecmp-text-primary">{data.priority}</dd>
                      </div>
                      <div className="space-y-1">
                        <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                          {t("category")}
                        </dt>
                        <dd className="text-ecmp-text-primary">
                          {data.category ?? "—"}
                        </dd>
                      </div>
                      <div className="space-y-1">
                        <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                          {t("owningUnit")}
                        </dt>
                        <dd className="text-ecmp-text-primary">
                          {data.owningUnitId ?? "—"}
                        </dd>
                      </div>
                      <div className="space-y-1">
                        <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                          {t("customer")}
                        </dt>
                        <dd className="break-all font-mono text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-primary">
                          {data.customerId}
                        </dd>
                      </div>
                      <div className="space-y-1">
                        <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                          {t("createdAt")}
                        </dt>
                        <dd className="text-ecmp-text-primary">{data.createdAt}</dd>
                      </div>
                      <div className="space-y-1 sm:col-span-2">
                        <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                          {t("subject")}
                        </dt>
                        <dd className="text-ecmp-text-primary">{data.subject}</dd>
                      </div>
                      <div className="space-y-1 sm:col-span-2">
                        <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                          {t("description")}
                        </dt>
                        <dd className="whitespace-pre-wrap text-ecmp-text-primary">
                          {data.description}
                        </dd>
                      </div>
                      {data.cancelReason ? (
                        <div className="space-y-1">
                          <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                            {t("cancelReason")}
                          </dt>
                          <dd className="text-ecmp-text-primary">
                            {data.cancelReason}
                          </dd>
                        </div>
                      ) : null}
                      {data.closedAt ? (
                        <div className="space-y-1">
                          <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                            {t("closedAt")}
                          </dt>
                          <dd className="text-ecmp-text-primary">
                            {data.closedAt}
                          </dd>
                        </div>
                      ) : null}
                    </dl>
                  </CardBody>
                </Card>
              </section>

              {data.resolution ? (
                <section className="space-y-[var(--ecmp-panel-gap)]">
                  <SectionHeader
                    title={t("resolution")}
                    description={`${data.resolution.status} · ${data.resolution.resolutionCode}`}
                  />
                  <Card>
                    <CardBody className="space-y-2 text-[length:var(--ecmp-font-body-size)]">
                      <p className="text-ecmp-text-primary">
                        {data.resolution.summary}
                      </p>
                      {data.resolution.detail ? (
                        <p className="whitespace-pre-wrap text-ecmp-text-secondary">
                          {data.resolution.detail}
                        </p>
                      ) : null}
                      <p className="text-ecmp-text-secondary">
                        {t("comment")}: {data.resolution.comment}
                      </p>
                    </CardBody>
                  </Card>
                </section>
              ) : null}

              {!canUpdate ? (
                <Alert
                  tone="info"
                  title={t("readOnly")}
                  description={t("updatePermission")}
                />
              ) : null}

              <div className="flex flex-wrap gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() =>
                    router.push(
                      `/complaints/cm/${encodeURIComponent(data.complaintId)}/cases`,
                    )
                  }
                >
                  {t("caseList")}
                </Button>
              </div>
            </div>
          }
        />
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
              showSuccess(
                t("caseCreated", {
                  number: next.caseNumber,
                  status: next.status,
                }),
              );
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
