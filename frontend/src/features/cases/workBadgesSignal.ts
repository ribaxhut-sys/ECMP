/**
 * Sidebar badge refresh signal.
 *
 * Opening a Complaint or Case marks it read server-side, but the sidebar only
 * refetches on route change — so the badge would keep the stale count while
 * the user is still on the detail page. Detail views fire this once loaded.
 */
export const WORK_BADGES_REFRESH_EVENT = "ecmp:work-badges-refresh";

export function refreshWorkBadges(): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new Event(WORK_BADGES_REFRESH_EVENT));
}
