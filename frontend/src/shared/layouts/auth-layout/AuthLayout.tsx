import type { ReactNode } from "react";
import { cn } from "@/shared/utils";

export interface AuthLayoutProps {
  children: ReactNode;
  className?: string;
}

/**
 * Centered auth shell for login / session screens.
 * Does not include the application sidebar or header chrome.
 */
export function AuthLayout({ children, className }: AuthLayoutProps) {
  return (
    <div
      className={cn(
        "flex min-h-screen w-full items-center justify-center overflow-x-hidden bg-ecmp-background px-4 py-8",
        className,
      )}
    >
      <div className="w-full max-w-md">{children}</div>
    </div>
  );
}
