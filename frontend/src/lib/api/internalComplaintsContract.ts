/**
 * Pengaduan Internal — pure path contract (no network).
 * Domain terpisah dari F4 `/api/v1/cm/cases` dan foundation `/api/v1/complaints`.
 */
export const INTERNAL_COMPLAINTS_BASE = "/api/v1/internal/complaints";

export function internalComplaintPaths() {
  return {
    list: INTERNAL_COMPLAINTS_BASE,
    detail: (id: string) =>
      `${INTERNAL_COMPLAINTS_BASE}/${encodeURIComponent(id)}`,
    transfer: (id: string) =>
      `${INTERNAL_COMPLAINTS_BASE}/${encodeURIComponent(id)}/transfer`,
    receive: (id: string) =>
      `${INTERNAL_COMPLAINTS_BASE}/${encodeURIComponent(id)}/receive`,
    status: (id: string) =>
      `${INTERNAL_COMPLAINTS_BASE}/${encodeURIComponent(id)}/status`,
    resolve: (id: string) =>
      `${INTERNAL_COMPLAINTS_BASE}/${encodeURIComponent(id)}/resolve`,
    acceptance: (id: string) =>
      `${INTERNAL_COMPLAINTS_BASE}/${encodeURIComponent(id)}/acceptance`,
    close: (id: string) =>
      `${INTERNAL_COMPLAINTS_BASE}/${encodeURIComponent(id)}/close`,
    transferRequest: (id: string) =>
      `${INTERNAL_COMPLAINTS_BASE}/${encodeURIComponent(id)}/transfer-request`,
    transferRequestDecision: (id: string) =>
      `${INTERNAL_COMPLAINTS_BASE}/${encodeURIComponent(id)}/transfer-request/decision`,
    pendingTransferRequestCount: `${INTERNAL_COMPLAINTS_BASE}/transfer-requests/pending-count`,
    withdraw: (id: string) =>
      `${INTERNAL_COMPLAINTS_BASE}/${encodeURIComponent(id)}/withdraw`,
    withdrawRequest: (id: string) =>
      `${INTERNAL_COMPLAINTS_BASE}/${encodeURIComponent(id)}/withdraw-request`,
    withdrawRequestDecision: (id: string) =>
      `${INTERNAL_COMPLAINTS_BASE}/${encodeURIComponent(id)}/withdraw-request/decision`,
    pendingWithdrawRequestCount: `${INTERNAL_COMPLAINTS_BASE}/withdraw-requests/pending-count`,
  } as const;
}
