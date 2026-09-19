"use client";

import { AnnouncementHistoryView } from "@/features/announcements";
import { PageContainer } from "@/shared/ui";

/**
 * Riwayat Pengumuman — every announcement:read holder (including Admin/Pusat).
 * Pengelolaan lives at ``/announcements/manage`` (Option B dual route).
 */
export default function AnnouncementsHistoryPage() {
  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <AnnouncementHistoryView />
    </PageContainer>
  );
}
