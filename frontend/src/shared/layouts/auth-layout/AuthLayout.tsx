import type { ReactNode } from "react";
import { cn } from "@/shared/utils";
import { IdentityTrustFooter } from "./IdentityTrustFooter";

export interface AuthLayoutProps {
  children: ReactNode;
  className?: string;
  /** Optional top-right chrome (e.g. language switcher). */
  toolbar?: ReactNode;
  showTrustFooter?: boolean;
}

/**
 * Centered auth shell for login / recovery screens.
 * Flat enterprise surface — no gradients, illustrations, or glassmorphism.
 */
export function AuthLayout({
  children,
  className,
  toolbar,
  showTrustFooter = true,
}: AuthLayoutProps) {
  return (
    <div
      className={cn(
        "relative flex min-h-screen w-full items-center justify-center overflow-x-hidden",
        "bg-ecmp-surface-sunken px-[var(--ecmp-page-gutter)] py-[var(--ecmp-section-gap)]",
        className,
      )}
    >
      <div className="relative z-[1] flex w-full max-w-[var(--ecmp-form-max-width)] flex-col gap-[var(--ecmp-panel-gap)]">
        {toolbar ? (
          <div className="flex justify-end">{toolbar}</div>
        ) : null}
        {children}
        {showTrustFooter ? <IdentityTrustFooter /> : null}
      </div>
    </div>
  );
}
