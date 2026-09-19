/**
 * Sidebar Internal inbox badge refresh (same tab).
 *
 * Receive / return / resend change the queue while the actor stays on detail.
 * The receiving login (other session) relies on poll / tab-focus in
 * usePendingInboxCount — this event cannot cross browsers.
 */
export const INTERNAL_INBOX_BADGES_REFRESH_EVENT =
  "ecmp:internal-inbox-badges-refresh";

export function refreshInternalInboxBadges(): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new Event(INTERNAL_INBOX_BADGES_REFRESH_EVENT));
}
