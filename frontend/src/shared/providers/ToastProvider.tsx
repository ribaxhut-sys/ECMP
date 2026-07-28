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
import { Toast, type ToastTone } from "@/shared/ui/toast";

interface ToastItem {
  id: number;
  title: string;
  description?: string;
  tone: ToastTone;
}

interface ToastContextValue {
  push: (toast: Omit<ToastItem, "id">) => void;
  pushError: (error: unknown, title?: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

let toastSeq = 0;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [current, setCurrent] = useState<ToastItem | null>(null);
  const t = useTranslations("common");

  const describeError = useCallback(
    (error: unknown): { title: string; description: string } => {
      if (error instanceof ApiError) {
        if (error.status === 0) {
          return {
            title: t("networkError"),
            description: error.message || t("networkErrorDescription"),
          };
        }
        return {
          title: t("requestFailed"),
          description: error.message || t("httpError", { status: error.status }),
        };
      }
      if (error instanceof Error) {
        return { title: t("unexpectedError"), description: error.message };
      }
      return {
        title: t("unexpectedError"),
        description: t("unexpectedErrorDescription"),
      };
    },
    [t],
  );

  const push = useCallback((toast: Omit<ToastItem, "id">) => {
    toastSeq += 1;
    setCurrent({ ...toast, id: toastSeq });
  }, []);

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
    () => ({ push, pushError }),
    [push, pushError],
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
