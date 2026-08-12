"use client";

import { useMemo } from "react";
import { useTranslations } from "next-intl";
import {
  Alert,
  Badge,
  Card,
  CardBody,
  CardHeader,
  Timeline,
  type TimelineItem,
} from "@/shared/ui";
import {
  hasRequiredClosureHistory,
  type MockComplaint,
} from "@/features/supervisor-assign/mock/assignmentRepository";

export interface ClosureHistoryPanelProps {
  complaint: MockComplaint;
}

function formatWhen(iso: string): string {
  try {
    return new Intl.DateTimeFormat(undefined, {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    }).format(new Date(iso));
  } catch {
    return iso;
  }
}

/**
 * SCR-HX-02 — Closure record portion only (WF-001-18 for SCR-WS-12).
 * Escalation portion lives in escalation-handling EscalationHistoryPanel (R2-B3).
 */
export function ClosureHistoryPanel({ complaint }: ClosureHistoryPanelProps) {
  const t = useTranslations("reopenApproval");
  const history = useMemo(
    () => complaint.decisionHistory ?? [],
    [complaint.decisionHistory],
  );

  const closureEntries = useMemo(
    () =>
      history.filter(
        (e) =>
          e.type === "APPROVE" ||
          e.type === "REOPEN_REQUEST" ||
          e.type === "REOPEN_APPROVE" ||
          e.type === "REOPEN_REJECT",
      ),
    [history],
  );

  const items: TimelineItem[] = useMemo(
    () =>
      [...closureEntries]
        .reverse()
        .map((entry) => ({
          id: entry.id,
          title:
            entry.type === "APPROVE"
              ? t("hx.approve")
              : entry.type === "REOPEN_REQUEST"
                ? t("hx.reopenRequest")
                : entry.type === "REOPEN_APPROVE"
                  ? t("hx.reopenApprove")
                  : t("hx.reopenReject"),
          time: formatWhen(entry.at),
          actor: entry.actorName,
          status: entry.type,
          statusTone:
            entry.type === "APPROVE" || entry.type === "REOPEN_APPROVE"
              ? "success"
              : entry.type === "REOPEN_REJECT"
                ? "danger"
                : "info",
          description: entry.reason ?? complaint.resolutionSummary ?? undefined,
        })),
    [closureEntries, complaint.resolutionSummary, t],
  );

  if (!hasRequiredClosureHistory(complaint)) {
    return (
      <Card>
        <CardHeader>
          <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
            {t("hx.title")}
          </h2>
        </CardHeader>
        <CardBody>
          <Alert tone="danger" title={t("hx.missingTitle")} />
          <p className="mt-2 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
            {t("hx.missingDescription")}
          </p>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
            {t("hx.title")}
          </h2>
          <Badge tone="info" variant="soft">
            {t("hx.badge")}
          </Badge>
        </div>
        <p className="mt-1 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
          {t("hx.description")}
        </p>
      </CardHeader>
      <CardBody className="space-y-4">
        <dl className="grid gap-3 sm:grid-cols-2">
          <div>
            <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
              {t("hx.closedAt")}
            </dt>
            <dd className="text-ecmp-text-primary">
              {complaint.closedAt ? formatWhen(complaint.closedAt) : "—"}
            </dd>
          </div>
          <div>
            <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
              {t("hx.resolution")}
            </dt>
            <dd className="text-ecmp-text-primary">
              {complaint.resolutionSummary ?? "—"}
            </dd>
          </div>
        </dl>
        {items.length > 0 ? <Timeline items={items} /> : null}
      </CardBody>
    </Card>
  );
}
