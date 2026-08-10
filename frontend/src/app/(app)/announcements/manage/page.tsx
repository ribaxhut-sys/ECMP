"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { AnnouncementManagement } from "@/features/announcements";
import { mayManageAnnouncements } from "@/features/announcements/announcementManageGate";
import { useOrgUnitCode } from "@/features/announcements/useOrgUnitCode";
import { PageContainer } from "@/shared/ui";

/**
 * Kelola Pengumuman — Admin / Supervisor Pusat / Manager Pusat only.
 * Cabang holders of announcement:manage are redirected to the shared history
 * route; backend require_announcement_manage remains the real enforcement.
 */
export default function AnnouncementsManagePage() {
  const router = useRouter();
  const { roles, hasPermission, status } = useAuth();
  const orgUnitCode = useOrgUnitCode();

  const ready = status === "authenticated" && orgUnitCode !== undefined;
  const canManage =
    ready &&
    mayManageAnnouncements({
      roles,
      hasPermission,
      orgUnitCode: orgUnitCode ?? null,
    });

  useEffect(() => {
    if (!ready) return;
    if (!canManage) {
      router.replace("/announcements");
    }
  }, [ready, canManage, router]);

  if (!ready || !canManage) {
    return (
      <PageContainer>
        <div
          className="h-40 animate-pulse rounded-[var(--ecmp-radius-md)] bg-ecmp-surface-sunken"
          aria-hidden
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <AnnouncementManagement />
    </PageContainer>
  );
}
