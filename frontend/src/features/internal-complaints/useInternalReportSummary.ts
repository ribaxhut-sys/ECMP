"use client";

/**
 * Report breakdown counted server-side (API-554).
 *
 * The cards on /internal/reports used to be derived from whatever rows the
 * browser had accumulated, so past the client cap every number was quietly
 * wrong. This asks the API for the counts over the same filtered, visible
 * population instead; the caller falls back to client-side counting only when
 * this request fails.
 */
import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import {
  ApiError,
  fetchInternalComplaintsReportSummary,
  type InternalComplaintsReportFilters,
  type InternalComplaintsReportSummary,
} from "@/lib/api";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";

export interface InternalReportSummaryResult {
  summary: InternalComplaintsReportSummary | null;
  loading: boolean;
  error: string | null;
  reload: () => void;
}

export function useInternalReportSummary(
  filters: InternalComplaintsReportFilters,
): InternalReportSummaryResult {
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");
  const [summary, setSummary] = useState<InternalComplaintsReportSummary | null>(
    null,
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);

  const reload = useCallback(() => setTick((n) => n + 1), []);

  // Filters are a fresh object each render; the primitives are the real key.
  const { status, category, priority, dateFrom, dateTo, q } = filters;

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchInternalComplaintsReportSummary({
      status,
      category,
      priority,
      dateFrom,
      dateTo,
      q,
    })
      .then((res) => {
        if (cancelled) return;
        setSummary(res.data);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setSummary(null);
        setError(
          err instanceof ApiError
            ? resolveApiErrorMessage(err, tErrors, tCommon)
            : tErrors("unexpectedError"),
        );
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [status, category, priority, dateFrom, dateTo, q, tick, tErrors, tCommon]);

  return { summary, loading, error, reload };
}
