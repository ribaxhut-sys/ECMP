"use client";

import { useCallback, useEffect, useRef, useState } from "react";
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

const AUTO_REFRESH_MS = 60_000;

export function useDashboardData() {
  const [state, setState] = useState<LoadState>({ status: "idle" });
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);
  const [isFetching, setIsFetching] = useState(false);
  const inFlight = useRef(false);
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");
  const tDashboard = useTranslations("dashboard");

  const reload = useCallback(async () => {
    if (inFlight.current) return;
    inFlight.current = true;
    setIsFetching(true);
    // Only show the first-load skeleton before any data has ever landed —
    // background/manual refresh keeps the current data visible.
    setState((prev) => (prev.status === "success" ? prev : { status: "loading" }));
    try {
      const data = await loadDashboardData();
      setState({ status: "success", data });
      setUpdatedAt(new Date());
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
      setIsFetching(false);
    }
  }, [tCommon, tDashboard, tErrors]);

  // Silent background refresh — paused while the tab is not visible so we
  // never poll a screen nobody is looking at.
  useEffect(() => {
    const id = window.setInterval(() => {
      if (document.visibilityState !== "visible") return;
      void reload();
    }, AUTO_REFRESH_MS);
    return () => window.clearInterval(id);
  }, [reload]);

  return { state, reload, updatedAt, isFetching };
}
