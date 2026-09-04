import type { Announcement } from "@/lib/api/types";

/** Newest published first — matches the backend's /announcements/active order. */
export function sortAnnouncements(items: readonly Announcement[]): Announcement[] {
  return [...items].sort((a, b) => {
    const aTime = a.publishedAt ? new Date(a.publishedAt).getTime() : 0;
    const bTime = b.publishedAt ? new Date(b.publishedAt).getTime() : 0;
    return bTime - aTime;
  });
}

/**
 * Landing page cap — this is an entry point, not a news archive. The rest
 * stay reachable only once a dedicated announcements list exists (not in
 * scope here).
 */
export const LANDING_ANNOUNCEMENT_LIMIT = 4;

export function selectLandingAnnouncements(
  items: readonly Announcement[],
  limit: number = LANDING_ANNOUNCEMENT_LIMIT,
): { featured: Announcement | null; rest: Announcement[] } {
  const sorted = sortAnnouncements(items).slice(0, Math.max(0, limit));
  if (sorted.length === 0) return { featured: null, rest: [] };
  return { featured: sorted[0], rest: sorted.slice(1) };
}
