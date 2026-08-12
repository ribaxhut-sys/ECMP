"use client";

import { useEffect, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Empty,
  Input,
  Modal,
  ModalSection,
  PageContainer,
  PageHeader,
  Select,
  Textarea,
  Timeline,
  Toast,
  type SelectOption,
  type TimelineItem,
} from "@/shared/ui";
import { fetchBranches, type Branch } from "@/lib/api/branches";
import {
  receiveInternalComplaint,
  recordInternalAcceptance,
  resolveInternalComplaint,
  transferInternalComplaint,
} from "@/lib/api/internalComplaints";
import { useInternalComplaint } from "./mock/useInternalComplaints";
import {
  HISTORY_LABEL_KEY,
  canAccept,
  canReceive,
  canResolve,
  canTransfer,
} from "./types";
import {
  InternalPriorityBadge,
  InternalStatusBadge,
} from "./components/InternalBadges";
import {
  filterTransferDestinations,
  formatUnitOptionLabel,
} from "./transferDirection";

function formatDateTime(value: string | null | undefined): string {
  if (!value) return "—";
  try {
    return new Intl.DateTimeFormat(undefined, {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function displayPersonName(
  name: string | null | undefined,
  fallbackId: string | null | undefined,
  unknownLabel: string,
): string {
  const label = (name || "").trim();
  if (label) return label;
  const id = (fallbackId || "").trim();
  return id ? unknownLabel : "—";
}

type ModalKind = "transfer" | "resolve" | "accept" | "reject" | null;

export function InternalComplaintDetailView({ id }: { id: string }) {
  const t = useTranslations("internalComplaints");
  const tCommon = useTranslations("common");
  const { hasPermission } = useAuth();
  const { complaint, loading, error, reload } = useInternalComplaint(id);

  const [branches, setBranches] = useState<Branch[]>([]);
  const [modal, setModal] = useState<ModalKind>(null);
  const [destinationUnitId, setDestinationUnitId] = useState("");
  const [transferReason, setTransferReason] = useState("");
  const [resolveSummary, setResolveSummary] = useState("");
  const [resolveCode, setResolveCode] = useState("IC-OK");
  const [resolveComment, setResolveComment] = useState("");
  const [acceptParty, setAcceptParty] = useState<"OWNER" | "HANDLING_UNIT">(
    "OWNER",
  );
  const [acceptNote, setAcceptNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchBranches(100)
      .then((res) => setBranches(res.data ?? []))
      .catch(() => setBranches([]));
  }, []);

  const activityItems: TimelineItem[] = useMemo(() => {
    const unknown = t("unknownUser");
    return (complaint?.history ?? [])
      .slice()
      .reverse()
      .map((event) => {
        const actorName = displayPersonName(
          event.actorName,
          event.actorId,
          unknown,
        );
        const unitMove =
          event.sourceUnitId &&
          event.targetUnitId &&
          event.sourceUnitId !== event.targetUnitId
            ? `${event.sourceUnitId} → ${event.targetUnitId}`
            : null;
        return {
          id: event.eventId,
          title: t(HISTORY_LABEL_KEY[event.eventType] ?? "activityCREATED"),
          description:
            [event.note, unitMove].filter(Boolean).join(" · ") || undefined,
          time: formatDateTime(event.occurredAt),
          actor: t("historyActor", { name: actorName }),
        };
      });
  }, [complaint, t]);

  const unitOptions: SelectOption[] = useMemo(
    () =>
      filterTransferDestinations(branches, complaint?.handlingUnitId).map(
        (b) => ({
          value: b.code,
          label: formatUnitOptionLabel(b.code, b.name),
        }),
      ),
    [branches, complaint?.handlingUnitId],
  );

  if (loading) {
    return (
      <PageContainer>
        <Empty title={tCommon("loading")} description="" />
      </PageContainer>
    );
  }

  if (!complaint || error) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader
          title={t("detailFallback")}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: t("title"), href: "/internal" },
            { label: t("listTitle"), href: "/internal/complaints" },
          ]}
        />
        <Empty
          title={t("detailFallback")}
          description={error ?? t("listEmptyDescription")}
        />
      </PageContainer>
    );
  }

  async function run(action: () => Promise<unknown>, okMessage: string) {
    setBusy(true);
    setActionError(null);
    try {
      await action();
      setModal(null);
      setToastMessage(okMessage);
      reload();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : t("actionFailed"));
    } finally {
      setBusy(false);
    }
  }

  const showReceive = canReceive(complaint.status) && hasPermission("complaints:update");
  const showTransfer = canTransfer(complaint.status) && hasPermission("complaints:assign");
  const showResolve = canResolve(complaint.status) && hasPermission("complaints:update");
  const showAccept = canAccept(complaint.status) && hasPermission("complaints:update");

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={complaint.number}
        description={complaint.title}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title"), href: "/internal" },
          { label: t("listTitle"), href: "/internal/complaints" },
          { label: complaint.number },
        ]}
        actions={
          <div className="flex flex-wrap gap-2">
            {showReceive ? (
              <Button
                type="button"
                disabled={busy}
                onClick={() =>
                  run(
                    () => receiveInternalComplaint(complaint.id),
                    t("receivedOk"),
                  )
                }
              >
                {t("receive")}
              </Button>
            ) : null}
            {showTransfer ? (
              <Button
                type="button"
                variant="secondary"
                disabled={busy}
                onClick={() => setModal("transfer")}
              >
                {t("transfer")}
              </Button>
            ) : null}
            {showResolve ? (
              <Button
                type="button"
                disabled={busy}
                onClick={() => setModal("resolve")}
              >
                {t("resolve")}
              </Button>
            ) : null}
            {showAccept ? (
              <>
                <Button
                  type="button"
                  disabled={busy}
                  onClick={() => {
                    setAcceptParty("HANDLING_UNIT");
                    setModal("accept");
                  }}
                >
                  {t("acceptHandling")}
                </Button>
                <Button
                  type="button"
                  disabled={busy}
                  onClick={() => {
                    setAcceptParty("OWNER");
                    setModal("accept");
                  }}
                >
                  {t("acceptOwner")}
                </Button>
                <Button
                  type="button"
                  variant="danger"
                  disabled={busy}
                  onClick={() => setModal("reject")}
                >
                  {t("reject")}
                </Button>
              </>
            ) : null}
          </div>
        }
      />

      {actionError ? <Alert tone="danger" title={actionError} /> : null}

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>{t("sectionBasics")}</CardTitle>
          </CardHeader>
          <CardBody className="space-y-2 text-sm">
            <div className="flex flex-wrap gap-2">
              <InternalStatusBadge status={complaint.status} />
              <InternalPriorityBadge priority={complaint.priority} />
            </div>
            <p>
              <span className="text-ecmp-text-secondary">{t("ownerUnit")}: </span>
              {complaint.ownerUnitId}
            </p>
            <p>
              <span className="text-ecmp-text-secondary">
                {t("handlingUnit")}:{" "}
              </span>
              {complaint.handlingUnitId}
            </p>
            {complaint.relatedComplaintNumber ? (
              <p>
                <span className="text-ecmp-text-secondary">
                  {t("relatedComplaint")}:{" "}
                </span>
                {complaint.relatedComplaintNumber}
              </p>
            ) : null}
            <p>
              <span className="text-ecmp-text-secondary">
                {t("handlingAcceptance")}:{" "}
              </span>
              {complaint.handlingUnitAcceptance ?? "—"}
            </p>
            <p>
              <span className="text-ecmp-text-secondary">
                {t("ownerAcceptance")}:{" "}
              </span>
              {complaint.ownerAcceptance ?? "—"}
            </p>
            <p>
              <span className="text-ecmp-text-secondary">{t("createdBy")}: </span>
              {displayPersonName(
                complaint.createdByName,
                complaint.createdBy,
                t("unknownUser"),
              )}
            </p>
            <p>
              <span className="text-ecmp-text-secondary">{t("createdAt")}: </span>
              {formatDateTime(complaint.createdAt)}
            </p>
            {complaint.resolutionSummary ? (
              <p>
                <span className="text-ecmp-text-secondary">
                  {t("resolution")}:{" "}
                </span>
                {complaint.resolutionSummary}
              </p>
            ) : null}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t("sectionNarrative")}</CardTitle>
          </CardHeader>
          <CardBody className="space-y-3 text-sm whitespace-pre-wrap">
            <div>
              <div className="text-ecmp-text-secondary">{t("description")}</div>
              <div>{complaint.description}</div>
            </div>
            {complaint.chronology ? (
              <div>
                <div className="text-ecmp-text-secondary">{t("chronology")}</div>
                <div>{complaint.chronology}</div>
              </div>
            ) : null}
            {complaint.impact ? (
              <div>
                <div className="text-ecmp-text-secondary">{t("impact")}</div>
                <div>{complaint.impact}</div>
              </div>
            ) : null}
          </CardBody>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t("history")}</CardTitle>
        </CardHeader>
        <CardBody>
          {activityItems.length === 0 ? (
            <Empty title={t("historyEmpty")} description="" />
          ) : (
            <Timeline items={activityItems} />
          )}
        </CardBody>
      </Card>

      <Modal
        open={modal === "transfer"}
        onClose={() => setModal(null)}
        title={t("transfer")}
      >
        <ModalSection className="space-y-3">
          <Select
            label={t("destinationUnit")}
            options={unitOptions}
            value={destinationUnitId}
            onChange={(e) => setDestinationUnitId(e.target.value)}
            hint={t("transferDirectionHint")}
          />
          <Textarea
            label={t("reason")}
            value={transferReason}
            onChange={(e) => setTransferReason(e.target.value)}
          />
          <Button
            type="button"
            disabled={busy || !destinationUnitId}
            onClick={() =>
              run(
                () =>
                  transferInternalComplaint(complaint.id, {
                    destinationUnitId,
                    reason: transferReason || null,
                  }),
                t("transferOk"),
              )
            }
          >
            {t("transfer")}
          </Button>
        </ModalSection>
      </Modal>

      <Modal
        open={modal === "resolve"}
        onClose={() => setModal(null)}
        title={t("resolve")}
      >
        <ModalSection className="space-y-3">
          <Input
            label={t("resolutionCode")}
            value={resolveCode}
            onChange={(e) => setResolveCode(e.target.value)}
          />
          <Input
            label={t("resolutionSummary")}
            value={resolveSummary}
            onChange={(e) => setResolveSummary(e.target.value)}
          />
          <Textarea
            label={t("comment")}
            value={resolveComment}
            onChange={(e) => setResolveComment(e.target.value)}
          />
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant="secondary"
              disabled={busy}
              onClick={() =>
                run(
                  () =>
                    resolveInternalComplaint(complaint.id, {
                      action: "PROPOSE",
                      comment: resolveComment || "propose",
                      resolutionCode: resolveCode,
                      summary: resolveSummary || "proposed",
                    }),
                  t("proposeOk"),
                )
              }
            >
              {t("propose")}
            </Button>
            <Button
              type="button"
              disabled={busy}
              onClick={() =>
                run(
                  () =>
                    resolveInternalComplaint(complaint.id, {
                      action: "ACCEPT",
                      comment: resolveComment || "accept",
                      resolutionCode: resolveCode,
                      summary: resolveSummary || "resolved",
                    }),
                  t("resolveOk"),
                )
              }
            >
              {t("resolveAccept")}
            </Button>
          </div>
        </ModalSection>
      </Modal>

      <Modal
        open={modal === "accept" || modal === "reject"}
        onClose={() => setModal(null)}
        title={modal === "reject" ? t("reject") : t("acceptance")}
      >
        <ModalSection className="space-y-3">
          <Select
            label={t("party")}
            options={[
              { value: "HANDLING_UNIT", label: t("partyHandling") },
              { value: "OWNER", label: t("partyOwner") },
            ]}
            value={acceptParty}
            onChange={(e) =>
              setAcceptParty(e.target.value as "OWNER" | "HANDLING_UNIT")
            }
          />
          <Textarea
            label={t("note")}
            value={acceptNote}
            onChange={(e) => setAcceptNote(e.target.value)}
          />
          <Button
            type="button"
            variant={modal === "reject" ? "danger" : "primary"}
            disabled={busy || (modal === "reject" && !acceptNote.trim())}
            onClick={() =>
              run(
                () =>
                  recordInternalAcceptance(complaint.id, {
                    party: acceptParty,
                    decision: modal === "reject" ? "REJECT" : "ACCEPT",
                    note: acceptNote || null,
                  }),
                modal === "reject" ? t("rejectOk") : t("acceptOk"),
              )
            }
          >
            {modal === "reject" ? t("reject") : t("confirmAccept")}
          </Button>
        </ModalSection>
      </Modal>

      <Toast
        open={Boolean(toastMessage)}
        onClose={() => setToastMessage(null)}
        title={toastMessage ?? ""}
        tone="success"
      />
    </PageContainer>
  );
}
