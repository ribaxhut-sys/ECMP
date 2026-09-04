"use client";

import { useCallback, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import { ApiError } from "@/lib/api";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { loadReportsData, type ReportsData } from "./loadReportsData";
import {
  DEFAULT_REPORT_PERIOD,
  previousReportPeriodRange,
  reportPeriodRange,
  type ReportPeriodKey,
} from "./reportPeriods";

type LoadState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: ReportsData }
  | { status: "error"; error: string; code?: string };

export function useReportsData() {
  const [state, setState] = useState<LoadState>({ status: "idle" });
  const [period, setPeriod] = useState<ReportPeriodKey>(DEFAULT_REPORT_PERIOD);
  /** Only the newest request may write state — an older one landing late
   * would show numbers from a period the user no longer has selected. */
  const requestId = useRef(0);
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");

  const reload = useCallback(async (selected: ReportPeriodKey, branchId?: string) => {
    const id = ++requestId.current;
    setState({ status: "loading" });
    try {
      const data = await loadReportsData(
        reportPeriodRange(selected),
        branchId,
        previousReportPeriodRange(selected),
      );
      if (id !== requestId.current) return;
      setState({ status: "success", data });
    } catch (err) {
      if (id !== requestId.current) return;
      const message = resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError");
      const code = err instanceof ApiError ? err.code : undefined;
      setState({ status: "error", error: message, code });
    }
  }, [tCommon, tErrors]);

  return { state, reload, period, setPeriod };
}
