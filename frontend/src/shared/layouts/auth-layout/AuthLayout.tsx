import type { ReactNode } from "react";
import { cn } from "@/shared/utils";

export interface AuthLayoutProps {
  children: ReactNode;
  className?: string;
}

/**
 * Centered auth shell for login / session screens.
 * Provides enterprise background layering; pages supply their own Card content.
 * No illustrations. No heavy gradients.
 */
export function AuthLayout({ children, className }: AuthLayoutProps) {
  return (
    <div
      className={cn(
        "relative flex min-h-screen w-full items-center justify-center overflow-x-hidden",
        "bg-ecmp-background px-[var(--ecmp-page-gutter)] py-[var(--ecmp-section-gap)]",
        className,
      )}
    >
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-ecmp-surface-sunken"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 h-44 border-b border-ecmp-border bg-ecmp-surface shadow-ecmp-surface"
      />

      <div className="relative z-[1] w-full max-w-[var(--ecmp-form-max-width)]">
        {children}
      </div>
    </div>
  );
}
