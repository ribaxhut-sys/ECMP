"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { fetchReportByBranch } from "@/lib/api";
import type { BranchCount } from "@/lib/api/types";
import { monthDateRangeIso } from "./dashboardUtils";

type LoadState =
  | { status: "loading" }
  | { status: "success"; data: BranchCount[] }
  | { status: "error" };

/**
 * Own data source for the branch health section — independent of the
 * shared 60s dashboard poll, so picking a month/year here never refetches
 * the rest of the dashboard (and vice versa).
 */
export function useBranchHealthData() {
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());
  const [state, setState] = useState<LoadState>({ status: "loading" });
  const requestSeq = useRef(0);

  const reload = useCallback(async (targetMonth: number, targetYear: number) => {
    const id = ++requestSeq.current;
    setState({ status: "loading" });
    try {
      const { dateFrom, dateTo } = monthDateRangeIso(targetYear, targetMonth);
      const res = await fetchReportByBranch({ dateFrom, dateTo });
      if (id !== requestSeq.current) return;
      setState({ status: "success", data: res.data });
    } catch {
      if (id !== requestSeq.current) return;
      setState({ status: "error" });
    }
  }, []);

  useEffect(() => {
    void reload(month, year);
  }, [month, year, reload]);

  const retry = useCallback(() => {
    void reload(month, year);
  }, [reload, month, year]);

  return { month, setMonth, year, setYear, state, retry };
}
