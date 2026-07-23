import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/shared/utils";

export interface PageContainerProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  /** Constrain content width (default true). */
  constrained?: boolean;
}

export function PageContainer({
  className,
  children,
  constrained = true,
  ...props
}: PageContainerProps) {
  return (
    <div
      className={cn(
        "w-full px-4 py-4 sm:px-6 lg:px-8 lg:py-6",
        constrained && "mx-auto max-w-7xl",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
