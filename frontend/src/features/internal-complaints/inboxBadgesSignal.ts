/**
 * Sidebar Internal inbox badge refresh.
 *
 * Receive / return / resend change the queue while the user stays on detail,
 * so the sidebar would keep a stale count until the next route change.
 */
export const INTERNAL_INBOX_BADGES_REFRESH_EVENT =
  "ecmp:internal-inbox-badges-refresh";

export function refreshInternalInboxBadges(): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new Event(INTERNAL_INBOX_BADGES_REFRESH_EVENT));
}
