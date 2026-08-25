"use client";

/**
 * API-backed hooks for Pengaduan Internal (replaces in-memory mock SoT).
 */
import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { ApiError } from "@/lib/api/client";
import {
  fetchInternalComplaint,
  fetchInternalComplaints,
  type InternalComplaint as ApiDetail,
} from "@/lib/api/internalComplaints";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import {
  mapDetailToRow,
  mapSummaryToRow,
  type InternalComplaint,
} from "../types";

/** API maximum (`pageSize` is capped at 100 server-side). */
export const INTERNAL_PAGE_SIZE = 100;
/** Safety stop for the accumulate loop — 20 × 100 rows. */
export const INTERNAL_MAX_PAGES = 20;

export interface InternalComplaintsResult {
  rows: InternalComplaint[];
  /** ``meta.totalItems`` from the API — the real population, not rows.length. */
  total: number;
  /** True when the population is larger than what was loaded (cap reached). */
  truncated: boolean;
  loading: boolean;
  error: string | null;
  reload: () => void;
}

/**
 * Every visible Pengaduan Internal for this caller, page by page.
 *
 * The list, dashboard, queues and reports all derive their numbers from this
 * array. It used to be a single ``pageSize: 100`` request, so past the 101st
 * complaint every count was quietly wrong. Pages are followed until
 * ``meta.totalItems`` is reached (or ``INTERNAL_MAX_PAGES``), and ``truncated``
 * says so out loud when the cap wins — there is no summary/aggregate endpoint
 * in the catalog to ask instead.
 */
export function useInternalComplaints(): InternalComplaintsResult {
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");
  const [rows, setRows] = useState<InternalComplaint[]>([]);
  const [total, setTotal] = useState(0);
  const [truncated, setTruncated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);

  const reload = useCallback(() => setTick((n) => n + 1), []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    async function loadAll(): Promise<void> {
      const collected: InternalComplaint[] = [];
      let reported = 0;
      let page = 1;
      for (; page <= INTERNAL_MAX_PAGES; page += 1) {
        const res = await fetchInternalComplaints({
          page,
          pageSize: INTERNAL_PAGE_SIZE,
        });
        if (cancelled) return;
        const batch = res.data ?? [];
        collected.push(...batch.map(mapSummaryToRow));
        reported = res.meta?.totalItems ?? collected.length;
        if (batch.length < INTERNAL_PAGE_SIZE || collected.length >= reported) {
          break;
        }
      }
      setRows(collected);
      setTotal(Math.max(reported, collected.length));
      setTruncated(collected.length < reported);
    }

    loadAll()
      .catch((err: unknown) => {
        if (cancelled) return;
        setError(
          err instanceof ApiError
            ? resolveApiErrorMessage(err, tErrors, tCommon)
            : tErrors("unexpectedError"),
        );
        setRows([]);
        setTotal(0);
        setTruncated(false);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [tick, tErrors, tCommon]);

  return { rows, total, truncated, loading, error, reload };
}

export function useInternalComplaint(id: string): {
  complaint: InternalComplaint | null;
  detail: ApiDetail | null;
  loading: boolean;
  error: string | null;
  reload: () => void;
} {
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");
  const [complaint, setComplaint] = useState<InternalComplaint | null>(null);
  const [detail, setDetail] = useState<ApiDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);

  const reload = useCallback(() => setTick((n) => n + 1), []);

  useEffect(() => {
    let cancelled = false;
    if (!id) {
      setComplaint(null);
      setDetail(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    fetchInternalComplaint(id)
      .then((res) => {
        if (cancelled) return;
        setDetail(res.data);
        setComplaint(mapDetailToRow(res.data));
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setError(
          err instanceof ApiError
            ? resolveApiErrorMessage(err, tErrors, tCommon)
            : tErrors("unexpectedError"),
        );
        setComplaint(null);
        setDetail(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [id, tick, tErrors, tCommon]);

  return { complaint, detail, loading, error, reload };
}
