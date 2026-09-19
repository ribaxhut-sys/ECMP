/**
 * Sidebar WP badge refresh (same tab).
 *
 * Opening a Complaint or Case marks it read server-side. The receiving login
 * (other session) relies on poll / tab-focus in useCmWorkBadges — this event
 * cannot cross browsers.
 */
export const WORK_BADGES_REFRESH_EVENT = "ecmp:work-badges-refresh";

export function refreshWorkBadges(): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new Event(WORK_BADGES_REFRESH_EVENT));
}
