import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/shared/utils";

export interface PageContainerProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  /** Constrain content width (default true). */
  constrained?: boolean;
}

/**
 * Standard page content wrapper — consumes layout tokens for gutter / max width.
 */
export function PageContainer({
  className,
  children,
  constrained = true,
  ...props
}: PageContainerProps) {
  return (
    <div
      className={cn(
        "w-full px-[var(--ecmp-page-gutter)] py-[var(--ecmp-section-gap)] sm:px-6 lg:px-8",
        constrained && "mx-auto max-w-[var(--ecmp-content-max-width)]",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
