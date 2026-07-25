import type {
  ComplaintSearchParams,
  ComplaintSortField,
  ComplaintStatus,
  Priority,
  SlaStatus,
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

export const SLA_STATUS_FILTER_OPTIONS = [
  { value: "", label: "All SLA" },
  { value: "PENDING", label: "Pending" },
  { value: "ON_TIME", label: "On time" },
  { value: "BREACHED", label: "Breached" },
  { value: "COMPLETED", label: "Completed" },
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

const SLA_STATUSES = new Set<SlaStatus>([
  "PENDING",
  "ON_TIME",
  "BREACHED",
  "COMPLETED",
]);

export interface QueueListFilters {
  keyword: string;
  status: string;
  priority: string;
  slaStatus: string;
  assignedTo: string;
  mineOnly: boolean;
  page: number;
  pageSize: number;
  sort: ComplaintSortField;
  order: SortOrder;
}

export function defaultQueueFilters(): QueueListFilters {
  return {
    keyword: "",
    status: "",
    priority: "",
    slaStatus: "",
    assignedTo: "",
    mineOnly: false,
    page: 1,
    pageSize: 20,
    sort: "createdAt",
    order: "desc",
  };
}

export function filtersFromSearchParams(
  params: URLSearchParams,
): QueueListFilters {
  const defaults = defaultQueueFilters();
  const sortRaw = params.get("sort") ?? defaults.sort;
  const orderRaw = params.get("order") ?? defaults.order;
  const statusRaw = params.get("status") ?? "";
  const priorityRaw = params.get("priority") ?? "";
  const slaRaw = params.get("slaStatus") ?? "";
  const page = Number(params.get("page") ?? defaults.page);
  const pageSize = Number(params.get("pageSize") ?? defaults.pageSize);

  return {
    keyword: (params.get("keyword") ?? "").slice(0, 200),
    status: STATUSES.has(statusRaw as ComplaintStatus) ? statusRaw : "",
    priority: PRIORITIES.has(priorityRaw as Priority) ? priorityRaw : "",
    slaStatus: SLA_STATUSES.has(slaRaw as SlaStatus) ? slaRaw : "",
    assignedTo: params.get("assignedTo") ?? "",
    mineOnly: params.get("mine") === "1",
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
  filters: QueueListFilters,
): URLSearchParams {
  const params = new URLSearchParams();
  const defaults = defaultQueueFilters();

  if (filters.keyword.trim()) params.set("keyword", filters.keyword.trim());
  if (filters.status) params.set("status", filters.status);
  if (filters.priority) params.set("priority", filters.priority);
  if (filters.slaStatus) params.set("slaStatus", filters.slaStatus);
  if (filters.assignedTo) params.set("assignedTo", filters.assignedTo);
  if (filters.mineOnly) params.set("mine", "1");
  if (filters.page !== defaults.page) params.set("page", String(filters.page));
  if (filters.pageSize !== defaults.pageSize) {
    params.set("pageSize", String(filters.pageSize));
  }
  if (filters.sort !== defaults.sort) params.set("sort", filters.sort);
  if (filters.order !== defaults.order) params.set("order", filters.order);
  return params;
}

export function toSearchApiParams(
  filters: QueueListFilters,
  currentUserId: string | null,
): ComplaintSearchParams {
  const assignedTo = filters.mineOnly
    ? currentUserId || undefined
    : filters.assignedTo || undefined;

  return {
    keyword: filters.keyword.trim() || undefined,
    status: filters.status
      ? (filters.status as ComplaintStatus)
      : undefined,
    priority: filters.priority
      ? (filters.priority as Priority)
      : undefined,
    slaStatus: filters.slaStatus
      ? (filters.slaStatus as SlaStatus)
      : undefined,
    assignedTo,
    page: filters.page,
    pageSize: filters.pageSize,
    sort: filters.sort,
    order: filters.order,
  };
}
