import type { HTMLAttributes } from "react";
import { cn } from "@/shared/utils";
import { IconSpinner } from "@/shared/icons";

export interface LoadingProps extends HTMLAttributes<HTMLDivElement> {
  label?: string;
}

export function Loading({
  className,
  label = "Loading",
  ...props
}: LoadingProps) {
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
      <IconSpinner className="size-5" />
      <span className="text-[length:var(--ecmp-font-body-size)]">{label}</span>
    </div>
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
  return (
    <div
      aria-busy="true"
      aria-label="Loading content"
      className={cn("space-y-3", className)}
      {...props}
    >
      {Array.from({ length: rows }).map((_, index) => (
        <div
          key={index}
          className="h-10 animate-pulse rounded-[var(--ecmp-radius-md)] bg-ecmp-secondary-muted"
        />
      ))}
    </div>
  );
}
