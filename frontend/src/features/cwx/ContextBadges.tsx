"use client";

import { useTranslations } from "next-intl";
import { Badge, type BadgeTone } from "@/shared/ui";
import type { DerivedBadge } from "./deriveOperationalContext";

const MAX_VISIBLE = 4;

function badgeTone(kind: DerivedBadge["kind"]): BadgeTone {
  switch (kind) {
    case "critical_sla":
    case "escalated":
      return "danger";
    case "high_priority":
    case "waiting_customer":
      return "warning";
    default:
      return "neutral";
  }
}

function badgeLabelKey(kind: DerivedBadge["kind"]): string {
  switch (kind) {
    case "high_priority":
      return "badgeHighPriority";
    case "critical_sla":
      return "badgeCriticalSla";
    case "escalated":
      return "badgeEscalated";
    case "waiting_customer":
      return "badgeWaitingCustomer";
  }
}

export type CwxContextBadgesProps = {
  badges: readonly DerivedBadge[];
};

/**
 * CWX-M2 Context Badges — max 4 visible + overflow. No invented kinds.
 */
export function CwxContextBadges({ badges }: CwxContextBadgesProps) {
  const t = useTranslations("cwx");
  if (badges.length === 0) return null;

  const visible = badges.slice(0, MAX_VISIBLE);
  const overflow = badges.length - visible.length;

  return (
    <div
      data-testid="cwx-context-badges"
      className="flex min-w-0 flex-wrap items-center gap-1.5"
      aria-label={t("badgesLabel")}
    >
      {visible.map((badge) => (
        <Badge key={badge.kind} tone={badgeTone(badge.kind)} variant="soft">
          {t(badgeLabelKey(badge.kind))}
        </Badge>
      ))}
      {overflow > 0 ? (
        <Badge tone="neutral" variant="soft">
          {t("badgeOverflow", { count: overflow })}
        </Badge>
      ) : null}
    </div>
  );
}
