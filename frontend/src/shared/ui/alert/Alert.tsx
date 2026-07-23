import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/shared/utils";
import { IconAlert } from "@/shared/icons";
import { Button } from "@/shared/ui/button";

export type AlertTone = "info" | "success" | "warning" | "danger";

export interface AlertProps extends HTMLAttributes<HTMLDivElement> {
  tone?: AlertTone;
  title: string;
  description?: ReactNode;
  actionLabel?: string;
  onAction?: () => void;
}

const toneClass: Record<AlertTone, string> = {
  info: "border-ecmp-info bg-ecmp-info-muted text-ecmp-info",
  success: "border-ecmp-success bg-ecmp-success-muted text-ecmp-success",
  warning: "border-ecmp-warning bg-ecmp-warning-muted text-ecmp-warning",
  danger: "border-ecmp-danger bg-ecmp-danger-muted text-ecmp-danger",
};

export function Alert({
  className,
  tone = "info",
  title,
  description,
  actionLabel,
  onAction,
  ...props
}: AlertProps) {
  return (
    <div
      role="alert"
      className={cn(
        "rounded-[var(--ecmp-radius-lg)] border px-4 py-4",
        toneClass[tone],
        className,
      )}
      {...props}
    >
      <div className="flex gap-3">
        <IconAlert className="mt-0.5 size-5 shrink-0" />
        <div className="min-w-0 flex-1">
          <p className="text-[length:var(--ecmp-font-subtitle-size)] font-semibold text-ecmp-text-primary">
            {title}
          </p>
          {description ? (
            <div className="mt-1 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary/90">
              {description}
            </div>
          ) : null}
          {actionLabel && onAction ? (
            <div className="mt-3">
              <Button variant="outline" size="sm" onClick={onAction}>
                {actionLabel}
              </Button>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
