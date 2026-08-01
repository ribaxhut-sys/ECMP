import type {
  ComplaintSearchParams,
  ComplaintSortField,
  ComplaintStatus,
  Priority,
  SortOrder,
} from "@/lib/api/types";

/** Filter option labels are built in the view via useTranslations. */

const SORT_FIELDS = new Set<ComplaintSortField>([
  "createdAt",
  "updatedAt",
  "priority",
  "status",
  "slaDueDate",
]);

const STATUSES = new Set<ComplaintStatus>([
  "NEW",
  "ASSIGNED",
  "IN_PROGRESS",
  "PENDING",
  "ESCALATED",
  "RESOLVED",
  "CLOSED",
]);

const PRIORITIES = new Set<Priority>(["LOW", "MEDIUM", "HIGH", "CRITICAL"]);

export interface ResolutionListFilters {
  keyword: string;
  status: string;
  priority: string;
  branchId: string;
  escalated: string;
  page: number;
  pageSize: number;
  sort: ComplaintSortField;
  order: SortOrder;
}

export function defaultResolutionFilters(): ResolutionListFilters {
  return {
    keyword: "",
    status: "",
    priority: "",
    branchId: "",
    escalated: "",
    page: 1,
    pageSize: 20,
    sort: "updatedAt",
    order: "desc",
  };
}

export function filtersFromSearchParams(
  params: URLSearchParams,
): ResolutionListFilters {
  const defaults = defaultResolutionFilters();
  const sortRaw = params.get("sort") ?? defaults.sort;
  const orderRaw = params.get("order") ?? defaults.order;
  const statusRaw = params.get("status") ?? "";
  const priorityRaw = params.get("priority") ?? "";
  const escalatedRaw = params.get("escalated") ?? "";
  const page = Number(params.get("page") ?? defaults.page);
  const pageSize = Number(params.get("pageSize") ?? defaults.pageSize);

  return {
    keyword: (params.get("keyword") ?? "").slice(0, 200),
    status: STATUSES.has(statusRaw as ComplaintStatus) ? statusRaw : "",
    priority: PRIORITIES.has(priorityRaw as Priority) ? priorityRaw : "",
    branchId: params.get("branchId") ?? "",
    escalated:
      escalatedRaw === "true" || escalatedRaw === "false" ? escalatedRaw : "",
    page: Number.isFinite(page) && page >= 1 ? Math.floor(page) : 1,
    pageSize:
      Number.isFinite(pageSize) && pageSize >= 1 && pageSize <= 100
        ? Math.floor(pageSize)
        : defaults.pageSize,
    sort: SORT_FIELDS.has(sortRaw as ComplaintSortField)
      ? (sortRaw as ComplaintSortField)
      : defaults.sort,
    order: orderRaw === "asc" || orderRaw === "desc" ? orderRaw : defaults.order,
  };
}

export function filtersToSearchParams(
  filters: ResolutionListFilters,
): URLSearchParams {
  const params = new URLSearchParams();
  const defaults = defaultResolutionFilters();

  if (filters.keyword.trim()) params.set("keyword", filters.keyword.trim());
  if (filters.status) params.set("status", filters.status);
  if (filters.priority) params.set("priority", filters.priority);
  if (filters.branchId) params.set("branchId", filters.branchId);
  if (filters.escalated) params.set("escalated", filters.escalated);
  if (filters.page !== defaults.page) params.set("page", String(filters.page));
  if (filters.pageSize !== defaults.pageSize) {
    params.set("pageSize", String(filters.pageSize));
  }
  if (filters.sort !== defaults.sort) params.set("sort", filters.sort);
  if (filters.order !== defaults.order) params.set("order", filters.order);
  return params;
}

export function toSearchApiParams(
  filters: ResolutionListFilters,
): ComplaintSearchParams {
  return {
    keyword: filters.keyword.trim() || undefined,
    status: filters.status
      ? (filters.status as ComplaintStatus)
      : undefined,
    priority: filters.priority
      ? (filters.priority as Priority)
      : undefined,
    branchId: filters.branchId || undefined,
    escalated:
      filters.escalated === "true"
        ? true
        : filters.escalated === "false"
          ? false
          : undefined,
    page: filters.page,
    pageSize: filters.pageSize,
    sort: filters.sort,
    order: filters.order,
  };
}
