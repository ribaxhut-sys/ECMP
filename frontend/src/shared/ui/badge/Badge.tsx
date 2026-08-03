import type { HTMLAttributes } from "react";
import { cn } from "@/shared/utils";

export type BadgeTone =
  | "neutral"
  | "primary"
  | "success"
  | "warning"
  | "danger"
  | "info";

export type BadgeVariant = "soft" | "solid" | "outline";

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: BadgeTone;
  variant?: BadgeVariant;
}

const softTone: Record<BadgeTone, string> = {
  neutral: "bg-ecmp-secondary-muted text-ecmp-text-primary",
  primary: "bg-ecmp-primary-muted text-ecmp-primary",
  success: "bg-ecmp-success-bg text-ecmp-success-text",
  warning: "bg-ecmp-warning-bg text-ecmp-warning-text",
  danger: "bg-ecmp-danger-bg text-ecmp-danger-text",
  info: "bg-ecmp-info-bg text-ecmp-info-text",
};

const solidTone: Record<BadgeTone, string> = {
  neutral: "bg-ecmp-secondary text-ecmp-secondary-foreground",
  primary: "bg-ecmp-primary text-ecmp-primary-foreground",
  success: "bg-ecmp-success text-ecmp-success-foreground",
  warning: "bg-ecmp-warning text-ecmp-warning-foreground",
  danger: "bg-ecmp-danger text-ecmp-danger-foreground",
  info: "bg-ecmp-info text-ecmp-info-foreground",
};

const outlineTone: Record<BadgeTone, string> = {
  neutral: "border-ecmp-border bg-transparent text-ecmp-text-secondary",
  primary: "border-ecmp-primary bg-transparent text-ecmp-primary",
  success: "border-ecmp-success-border bg-ecmp-success-subtle text-ecmp-success-text",
  warning: "border-ecmp-warning-border bg-ecmp-warning-subtle text-ecmp-warning-text",
  danger: "border-ecmp-danger-border bg-ecmp-danger-subtle text-ecmp-danger-text",
  info: "border-ecmp-info-border bg-ecmp-info-subtle text-ecmp-info-text",
};

export function Badge({
  className,
  tone = "neutral",
  variant = "soft",
  children,
  ...props
}: BadgeProps) {
  const toneClass =
    variant === "solid"
      ? solidTone[tone]
      : variant === "outline"
        ? outlineTone[tone]
        : softTone[tone];

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-[var(--ecmp-radius-badge)] px-2 py-0.5",
        "text-[length:var(--ecmp-font-caption-size)] font-medium tracking-wide",
        variant === "outline" && "border",
        toneClass,
        className,
      )}
      {...props}
    >
      {children}
    </span>
  );
}
