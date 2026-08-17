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

export function useInternalComplaints(): {
  rows: InternalComplaint[];
  loading: boolean;
  error: string | null;
  reload: () => void;
} {
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");
  const [rows, setRows] = useState<InternalComplaint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);

  const reload = useCallback(() => setTick((n) => n + 1), []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchInternalComplaints({ page: 1, pageSize: 100 })
      .then((res) => {
        if (cancelled) return;
        setRows((res.data ?? []).map(mapSummaryToRow));
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setError(
          err instanceof ApiError
            ? resolveApiErrorMessage(err, tErrors, tCommon)
            : tErrors("unexpectedError"),
        );
        setRows([]);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [tick, tErrors, tCommon]);

  return { rows, loading, error, reload };
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
