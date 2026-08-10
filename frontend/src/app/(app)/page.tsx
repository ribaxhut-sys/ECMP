"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { fetchHasUnreadAnnouncements } from "@/lib/api";
import { isShellUiBatch } from "@/shared/config/uiBatch";
import { PageContainer, Skeleton } from "@/shared/ui";

/**
 * Root entry-point gate (post-login unread-announcement redirect milestone).
 *
 * Dashboard stays the app's default home (LOCKED) — this route only decides,
 * once, whether to detour through /announcements first. Nothing else in the
 * app links here anymore (sidebar Brand points at /dashboard, breadcrumbs
 * point at /dashboard), so this only runs at the login redirect or a fresh
 * visit to "/" — never as part of normal in-app navigation, which is what
 * keeps this from becoming a redirect loop.
 *
 * `(app)/layout.tsx` → AuthenticatedShell → RequireAuth already blocks
 * rendering of this component until `status === "authenticated"`, so no
 * additional auth-status check is needed here.
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

    fetchHasUnreadAnnouncements()
      .then((res) => {
        router.replace(res.data ? "/announcements" : "/dashboard");
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
