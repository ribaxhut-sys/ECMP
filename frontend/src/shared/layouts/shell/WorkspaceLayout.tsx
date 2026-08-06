"use client";

import type { ReactNode } from "react";
import { cn } from "@/shared/utils";

export interface WorkspaceLayoutProps {
  children: ReactNode;
  /** Optional top toolbar (filters, title actions). */
  toolbar?: ReactNode;
  className?: string;
}

/**
 * Content frame inside AppLayout main — page gutter + optional toolbar.
 * Reuses theme layout tokens; no complaint domain content.
 */
export function WorkspaceLayout({
  children,
  toolbar,
  className,
}: WorkspaceLayoutProps) {
  return (
    <div
      className={cn(
        "mx-auto w-full max-w-[var(--ecmp-content-max,80rem)]",
        "px-[var(--ecmp-page-gutter)] py-[var(--ecmp-section-gap)]",
        "sm:px-6 lg:px-8",
        className,
      )}
    >
      {toolbar ? (
        <div className="mb-[var(--ecmp-panel-gap)]">{toolbar}</div>
      ) : null}
      <div className="min-w-0">{children}</div>
    </div>
  );
}
