/**
 * Typography for Internal ticket numbers.
 *
 * Unread = this login has not opened GET detail since the last bump, and
 * the ticket still needs action for their unit. Badge (API-551) is separate.
 */
export function internalTicketNumberClass(
  isRead: boolean | null | undefined,
  unreadClass: string,
  readClass: string,
): string {
  return isRead === false ? unreadClass : readClass;
}
