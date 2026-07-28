"use client";

import { useEffect, type HTMLAttributes, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { useTranslations } from "next-intl";
import { cn } from "@/shared/utils";
import { IconCheck, IconClose } from "@/shared/icons";
import { Button } from "@/shared/ui/button";

export type ToastTone = "success" | "info" | "warning" | "danger";

export interface ToastProps extends HTMLAttributes<HTMLDivElement> {
  open: boolean;
  title: string;
  description?: ReactNode;
  tone?: ToastTone;
  /** Auto-dismiss delay in ms. Set 0 to disable. Default 4500. */
  durationMs?: number;
  onClose: () => void;
}

const toneClass: Record<ToastTone, string> = {
  success: "border-ecmp-success bg-ecmp-success-muted text-ecmp-success",
  info: "border-ecmp-info bg-ecmp-info-muted text-ecmp-info",
  warning: "border-ecmp-warning bg-ecmp-warning-muted text-ecmp-warning",
  danger: "border-ecmp-danger bg-ecmp-danger-muted text-ecmp-danger",
};

/**
 * Transient notification. Mount near page root; portals to document.body.
 * Prefer for success feedback; use Alert for persistent form errors.
 */
export function Toast({
  open,
  title,
  description,
  tone = "success",
  durationMs = 4500,
  onClose,
  className,
  ...props
}: ToastProps) {
  const t = useTranslations("common");

  useEffect(() => {
    if (!open || durationMs <= 0) return;
    const timer = window.setTimeout(onClose, durationMs);
    return () => window.clearTimeout(timer);
  }, [open, durationMs, onClose]);

  if (!open || typeof document === "undefined") return null;

  return createPortal(
    <div
      className="pointer-events-none fixed inset-x-0 top-0 z-[60] flex justify-center p-4 sm:justify-end"
      aria-live="polite"
      aria-relevant="additions"
    >
      <div
        role="status"
        className={cn(
          "pointer-events-auto flex w-full max-w-md gap-3 rounded-[var(--ecmp-radius-lg)] border px-4 py-3 shadow-ecmp-md",
          toneClass[tone],
          className,
        )}
        {...props}
      >
        {tone === "success" ? (
          <IconCheck className="mt-0.5 size-5 shrink-0" title={t("success")} />
        ) : null}
        <div className="min-w-0 flex-1">
          <p className="text-[length:var(--ecmp-font-subtitle-size)] font-semibold text-ecmp-text-primary">
            {title}
          </p>
          {description ? (
            <div className="mt-1 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary/90">
              {description}
            </div>
          ) : null}
        </div>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          aria-label={t("dismissNotification")}
          onClick={onClose}
          className="!min-h-[44px] !min-w-[44px] shrink-0 px-2"
        >
          <IconClose className="size-4" />
        </Button>
      </div>
    </div>,
    document.body,
  );
}
