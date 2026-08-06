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
  hasRequiredEscalationHistory,
  type MockComplaint,
  type MockDecisionHistoryType,
} from "@/features/supervisor-assign/mock/assignmentRepository";

export interface EscalationHistoryPanelProps {
  complaint: MockComplaint;
}

function formatWhen(iso: string): string {
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(iso));
  } catch {
    return iso;
  }
}

const ESCALATION_TYPES: ReadonlySet<MockDecisionHistoryType> = new Set([
  "ESCALATION_OPEN",
  "ESCALATION_CONTEXT_REQUEST",
  "ESCALATION_CONTEXT_PROVIDED",
  "ESCALATION_HANDLE",
  "ESCALATION_FORWARD",
  "PROGRESS",
]);

/**
 * SCR-HX-02 — Escalation context portion (WF-001-18 for SCR-WS-11).
 * Closure segment remains in reopen-approval ClosureHistoryPanel.
 */
export function EscalationHistoryPanel({
  complaint,
}: EscalationHistoryPanelProps) {
  const t = useTranslations("escalationHandling");
  const history = useMemo(
    () => complaint.decisionHistory ?? [],
    [complaint.decisionHistory],
  );

  const escalationEntries = useMemo(
    () => history.filter((e) => ESCALATION_TYPES.has(e.type)),
    [history],
  );

  const items: TimelineItem[] = useMemo(
    () =>
      [...escalationEntries].reverse().map((entry) => ({
        id: entry.id,
        title:
          entry.type === "ESCALATION_OPEN"
            ? t("hx.open")
            : entry.type === "ESCALATION_CONTEXT_REQUEST"
              ? t("hx.contextRequest")
              : entry.type === "ESCALATION_CONTEXT_PROVIDED"
                ? t("hx.contextProvided")
                : entry.type === "ESCALATION_HANDLE"
                  ? t("hx.handle")
                  : entry.type === "ESCALATION_FORWARD"
                    ? t("hx.forward")
                    : t("hx.progress"),
        time: formatWhen(entry.at),
        actor: entry.actorName,
        status: entry.type,
        statusTone:
          entry.type === "ESCALATION_HANDLE"
            ? "success"
            : entry.type === "ESCALATION_FORWARD"
              ? "warning"
              : entry.type === "ESCALATION_CONTEXT_PROVIDED"
                ? "success"
                : "info",
        description: entry.reason,
      })),
    [escalationEntries, t],
  );

  if (!hasRequiredEscalationHistory(complaint)) {
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
              {t("hx.escalationReason")}
            </dt>
            <dd className="text-ecmp-text-primary">
              {complaint.escalationNote ?? "—"}
            </dd>
          </div>
          <div>
            <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
              {t("hx.officerContext")}
            </dt>
            <dd className="text-ecmp-text-primary">
              {complaint.escalationContextPackage ?? t("hx.officerContextEmpty")}
            </dd>
          </div>
        </dl>
        {complaint.progressNotes.length > 0 ? (
          <div>
            <p className="mb-2 text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
              {t("hx.progressSummary")}
            </p>
            <ul className="space-y-1 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-primary">
              {complaint.progressNotes.map((note) => (
                <li key={note.id}>• {note.text}</li>
              ))}
            </ul>
          </div>
        ) : null}
        {items.length > 0 ? <Timeline items={items} /> : null}
      </CardBody>
    </Card>
  );
}
