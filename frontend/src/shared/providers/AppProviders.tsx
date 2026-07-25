"use client";

import type { ReactNode } from "react";
import { AuthProvider } from "@/auth/AuthProvider";
import { GlobalLoadingBar } from "@/shared/ui/loading/GlobalLoadingBar";
import { ToastProvider } from "./ToastProvider";

/**
 * Root client providers for Sprint F1 foundation:
 * Auth session, global Axios error toasts, global loading bar.
 */
export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <ToastProvider>
        <GlobalLoadingBar />
        {children}
      </ToastProvider>
    </AuthProvider>
  );
}
