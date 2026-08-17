"use client";

import { useMemo, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { formatShortDateTime24 } from "@/shared/utils/datetime";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  CardHeader,
  Timeline,
  type TimelineItem,
} from "@/shared/ui";
import type {
  MockComplaint,
  MockDecisionHistoryEntry,
} from "@/features/supervisor-assign/mock/assignmentRepository";

export interface DecisionHistoryPanelProps {
  complaint: MockComplaint;
  /** Soft-gate: user expanded/acknowledged reject reason before resubmit. */
  onRejectAcknowledged?: () => void;
  rejectAcknowledged?: boolean;
  /**
   * Embedded context:
   * - reject (SCR-WS-06): soft-gate reject acknowledge
   * - reopen (SCR-WS-07): continuation history without reject soft-gate
   */
  variant?: "reject" | "reopen";
}


/**
 * SCR-HX-01 — Decision History (Officer), embedded portion for WF-001-09.
 * Shows reject reason + reviewer + time; read-only; no primary decision.
 */
export function DecisionHistoryPanel({
  complaint,
  onRejectAcknowledged,
  rejectAcknowledged = false,
  variant = "reject",
}: DecisionHistoryPanelProps) {
  const t = useTranslations("rejectedResubmission");
  const locale = useLocale();
  const history = useMemo(
    () => complaint.decisionHistory ?? [],
    [complaint.decisionHistory],
  );
  const [expandedId, setExpandedId] = useState<string | null>(() => {
    const latestReject = [...(complaint.decisionHistory ?? [])]
      .reverse()
      .find((e) => e.type === "REJECT");
    return latestReject?.id ?? null;
  });

  const items: TimelineItem[] = useMemo(
    () =>
      [...history]
        .slice()
        .reverse()
        .map((entry) => toTimelineItem(entry, t, locale, expandedId === entry.id)),
    [history, t, locale, expandedId],
  );

  if (history.length === 0) {
    return (
      <Card>
        <CardHeader>
          <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
            {t("historyTitle")}
          </h2>
        </CardHeader>
        <CardBody>
          <Alert tone="danger" title={t("historyMissingTitle")} />
          <p className="mt-2 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
            {t("historyMissingDescription")}
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
            {t("historyTitle")}
          </h2>
          <Badge tone="warning" variant="soft">
            {t("historyBadge")}
          </Badge>
        </div>
        <p className="mt-1 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
          {variant === "reopen"
            ? t("historyDescriptionReopen")
            : t("historyDescription")}
        </p>
      </CardHeader>
      <CardBody className="space-y-4">
        <Timeline items={items} />
        {variant === "reject" ? (
          <>
            <div className="flex flex-wrap gap-2">
              {history
                .filter((e) => e.type === "REJECT")
                .map((entry) => (
                  <Button
                    key={entry.id}
                    type="button"
                    size="sm"
                    variant={expandedId === entry.id ? "primary" : "outline"}
                    onClick={() => {
                      setExpandedId(entry.id);
                      onRejectAcknowledged?.();
                    }}
                  >
                    {t("expandReject")}
                  </Button>
                ))}
            </div>
            {rejectAcknowledged ? (
              <Alert tone="success" title={t("rejectAcknowledged")} />
            ) : (
              <Alert tone="info" title={t("rejectAcknowledgeHint")} />
            )}
          </>
        ) : null}
      </CardBody>
    </Card>
  );
}

function toTimelineItem(
  entry: MockDecisionHistoryEntry,
  t: ReturnType<typeof useTranslations>,
  locale: string,
  expanded: boolean,
): TimelineItem {
  const titleKey =
    entry.type === "REJECT"
      ? "historyType.reject"
      : entry.type === "SUBMIT"
        ? "historyType.submit"
        : entry.type === "APPROVE"
          ? "historyType.approve"
          : entry.type === "REOPEN_REQUEST"
            ? "historyType.reopenRequest"
            : entry.type === "REOPEN_APPROVE"
              ? "historyType.reopenApprove"
              : entry.type === "REOPEN_REJECT"
                ? "historyType.reopenReject"
                : "historyType.progress";

  const description =
    entry.type === "REJECT"
      ? expanded
        ? entry.reason ?? t("historyNoReason")
        : t("historyRejectCollapsed")
      : entry.reason;

  return {
    id: entry.id,
    title: t(titleKey),
    time: formatShortDateTime24(entry.at, locale),
    actor: entry.actorName,
    status: entry.type,
    statusTone:
      entry.type === "REJECT" || entry.type === "REOPEN_REJECT"
        ? "danger"
        : entry.type === "APPROVE" || entry.type === "REOPEN_APPROVE"
          ? "success"
          : "info",
    description,
  };
}
