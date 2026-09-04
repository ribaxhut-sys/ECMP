"use client";

import { useTranslations } from "next-intl";
import type { ComplaintSla } from "@/lib/api/types";
import { Badge, type BadgeTone } from "@/shared/ui";

/**
 * DEC-031 resolution-SLA badge (30 calendar days).
 *
 * Renders only what the server computed — status, elapsed and remaining days
 * all arrive on the payload. Nothing here reads the browser clock, so a stale
 * tab cannot drift into showing a complaint as overdue before it is.
 *
 * `null` sla means "not measured": measurement is switched off, or the
 * complaint closed without a recorded closure time. Both render as nothing
 * rather than as a guess.
 */
export function ComplaintSlaBadge({
  sla,
  className,
}: {
  sla: ComplaintSla | null | undefined;
  className?: string;
}) {
  const t = useTranslations("complaints");

  if (!sla) return null;

  // Warning is a shade of ON_TRACK, not a status of its own (DEC-031 §2.6/2.7)
  // — the target has not been missed, it is merely close.
  const kind = sla.status === "ON_TRACK" && sla.isWarning ? "WARNING" : sla.status;

  const tone: Record<typeof kind, BadgeTone> = {
    ON_TRACK: "neutral",
    WARNING: "warning",
    OVERDUE: "danger",
    MET: "success",
    MISSED: "danger",
  } as Record<typeof kind, BadgeTone>;

  const label =
    kind === "OVERDUE"
      ? t("slaOverdueBadge", { days: sla.overdueDays ?? 0 })
      : kind === "WARNING"
        ? t("slaWarningBadge", { days: sla.remainingDays ?? 0 })
        : kind === "MET"
          ? t("slaMetBadge", { days: sla.elapsedDays })
          : kind === "MISSED"
            ? t("slaMissedBadge", { days: sla.elapsedDays })
            : t("slaOnTrackBadge", { days: sla.remainingDays ?? 0 });

  return (
    <Badge
      tone={tone[kind]}
      variant={kind === "OVERDUE" ? "solid" : "soft"}
      className={className}
      // The badge is short by design; the title carries the full promise so
      // "lewat batas 5 hari" is never mistaken for a 5-day target.
      title={t("slaBadgeTooltip", {
        target: sla.targetDays,
        elapsed: sla.elapsedDays,
      })}
      data-testid="complaint-sla-badge"
      data-sla-status={kind}
    >
      {label}
    </Badge>
  );
}
