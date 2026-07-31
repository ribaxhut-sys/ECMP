"use client";

import { useCallback, useRef, useState } from "react";
import { ApiError } from "@/lib/api";
import { loadReportsData, type ReportsData } from "./loadReportsData";

type LoadState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: ReportsData }
  | { status: "error"; error: string; code?: string };

export function useReportsData() {
  const [state, setState] = useState<LoadState>({ status: "idle" });
  const inFlight = useRef(false);

  const reload = useCallback(async () => {
    if (inFlight.current) return;
    inFlight.current = true;
    setState({ status: "loading" });
    try {
      const data = await loadReportsData();
      setState({ status: "success", data });
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Failed to load reports";
      const code = err instanceof ApiError ? err.code : undefined;
      setState({ status: "error", error: message, code });
    } finally {
      inFlight.current = false;
    }
  }, []);

  return { state, reload };
}
