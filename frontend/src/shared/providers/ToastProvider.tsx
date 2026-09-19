"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useTranslations } from "next-intl";
import { ApiError, subscribeApiErrors } from "@/lib/api/client";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { Toast, type ToastTone } from "@/shared/ui/toast";

interface ToastItem {
  id: number;
  title: string;
  description?: string;
  tone: ToastTone;
}

interface ToastContextValue {
  push: (toast: Omit<ToastItem, "id">) => void;
  /** Transient success feedback — prefer over Alert tone="success". */
  pushSuccess: (title: string, description?: string) => void;
  pushError: (error: unknown, title?: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

let toastSeq = 0;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [current, setCurrent] = useState<ToastItem | null>(null);
  const t = useTranslations("common");
  const tErrors = useTranslations("errors");

  const describeError = useCallback(
    (error: unknown): { title: string; description: string } => {
      if (error instanceof ApiError) {
        return {
          title: error.status === 0 ? t("networkError") : t("requestFailed"),
          description: resolveApiErrorMessage(error, tErrors, t),
        };
      }
      if (error instanceof Error) {
        return { title: t("unexpectedError"), description: t("unexpectedErrorDescription") };
      }
      return {
        title: t("unexpectedError"),
        description: t("unexpectedErrorDescription"),
      };
    },
    [t, tErrors],
  );

  const push = useCallback((toast: Omit<ToastItem, "id">) => {
    toastSeq += 1;
    setCurrent({ ...toast, id: toastSeq });
  }, []);

  const pushSuccess = useCallback(
    (title: string, description?: string) => {
      push({ title, description, tone: "success" });
    },
    [push],
  );

  const pushError = useCallback(
    (error: unknown, title?: string) => {
      const described = describeError(error);
      push({
        title: title ?? described.title,
        description: described.description,
        tone: "danger",
      });
    },
    [push, describeError],
  );

  useEffect(() => {
    return subscribeApiErrors((error) => {
      pushError(error);
    });
  }, [pushError]);

  const value = useMemo<ToastContextValue>(
    () => ({ push, pushSuccess, pushError }),
    [push, pushSuccess, pushError],
  );

  return (
    <ToastContext.Provider value={value}>
      {children}
      <Toast
        key={current?.id ?? "empty"}
        open={Boolean(current)}
        title={current?.title ?? ""}
        description={current?.description}
        tone={current?.tone ?? "danger"}
        onClose={() => setCurrent(null)}
      />
    </ToastContext.Provider>
  );
}

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    throw new Error("useToast must be used within ToastProvider");
  }
  return ctx;
}
