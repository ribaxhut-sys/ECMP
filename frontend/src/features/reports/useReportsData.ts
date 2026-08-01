"use client";

import { useCallback, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import { ApiError } from "@/lib/api";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { loadReportsData, type ReportsData } from "./loadReportsData";

type LoadState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: ReportsData }
  | { status: "error"; error: string; code?: string };

export function useReportsData() {
  const [state, setState] = useState<LoadState>({ status: "idle" });
  const inFlight = useRef(false);
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");

  const reload = useCallback(async () => {
    if (inFlight.current) return;
    inFlight.current = true;
    setState({ status: "loading" });
    try {
      const data = await loadReportsData();
      setState({ status: "success", data });
    } catch (err) {
      const message = resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError");
      const code = err instanceof ApiError ? err.code : undefined;
      setState({ status: "error", error: message, code });
    } finally {
      inFlight.current = false;
    }
  }, [tCommon, tErrors]);

  return { state, reload };
}
