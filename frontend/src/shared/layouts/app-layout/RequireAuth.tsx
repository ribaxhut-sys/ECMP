"use client";

import { useEffect, type ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { Loading } from "@/shared/ui";

const CHANGE_PASSWORD_PATH = "/change-password";

/**
 * Client-side session gate.
 * Redirects unauthenticated users to login, and users with
 * forcePasswordChange to /change-password (no infinite loop).
 */
export function RequireAuth({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { status, forcePasswordChange } = useAuth();

  useEffect(() => {
    if (status === "unauthenticated") {
      router.replace("/login");
      return;
    }
    if (
      status === "authenticated" &&
      forcePasswordChange &&
      pathname !== CHANGE_PASSWORD_PATH
    ) {
      router.replace(CHANGE_PASSWORD_PATH);
    }
  }, [status, forcePasswordChange, pathname, router]);

  if (status === "loading" || status === "unauthenticated") {
    return <Loading label="Loading session…" />;
  }

  if (forcePasswordChange && pathname !== CHANGE_PASSWORD_PATH) {
    return <Loading label="Password change required…" />;
  }

  return <>{children}</>;
}
