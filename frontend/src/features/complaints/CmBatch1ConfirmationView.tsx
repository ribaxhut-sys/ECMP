"use client";

import { useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  decideCmBatch1IntakeEscalation,
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
  ErrorState,
  Modal,
  PageContainer,
  PageHeader,
  SectionHeader,
  Skeleton,
  Textarea,
} from "@/shared/ui";
import { useToast } from "@/shared/providers";
import { CmBatch1BoundAttachmentsCard } from "./CmBatch1BoundAttachmentsCard";

const REJECT_NOTE_MIN = 20;

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
  const tPriority = useTranslations("priority");
  const router = useRouter();
  const searchParams = useSearchParams();
  const intakeEscalate = searchParams.get("intake") === "escalate";
  const intakeClosed = searchParams.get("intake") === "closed";
  const { hasPermission } = useAuth();
  const { pushSuccess, pushError } = useToast();
  const canRead =
    hasPermission("complaints:read") || hasPermission("complaints:create");
  const canDecideEscalation = hasPermission("complaints:escalate");

  const [data, setData] = useState<CmBatch1ComplaintResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [approveOpen, setApproveOpen] = useState(false);
  const [rejectOpen, setRejectOpen] = useState(false);
  const [rejectNote, setRejectNote] = useState("");
  const [deciding, setDeciding] = useState(false);
  const announcedIdRef = useRef<string | null>(null);

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

  useEffect(() => {
    if (!data) return;
    if (announcedIdRef.current === data.complaintId) return;
    announcedIdRef.current = data.complaintId;
    const closed = intakeClosed || data.status === "CLOSED";
    if (closed) {
      pushSuccess(
        t("closedSuccess"),
        t("closedSuccessDescription", { number: data.complaintNumber }),
      );
      return;
    }
    if (intakeEscalate) {
      pushSuccess(
        t("escalateSuccess"),
        t("escalateSuccessDescription", { number: data.complaintNumber }),
      );
      return;
    }
    pushSuccess(
      t("createdSuccess"),
      t("registeredDescription", { number: data.complaintNumber }),
    );
  }, [data, intakeClosed, intakeEscalate, pushSuccess, t]);

  async function submitDecision(decision: "APPROVE" | "REJECT"): Promise<void> {
    if (!data) return;
    setDeciding(true);
    try {
      const res = await decideCmBatch1IntakeEscalation(data.complaintId, {
        decision,
        note: decision === "REJECT" ? rejectNote.trim() : undefined,
      });
      setData(res.data);
      setApproveOpen(false);
      setRejectOpen(false);
      setRejectNote("");
      if (decision === "APPROVE") {
        pushSuccess(
          t("escalationApprovedToast"),
          t("escalationApprovedToastDescription", {
            number: res.data.complaintNumber,
          }),
        );
      } else {
        pushSuccess(
          t("escalationRejectedToast"),
          t("escalationRejectedToastDescription", {
            number: res.data.complaintNumber,
          }),
        );
      }
    } catch (err) {
      pushError(err, t("escalationDecisionFailed"));
    } finally {
      setDeciding(false);
    }
  }

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
          primaryAction={{
            label: tCommon("goHome"),
            onClick: () => router.push("/dashboard"),
          }}
        />
      </PageContainer>
    );
  }

  const statusLabel =
    data?.status === "CLOSED"
      ? t("statusClosed")
      : data?.status === "REGISTERED"
        ? t("registered")
        : (data?.status ?? "");

  const pendingEscalation =
    data?.status === "REGISTERED" &&
    data.intakeDisposition === "ESCALATE_PENDING_APPROVAL";
  const showSupervisorActions = pendingEscalation && canDecideEscalation;

  const priorityRaw = (data?.priority || "").toUpperCase();
  const priorityKnown = ["LOW", "MEDIUM", "HIGH", "CRITICAL"] as const;
  const priorityLabel =
    (priorityKnown as readonly string[]).includes(priorityRaw)
      ? tPriority(priorityRaw as (typeof priorityKnown)[number])
      : priorityRaw || tCommon("emDash");

  const pageTitle =
    intakeClosed || data?.status === "CLOSED"
      ? t("intakeClosedBannerTitle")
      : pendingEscalation || intakeEscalate
        ? t("intakeEscalateBannerTitle")
        : t("complaintRegistered");

  const rejectNoteOk = rejectNote.trim().length >= REJECT_NOTE_MIN;

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={pageTitle}
        breadcrumbs={[
          { label: t("home"), href: "/dashboard" },
          { label: t("title"), href: "/complaints" },
          { label: t("confirmation") },
        ]}
        description={
          intakeClosed || data?.status === "CLOSED"
            ? t("intakeClosedBannerDescription")
            : pendingEscalation || intakeEscalate
              ? t("intakeEscalateBannerDescription")
              : t("confirmationDescription")
        }
      />

      {intakeClosed ? (
        <Alert
          tone="info"
          title={t("intakeClosedBannerTitle")}
          description={t("intakeClosedBannerDescription")}
        />
      ) : null}

      {pendingEscalation || intakeEscalate ? (
        <Alert
          tone="info"
          title={t("intakeEscalateBannerTitle")}
          description={t("intakeEscalateBannerDescription")}
        />
      ) : null}

      {loading ? <Skeleton rows={5} /> : null}

      {!loading && error ? (
        <ErrorState
          title={t("couldNotLoadComplaint")}
          message={error}
          onRetry={() => {
            setLoading(true);
            setError(null);
            void fetchCmBatch1Complaint(complaintId.trim())
              .then((res) => setData(res.data))
              .catch((err) =>
                setError(
                  err instanceof ApiError
                    ? err.message
                    : t("couldNotLoadComplaint"),
                ),
              )
              .finally(() => setLoading(false));
          }}
        />
      ) : null}

      {!loading && data ? (
        <>
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
                      {t("status")}
                    </dt>
                    <dd className="flex flex-wrap items-center gap-2">
                      <Badge
                        tone={
                          data.status === "CLOSED" ? "success" : "info"
                        }
                      >
                        {statusLabel}
                      </Badge>
                      {data.intakeDisposition ===
                      "ESCALATE_PENDING_APPROVAL" ? (
                        <Badge tone="warning">{t("awaitingApproval")}</Badge>
                      ) : null}
                      {data.intakeDisposition === "ESCALATE_APPROVED" ? (
                        <Badge tone="info">{t("escalationApproved")}</Badge>
                      ) : null}
                      {data.intakeDisposition === "ESCALATE_REJECTED" ? (
                        <Badge tone="neutral">{t("escalationRejected")}</Badge>
                      ) : null}
                    </dd>
                  </div>
                  {intakeEscalate ||
                  pendingEscalation ||
                  (data.priority && data.status !== "CLOSED") ? (
                    <div className="space-y-1">
                      <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                        {t("priority")}
                      </dt>
                      <dd>
                        <Badge
                          tone={
                            ["CRITICAL", "HIGH"].includes(
                              (data.priority || "").toUpperCase(),
                            )
                              ? "danger"
                              : "neutral"
                          }
                        >
                          {priorityLabel}
                        </Badge>
                      </dd>
                    </div>
                  ) : null}
                  <div className="space-y-1">
                    <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                      {tCases("title")}
                    </dt>
                    <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                      {data.caseCreated ? tCommon("yes") : tCommon("no")}
                    </dd>
                  </div>
                  {data.replayed ? (
                    <div className="space-y-1">
                      <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                        {t("replayed")}
                      </dt>
                      <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                        {tCommon("yes")}
                      </dd>
                    </div>
                  ) : null}
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

          <CmBatch1BoundAttachmentsCard
            complaintId={data.complaintId}
            customerId={data.customerId}
          />

          <div className="flex flex-wrap gap-[var(--ecmp-form-gap)]">
            {showSupervisorActions ? (
              <>
                <Button
                  type="button"
                  onClick={() => setApproveOpen(true)}
                  disabled={deciding}
                >
                  {t("approveEscalation")}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setRejectOpen(true)}
                  disabled={deciding}
                >
                  {t("rejectEscalation")}
                </Button>
              </>
            ) : null}
            {intakeEscalate && !showSupervisorActions ? (
              <Button
                type="button"
                onClick={() => router.push("/complaints/cm/supervisor")}
              >
                {t("openSupervisorQueue")}
              </Button>
            ) : null}
            {!intakeClosed && !pendingEscalation && !intakeEscalate ? (
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
            ) : null}
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
              {t("backToComplaints")}
            </Button>
          </div>
        </>
      ) : null}

      <Modal
        open={approveOpen}
        onClose={() => (!deciding ? setApproveOpen(false) : undefined)}
        title={t("approveEscalationTitle")}
        size="sm"
        footer={
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setApproveOpen(false)}
              disabled={deciding}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              loading={deciding}
              onClick={() => void submitDecision("APPROVE")}
            >
              {t("approveEscalation")}
            </Button>
          </div>
        }
      >
        <p className="text-ecmp-text-primary">
          {t("approveEscalationBody", {
            number: data?.complaintNumber ?? "",
          })}
        </p>
      </Modal>

      <Modal
        open={rejectOpen}
        onClose={() => (!deciding ? setRejectOpen(false) : undefined)}
        title={t("rejectEscalationTitle")}
        size="sm"
        footer={
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setRejectOpen(false)}
              disabled={deciding}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              variant="danger"
              loading={deciding}
              disabled={!rejectNoteOk}
              onClick={() => void submitDecision("REJECT")}
            >
              {t("rejectEscalation")}
            </Button>
          </div>
        }
      >
        <div className="space-y-3">
          <p className="text-ecmp-text-primary">
            {t("rejectEscalationBody", {
              number: data?.complaintNumber ?? "",
            })}
          </p>
          <Textarea
            label={t("rejectEscalationNoteLabel")}
            hint={t("rejectEscalationNoteHint")}
            value={rejectNote}
            onChange={(e) => setRejectNote(e.target.value)}
            rows={4}
            maxLength={2000}
            disabled={deciding}
          />
        </div>
      </Modal>
    </PageContainer>
  );
}
