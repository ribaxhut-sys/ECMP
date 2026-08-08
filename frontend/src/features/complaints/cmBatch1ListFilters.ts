/** URL/query helpers for Aggregate list filters (API-514). */

export type CmBatch1ListStatus = "REGISTERED" | "CLOSED";

export type CmBatch1ListIntakeDisposition =
  | "ESCALATE_PENDING_APPROVAL"
  | "ESCALATE_APPROVED"
  | "ESCALATE_REJECTED"
  | "ESCALATE_CANCELLED"
  | "RETURNED_TO_BRANCH"
  | "HQ_SCHEDULED"
  | "BRANCH_CLOSED"
  /** Pseudo-value: any escalate-family state (Users directory drill-down). */
  | "ESCALATED";

const STATUSES = new Set<string>(["REGISTERED", "CLOSED"]);
const INTAKE_DISPOSITIONS = new Set<string>([
  "ESCALATE_PENDING_APPROVAL",
  "ESCALATE_APPROVED",
  "ESCALATE_REJECTED",
  "ESCALATE_CANCELLED",
  "RETURNED_TO_BRANCH",
  "HQ_SCHEDULED",
  "BRANCH_CLOSED",
  "ESCALATED",
]);

export interface CmBatch1ListFilters {
  keyword: string;
  /** Empty = all statuses. */
  status: string;
  /** Empty = all intake dispositions. */
  intakeDisposition: string;
  /** Set via drill-down from the Users directory work-stats panel (UM-BUG-006). */
  createdBy: string;
  decidedBy: string;
  page: number;
  pageSize: number;
}

export function defaultCmBatch1ListFilters(): CmBatch1ListFilters {
  return {
    keyword: "",
    status: "",
    intakeDisposition: "",
    createdBy: "",
    decidedBy: "",
    page: 1,
    pageSize: 20,
  };
}

export function cmBatch1FiltersFromSearchParams(
  params: URLSearchParams,
): CmBatch1ListFilters {
  const defaults = defaultCmBatch1ListFilters();
  const statusRaw = (params.get("status") ?? "").toUpperCase();
  const dispositionRaw = (params.get("intakeDisposition") ?? "").toUpperCase();
  const page = Number(params.get("page") ?? defaults.page);
  const pageSize = Number(params.get("pageSize") ?? defaults.pageSize);
  return {
    keyword: (params.get("keyword") ?? "").slice(0, 200),
    status: STATUSES.has(statusRaw) ? statusRaw : "",
    intakeDisposition: INTAKE_DISPOSITIONS.has(dispositionRaw)
      ? dispositionRaw
      : "",
    createdBy: (params.get("createdBy") ?? "").slice(0, 128),
    decidedBy: (params.get("decidedBy") ?? "").slice(0, 128),
    page: Number.isFinite(page) && page >= 1 ? Math.floor(page) : 1,
    pageSize:
      Number.isFinite(pageSize) && pageSize >= 1 && pageSize <= 100
        ? Math.floor(pageSize)
        : defaults.pageSize,
  };
}

export function cmBatch1FiltersToSearchParams(
  filters: CmBatch1ListFilters,
): URLSearchParams {
  const params = new URLSearchParams();
  const defaults = defaultCmBatch1ListFilters();
  if (filters.keyword.trim()) params.set("keyword", filters.keyword.trim());
  if (filters.status) params.set("status", filters.status);
  if (filters.intakeDisposition) {
    params.set("intakeDisposition", filters.intakeDisposition);
  }
  if (filters.createdBy.trim()) params.set("createdBy", filters.createdBy.trim());
  if (filters.decidedBy.trim()) params.set("decidedBy", filters.decidedBy.trim());
  if (filters.page !== defaults.page) params.set("page", String(filters.page));
  if (filters.pageSize !== defaults.pageSize) {
    params.set("pageSize", String(filters.pageSize));
  }
  return params;
}
