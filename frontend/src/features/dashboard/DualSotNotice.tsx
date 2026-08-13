"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { DASHBOARD_CAPTION, DASHBOARD_SURFACE_QUIET } from "./dashboardUtils";

/**
 * DEC-025: complaint KPI numbers prefer Aggregate; Foundation charts remain
 * until a Retirement DEC. The list link is the CM door (`/complaints`).
 */
export function DualSotNotice({
  complaintKpiSource,
}: {
  complaintKpiSource: "aggregate" | "foundation" | null;
}) {
  const t = useTranslations("dashboard");
  const { hasPermission } = useAuth();
  const fromAggregate = complaintKpiSource === "aggregate";
  const canOpenComplaintList =
    hasPermission("complaints:read") || hasPermission("*");

  return (
    <aside
      data-testid="dashboard-dual-sot-notice"
      aria-label={t("dualSotNoticeLabel")}
      className={`${DASHBOARD_SURFACE_QUIET} px-4 py-2.5`}
    >
      <p className={DASHBOARD_CAPTION}>
        <span className="font-medium text-ecmp-text-primary">
          {fromAggregate
            ? t("dualSotKpiAggregateTitle")
            : t("dualSotNoticeTitle")}
        </span>{" "}
        {fromAggregate
          ? t("dualSotKpiAggregateBody")
          : t("dualSotNoticeBody")}
        {canOpenComplaintList ? (
          <>
            {" "}
            <Link
              href="/complaints"
              className="font-medium text-ecmp-primary underline-offset-2 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus"
            >
              {t("dualSotNoticeLink")}
            </Link>
          </>
        ) : null}
      </p>
    </aside>
  );
}
