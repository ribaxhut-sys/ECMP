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

function SkeletonBar({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "rounded-[var(--ecmp-radius-md)] bg-ecmp-secondary-muted/80",
        "animate-pulse motion-reduce:animate-none",
        className,
      )}
    />
  );
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
        <SkeletonBar key={index} className="h-10" />
      ))}
    </div>
  );
}

export interface CardSkeletonProps extends HTMLAttributes<HTMLDivElement> {
  rows?: number;
}

/** Inline card placeholder — prefer over fullscreen spinner. */
export function CardSkeleton({
  className,
  rows = 3,
  ...props
}: CardSkeletonProps) {
  const tCommon = useTranslations("common");

  return (
    <div
      aria-busy="true"
      aria-label={tCommon("loadingContent")}
      className={cn(
        "rounded-[var(--ecmp-radius-card)] border border-ecmp-border/80 bg-ecmp-surface p-[var(--ecmp-card-padding)] shadow-ecmp-raised",
        className,
      )}
      {...props}
    >
      <SkeletonBar className="mb-4 h-5 w-1/3" />
      <SkeletonBar className="mb-3 h-4 w-2/3" />
      <div className="space-y-3 pt-2">
        {Array.from({ length: rows }).map((_, index) => (
          <SkeletonBar key={index} className="h-10" />
        ))}
      </div>
    </div>
  );
}

export interface TableSkeletonProps extends HTMLAttributes<HTMLDivElement> {
  rows?: number;
  columns?: number;
}

/** Table chrome skeleton for list loading states. */
export function TableSkeleton({
  className,
  rows = 5,
  columns = 4,
  ...props
}: TableSkeletonProps) {
  const tCommon = useTranslations("common");

  return (
    <div
      aria-busy="true"
      aria-label={tCommon("loadingContent")}
      className={cn(
        "overflow-hidden rounded-[var(--ecmp-radius-table)] border border-ecmp-border/80 bg-ecmp-surface shadow-ecmp-raised",
        className,
      )}
      {...props}
    >
      <div className="flex gap-4 border-b border-ecmp-border/80 bg-ecmp-surface-sunken px-4 py-3">
        {Array.from({ length: columns }).map((_, index) => (
          <SkeletonBar key={index} className="h-3 flex-1" />
        ))}
      </div>
      <div className="divide-y divide-ecmp-border/60">
        {Array.from({ length: rows }).map((_, rowIndex) => (
          <div key={rowIndex} className="flex gap-4 px-4 py-3.5">
            {Array.from({ length: columns }).map((_, colIndex) => (
              <SkeletonBar
                key={colIndex}
                className={cn("h-4 flex-1", colIndex === 0 && "max-w-[8rem]")}
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
