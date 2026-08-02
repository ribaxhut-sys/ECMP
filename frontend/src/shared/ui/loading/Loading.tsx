"use client";

import type { HTMLAttributes } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/shared/utils";
import { IconSpinner } from "@/shared/icons";

export interface LoadingProps extends HTMLAttributes<HTMLDivElement> {
  label?: string;
}

export function Loading({ className, label, ...props }: LoadingProps) {
  const tCommon = useTranslations("common");

  return (
    <div
      role="status"
      aria-live="polite"
      aria-busy="true"
      className={cn(
        "flex items-center justify-center gap-3 py-8 text-ecmp-text-secondary",
        className,
      )}
      {...props}
    >
      <Spinner />
      <span className="text-[length:var(--ecmp-font-body-size)]">
        {label ?? tCommon("loading")}
      </span>
    </div>
  );
}

export interface SpinnerProps extends HTMLAttributes<HTMLSpanElement> {
  size?: "sm" | "md" | "lg";
}

const spinnerSize: Record<NonNullable<SpinnerProps["size"]>, string> = {
  sm: "size-4",
  md: "size-5",
  lg: "size-6",
};

/** Standalone spinner consuming motion tokens via IconSpinner + reduced-motion CSS. */
export function Spinner({ className, size = "md", ...props }: SpinnerProps) {
  return (
    <span
      role="status"
      aria-hidden={props["aria-label"] ? undefined : true}
      className={cn("inline-flex", className)}
      {...props}
    >
      <IconSpinner className={spinnerSize[size]} />
    </span>
  );
}

export interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  rows?: number;
}

export function Skeleton({
  className,
  rows = 3,
  ...props
}: SkeletonProps) {
  const tCommon = useTranslations("common");

  return (
    <div
      aria-busy="true"
      aria-label={tCommon("loadingContent")}
      className={cn("space-y-[var(--ecmp-space-12)]", className)}
      {...props}
    >
      {Array.from({ length: rows }).map((_, index) => (
        <div
          key={index}
          className={cn(
            "h-10 rounded-[var(--ecmp-radius-md)] bg-ecmp-secondary-muted",
            "animate-pulse motion-reduce:animate-none",
          )}
        />
      ))}
    </div>
  );
}
