"use client";

import type { HTMLAttributes, ReactNode } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/shared/utils";
import { IconEmpty } from "@/shared/icons";
import { Button, type ButtonVariant } from "@/shared/ui/button";

export type EmptyActionConfig = {
  label: string;
  onClick?: () => void;
  disabled?: boolean;
  title?: string;
  variant?: ButtonVariant;
};

export interface EmptyProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  description: string;
  /** @deprecated Prefer primaryAction */
  action?: ReactNode | EmptyActionConfig;
  /** Primary CTA — required for standardized empty states. */
  primaryAction?: ReactNode | EmptyActionConfig;
  secondaryAction?: ReactNode | EmptyActionConfig;
  icon?: ReactNode;
}

function isActionConfig(
  value: ReactNode | EmptyActionConfig | undefined,
): value is EmptyActionConfig {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value) &&
    !("$$typeof" in value) &&
    "label" in value &&
    typeof (value as EmptyActionConfig).label === "string"
  );
}

function renderAction(
  value: ReactNode | EmptyActionConfig | undefined,
  fallbackVariant: ButtonVariant,
): ReactNode {
  if (!value) return null;
  if (isActionConfig(value)) {
    return (
      <Button
        type="button"
        size="md"
        variant={value.variant ?? fallbackVariant}
        disabled={value.disabled}
        title={value.title}
        onClick={value.onClick}
      >
        {value.label}
      </Button>
    );
  }
  return value;
}

function EmptyIllustration() {
  return (
    <div
      aria-hidden
      className={cn(
        "relative flex size-16 items-center justify-center overflow-hidden rounded-[var(--ecmp-radius-xl)]",
        "border border-ecmp-border/70 bg-gradient-to-br from-ecmp-surface via-ecmp-surface-sunken to-ecmp-primary-muted/40",
        "shadow-ecmp-raised",
      )}
    >
      <span className="absolute inset-x-3 top-3 h-1.5 rounded-full bg-ecmp-border/80" />
      <span className="absolute inset-x-3 top-6 h-1.5 w-1/2 rounded-full bg-ecmp-border/50" />
      <IconEmpty className="relative size-6 text-ecmp-muted" />
    </div>
  );
}

export function Empty({
  className,
  title,
  description,
  action,
  primaryAction,
  secondaryAction,
  icon,
  ...props
}: EmptyProps) {
  const tCommon = useTranslations("common");
  const primary = renderAction(primaryAction ?? action, "primary");
  const secondary = renderAction(secondaryAction, "outline");

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-[var(--ecmp-radius-card)]",
        "border border-dashed border-ecmp-border/80 bg-ecmp-surface-sunken/60",
        "px-6 py-14 text-center",
        className,
      )}
      {...props}
    >
      {icon ?? <EmptyIllustration />}
      <p className="mt-5 text-[length:var(--ecmp-font-card-title-size)] font-[number:var(--ecmp-font-card-title-weight)] tracking-tight text-ecmp-text-primary">
        {title ?? tCommon("emptyTitle")}
      </p>
      <p className="mt-2 max-w-md text-[length:var(--ecmp-font-body-small-size)] leading-relaxed text-ecmp-text-secondary">
        {description}
      </p>
      {primary || secondary ? (
        <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
          {primary}
          {secondary}
        </div>
      ) : null}
    </div>
  );
}
