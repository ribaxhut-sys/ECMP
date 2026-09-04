import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import {
  ApiError,
  fetchCmCaseHistory,
  type CmCaseHistoryEntry,
} from "@/lib/api";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";

export function useCmCaseHistory(
  caseId: string,
  refreshKey?: string | null,
): {
  entries: CmCaseHistoryEntry[];
  loading: boolean;
  error: string | null;
} {
  const t = useTranslations("cases");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const [entries, setEntries] = useState<CmCaseHistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    const id = caseId.trim();
    if (!id) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetchCmCaseHistory(id);
      setEntries(res.data ?? []);
    } catch (err) {
      setEntries([]);
      setError(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : t("historyUnavailable"),
      );
    } finally {
      setLoading(false);
    }
  }, [caseId, t, tCommon, tErrors]);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  return { entries, loading, error };
}
