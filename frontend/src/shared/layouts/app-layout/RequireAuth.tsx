"use client";

import { useEffect, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { Loading } from "@/shared/ui";

/**
 * Client-side session gate. Preserves existing auth redirect behavior;
 * does not alter login/logout/token flows.
 */
export function RequireAuth({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { status } = useAuth();

  useEffect(() => {
    if (status === "unauthenticated") {
      router.replace("/login");
    }
  }, [status, router]);

  if (status === "loading" || status === "unauthenticated") {
    return <Loading label="Loading session…" />;
  }

  return <>{children}</>;
}
