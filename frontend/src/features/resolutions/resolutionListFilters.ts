import type {
  ComplaintSearchParams,
  ComplaintSortField,
  ComplaintStatus,
  Priority,
  SortOrder,
} from "@/lib/api/types";

export const STATUS_FILTER_OPTIONS = [
  { value: "", label: "All statuses" },
  { value: "NEW", label: "New" },
  { value: "ASSIGNED", label: "Assigned" },
  { value: "IN_PROGRESS", label: "In progress" },
  { value: "PENDING", label: "Pending" },
  { value: "ESCALATED", label: "Escalated" },
  { value: "RESOLVED", label: "Resolved" },
  { value: "CLOSED", label: "Closed" },
] as const;

export const PRIORITY_FILTER_OPTIONS = [
  { value: "", label: "All priorities" },
  { value: "LOW", label: "Low" },
  { value: "MEDIUM", label: "Medium" },
  { value: "HIGH", label: "High" },
  { value: "CRITICAL", label: "Critical" },
] as const;

export const ESCALATED_FILTER_OPTIONS = [
  { value: "", label: "Any escalation" },
  { value: "true", label: "Escalated" },
  { value: "false", label: "Not escalated" },
] as const;

export const SORT_FIELD_OPTIONS: { value: ComplaintSortField; label: string }[] =
  [
    { value: "createdAt", label: "Created at" },
    { value: "updatedAt", label: "Updated at" },
    { value: "priority", label: "Priority" },
    { value: "status", label: "Status" },
    { value: "slaDueDate", label: "SLA due date" },
  ];

export const SORT_ORDER_OPTIONS: { value: SortOrder; label: string }[] = [
  { value: "desc", label: "Descending" },
  { value: "asc", label: "Ascending" },
];

export const PAGE_SIZE_OPTIONS = [
  { value: "10", label: "10 / page" },
  { value: "20", label: "20 / page" },
  { value: "50", label: "50 / page" },
] as const;

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
