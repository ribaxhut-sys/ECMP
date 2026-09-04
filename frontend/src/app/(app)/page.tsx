"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { fetchUnreadAnnouncementCount } from "@/lib/api";
import { isShellUiBatch } from "@/shared/config/uiBatch";
import { PageContainer, Skeleton } from "@/shared/ui";

/**
 * Root entry-point gate (post-login unread-announcement redirect, LOCKED).
 *
 * Dashboard stays the app's default home — this route only decides, once,
 * whether to detour through /announcements first when the caller has any
 * unread *active* announcement (`GET /unread` count > 0). Nothing else in
 * the app links here (sidebar Brand and breadcrumbs point at /dashboard),
 * so this only runs at the login redirect or a fresh visit to "/" — never
 * as part of normal in-app navigation (avoids a redirect loop).
 *
 * `(app)/layout.tsx` → AuthenticatedShell → RequireAuth already blocks
 * rendering until `status === "authenticated"`.
 */
export default function EntryPointPage() {
  const router = useRouter();
  const { hasPermission } = useAuth();
  const t = useTranslations("session");
  const decided = useRef(false);

  useEffect(() => {
    if (isShellUiBatch()) {
      router.replace("/workspace");
      return;
    }
    // Guards against React StrictMode's double-invoke and repeat renders —
    // exactly one navigation decision (and at most one API call) per visit.
    if (decided.current) return;
    decided.current = true;

    if (!hasPermission("announcement:read")) {
      router.replace("/dashboard");
      return;
    }

    fetchUnreadAnnouncementCount()
      .then((res) => {
        const unread = typeof res.data === "number" ? res.data : 0;
        router.replace(unread > 0 ? "/announcements" : "/dashboard");
      })
      .catch(() => {
        // Fail open — Dashboard stays reachable even if the unread check errors.
        router.replace("/dashboard");
      });
  }, [hasPermission, router]);

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]" aria-label={t("loading")}>
      <Skeleton rows={6} />
    </PageContainer>
  );
}
