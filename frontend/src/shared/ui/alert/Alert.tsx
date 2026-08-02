import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/shared/utils";
import { IconAlert, IconCheck, IconClose } from "@/shared/icons";
import { Button } from "@/shared/ui/button";

export type AlertTone = "info" | "success" | "warning" | "danger";

export interface AlertProps extends HTMLAttributes<HTMLDivElement> {
  tone?: AlertTone;
  title: string;
  description?: ReactNode;
  actionLabel?: string;
  onAction?: () => void;
  /** Optional dismiss handler — renders a close control when provided. */
  onDismiss?: () => void;
  dismissLabel?: string;
  icon?: ReactNode;
  actions?: ReactNode;
}

const toneClass: Record<AlertTone, string> = {
  info: "border-ecmp-info-border bg-ecmp-info-bg text-ecmp-info-text",
  success: "border-ecmp-success-border bg-ecmp-success-bg text-ecmp-success-text",
  warning: "border-ecmp-warning-border bg-ecmp-warning-bg text-ecmp-warning-text",
  danger: "border-ecmp-danger-border bg-ecmp-danger-bg text-ecmp-danger-text",
};

function DefaultIcon({ tone }: { tone: AlertTone }) {
  if (tone === "success") {
    return <IconCheck className="mt-0.5 size-5 shrink-0" aria-hidden />;
  }
  return <IconAlert className="mt-0.5 size-5 shrink-0" aria-hidden />;
}

export function Alert({
  className,
  tone = "info",
  title,
  description,
  actionLabel,
  onAction,
  onDismiss,
  dismissLabel = "Dismiss",
  icon,
  actions,
  ...props
}: AlertProps) {
  return (
    <div
      role="alert"
      className={cn(
        "rounded-[var(--ecmp-radius-lg)] border px-4 py-4 shadow-ecmp-surface",
        toneClass[tone],
        className,
      )}
      {...props}
    >
      <div className="flex gap-3">
        {icon ?? <DefaultIcon tone={tone} />}
        <div className="min-w-0 flex-1">
          <p className="text-[length:var(--ecmp-font-card-title-size)] font-[number:var(--ecmp-font-card-title-weight)] text-ecmp-text-primary">
            {title}
          </p>
          {description ? (
            <div className="mt-1 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-primary/90">
              {description}
            </div>
          ) : null}
          {actions || (actionLabel && onAction) ? (
            <div className="mt-3 flex flex-wrap items-center gap-2">
              {actions}
              {actionLabel && onAction ? (
                <Button variant="outline" size="sm" onClick={onAction}>
                  {actionLabel}
                </Button>
              ) : null}
            </div>
          ) : null}
        </div>
        {onDismiss ? (
          <Button
            variant="ghost"
            size="sm"
            aria-label={dismissLabel}
            onClick={onDismiss}
            className="!min-h-9 !min-w-9 shrink-0 !px-0"
          >
            <IconClose className="size-4" />
          </Button>
        ) : null}
      </div>
    </div>
  );
}
