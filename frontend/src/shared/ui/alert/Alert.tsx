import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/shared/utils";
import { IconAlert, IconCheck, IconClose } from "@/shared/icons";
import { Button } from "@/shared/ui/button";

/**
 * Persistent inline feedback (validation, permission, business warning, errors).
 * Compact banner — not a card. Do not use tone="success" for action success —
 * use useToast().pushSuccess instead.
 */
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
    return <IconCheck className="mt-px !size-4 shrink-0" aria-hidden />;
  }
  return <IconAlert className="mt-px !size-4 shrink-0" aria-hidden />;
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
  const hasBody =
    Boolean(description) || Boolean(actions) || Boolean(actionLabel && onAction);

  return (
    <div
      role="alert"
      className={cn(
        "rounded-[var(--ecmp-radius-md)] border px-3 py-2",
        toneClass[tone],
        className,
      )}
      {...props}
    >
      <div className={cn("flex gap-2", hasBody ? "items-start" : "items-center")}>
        {icon ?? <DefaultIcon tone={tone} />}
        <div className="min-w-0 flex-1">
          <p className="text-[length:var(--ecmp-font-label-size)] font-[number:var(--ecmp-font-label-weight)] leading-[var(--ecmp-font-label-line)] text-ecmp-text-primary">
            {title}
          </p>
          {description ? (
            <div className="mt-0.5 text-[length:var(--ecmp-font-helper-size)] leading-[var(--ecmp-font-helper-line)] text-ecmp-text-primary/90">
              {description}
            </div>
          ) : null}
          {actions || (actionLabel && onAction) ? (
            <div className="mt-2 flex flex-wrap items-center gap-2">
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
            className="!min-h-8 !min-w-8 shrink-0 !px-0"
          >
            <IconClose className="!size-3.5" />
          </Button>
        ) : null}
      </div>
    </div>
  );
}
