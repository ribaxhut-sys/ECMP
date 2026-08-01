"use client";

import { useCallback, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import { ApiError } from "@/lib/api";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import {
  loadDashboardData,
  type DashboardData,
} from "./loadDashboardData";

type LoadState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: DashboardData }
  | { status: "error"; error: string; code?: string };

export function useDashboardData() {
  const [state, setState] = useState<LoadState>({ status: "idle" });
  const inFlight = useRef(false);
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");
  const tDashboard = useTranslations("dashboard");

  const reload = useCallback(async () => {
    if (inFlight.current) return;
    inFlight.current = true;
    setState({ status: "loading" });
    try {
      const data = await loadDashboardData();
      setState({ status: "success", data });
    } catch (err) {
      const message = resolveApiErrorMessage(
        err,
        tErrors,
        tCommon,
        "unexpectedError",
      );
      const code = err instanceof ApiError ? err.code : undefined;
      setState({
        status: "error",
        error: message || tDashboard("unableToLoad"),
        code,
      });
    } finally {
      inFlight.current = false;
    }
  }, [tCommon, tDashboard, tErrors]);

  return { state, reload };
}
