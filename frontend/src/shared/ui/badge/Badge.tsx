import type { HTMLAttributes } from "react";
import { cn } from "@/shared/utils";

export type BadgeTone =
  | "neutral"
  | "primary"
  | "success"
  | "warning"
  | "danger"
  | "info";

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: BadgeTone;
}

const toneClass: Record<BadgeTone, string> = {
  neutral: "bg-ecmp-secondary-muted text-ecmp-text-primary",
  primary: "bg-ecmp-primary-muted text-ecmp-primary",
  success: "bg-ecmp-success-muted text-ecmp-success",
  warning: "bg-ecmp-warning-muted text-ecmp-warning",
  danger: "bg-ecmp-danger-muted text-ecmp-danger",
  info: "bg-ecmp-info-muted text-ecmp-info",
};

export function Badge({
  className,
  tone = "neutral",
  children,
  ...props
}: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-[var(--ecmp-radius-sm)] px-2 py-1 text-[length:var(--ecmp-font-caption-size)] font-medium tracking-wide",
        toneClass[tone],
        className,
      )}
      {...props}
    >
      {children}
    </span>
  );
}
