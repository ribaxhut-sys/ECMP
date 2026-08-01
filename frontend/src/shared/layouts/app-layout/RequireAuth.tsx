"use client";

import { useEffect, type ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { PASSWORD_CHANGE_ROUTE } from "@/features/auth";
import { Loading } from "@/shared/ui";

/**
 * Client-side session gate. Preserves existing auth redirect behavior;
 * does not alter login/logout/token flows.
 *
 * When forcePasswordChange is true, the user is confined to the change-password
 * page until they update their password.
 */
export function RequireAuth({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { status, user } = useAuth();
  const t = useTranslations("session");
  const forcePasswordChange = Boolean(user?.forcePasswordChange);

  useEffect(() => {
    if (status === "unauthenticated") {
      router.replace("/login");
      return;
    }
    if (
      status === "authenticated" &&
      forcePasswordChange &&
      pathname !== PASSWORD_CHANGE_ROUTE
    ) {
      router.replace(PASSWORD_CHANGE_ROUTE);
    }
  }, [status, forcePasswordChange, pathname, router]);

  if (status === "loading" || status === "unauthenticated") {
    return <Loading label={t("loading")} />;
  }

  if (forcePasswordChange && pathname !== PASSWORD_CHANGE_ROUTE) {
    return <Loading label={t("passwordChangeRequired")} />;
  }

  return <>{children}</>;
}
