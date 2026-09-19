/** URL/query helpers for Aggregate list filters (API-514). */

export type CmBatch1ListStatus = "REGISTERED" | "IN_PROGRESS" | "CLOSED" | "OPEN";

export type CmBatch1ListIntakeDisposition =
  | "ESCALATE_PENDING_APPROVAL"
  | "ESCALATE_APPROVED"
  | "ESCALATE_REJECTED"
  | "ESCALATE_CANCELLED"
  | "RETURNED_TO_BRANCH"
  | "HQ_SCHEDULED"
  | "HQ_CLOSED"
  | "BRANCH_CLOSED"
  /** Ditutup karena seluruh Case dibatalkan — bukan penyelesaian kerja. */
  | "ALL_CASES_CANCELLED"
  /** Pseudo-value: any escalate-family state (Users directory drill-down). */
  | "ESCALATED"
  /** Pseudo-value: not in the escalate family (dashboard waiting-assignment). */
  | "UNESCALATED"
  /** Pseudo-value: BRANCH_CLOSED or HQ_CLOSED (Ditutup cabang archive). */
  | "COMPLETED";

/** Aggregate list filtered to open complaints (REGISTERED + IN_PROGRESS). */
export const CM_BATCH1_OPEN_HREF = "/complaints?status=OPEN";

/** Aggregate list filtered to closed complaints (sidebar Ditutup). */
export const CM_BATCH1_CLOSED_HREF = "/ditutup";

/** Aggregate list filtered to open intake that is not on an escalate path. */
export const CM_BATCH1_WAITING_ASSIGNMENT_HREF =
  "/complaints?status=REGISTERED&intakeDisposition=UNESCALATED";

/** Aggregate list filtered to intake waiting for escalation approval. */
export const CM_BATCH1_ESCALATION_PENDING_HREF =
  "/complaints?intakeDisposition=ESCALATE_PENDING_APPROVAL";

/** Aggregate list filtered to approved escalations waiting for HQ handling. */
export const CM_BATCH1_ESCALATION_APPROVED_HREF =
  "/complaints?intakeDisposition=ESCALATE_APPROVED";

/** Aggregate list filtered to complaints scheduled at HQ. */
export const CM_BATCH1_HQ_SCHEDULED_HREF =
  "/complaints?intakeDisposition=HQ_SCHEDULED";

/** Aggregate list filtered to complaints HQ returned to the branch. */
export const CM_BATCH1_RETURNED_TO_BRANCH_HREF =
  "/complaints?intakeDisposition=RETURNED_TO_BRANCH";

/** Aggregate list filtered to in-progress complaints. */
export const CM_BATCH1_IN_PROGRESS_HREF = "/complaints?status=IN_PROGRESS";

/** Pusat Pengaduan default — Cases escalated to Pusat and never handled. */
export const CM_BATCH1_PUSAT_UNHANDLED_HREF =
  "/complaints?needsPusatHandling=1";

/** Pusat Tindak lanjut — same door as the sidebar item. */
export const CM_BATCH1_FOLLOW_UP_HREF = "/tindak-lanjut";

/** HQ arrival calendar — same door as the sidebar Jadwal Eskalasi item. */
export const CM_BATCH1_HQ_SCHEDULE_PAGE_HREF = "/complaints/cm/hq-schedule";

/** True when the Aggregate list is the Ditutup (CLOSED) archive. */
export function isCmBatch1ClosedArchive(
  filters: Pick<CmBatch1ListFilters, "status">,
): boolean {
  return (filters.status || "").trim().toUpperCase() === "CLOSED";
}

function firstSearchValue(
  value: string | string[] | undefined,
): string {
  if (Array.isArray(value)) return value[0] ?? "";
  return value ?? "";
}

/**
 * Bookmark `/complaints?status=CLOSED` → `/ditutup`.
 * Drops work-queue pins; keeps keyword / paging / user drill-down.
 */
export function closedArchiveRedirectHrefFromRecord(
  params: Record<string, string | string[] | undefined>,
): string | null {
  const status = firstSearchValue(params.status).trim().toUpperCase();
  if (status !== "CLOSED") return null;
  const next = new URLSearchParams();
  const keyword = firstSearchValue(params.keyword).trim().slice(0, 200);
  if (keyword) next.set("keyword", keyword);
  const createdBy = firstSearchValue(params.createdBy).trim().slice(0, 128);
  if (createdBy) next.set("createdBy", createdBy);
  const decidedBy = firstSearchValue(params.decidedBy).trim().slice(0, 128);
  if (decidedBy) next.set("decidedBy", decidedBy);
  const page = firstSearchValue(params.page).trim();
  if (page && page !== "1") next.set("page", page);
  const pageSize = firstSearchValue(params.pageSize).trim();
  if (pageSize) next.set("pageSize", pageSize);
  const qs = next.toString();
  return qs ? `${CM_BATCH1_CLOSED_HREF}?${qs}` : CM_BATCH1_CLOSED_HREF;
}

const STATUSES = new Set<string>(["REGISTERED", "IN_PROGRESS", "CLOSED", "OPEN"]);
const INTAKE_DISPOSITIONS = new Set<string>([
  "ESCALATE_PENDING_APPROVAL",
  "ESCALATE_APPROVED",
  "ESCALATE_REJECTED",
  "ESCALATE_CANCELLED",
  "RETURNED_TO_BRANCH",
  "HQ_SCHEDULED",
  "HQ_CLOSED",
  "BRANCH_CLOSED",
  "ALL_CASES_CANCELLED",
  "ESCALATED",
  "UNESCALATED",
  "COMPLETED",
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
  needsPusatHandling: boolean;
  page: number;
  pageSize: number;
}

export function defaultCmBatch1ListFilters(options?: {
  pusatUnhandledQueue?: boolean;
  /** Cabang work list — open parents only. Ignored when pusatUnhandledQueue. */
  openOnly?: boolean;
  /** Ditutup archive — CLOSED parents only. */
  closedArchive?: boolean;
}): CmBatch1ListFilters {
  const closedArchive = options?.closedArchive === true;
  const pusatUnhandledQueue =
    !closedArchive && options?.pusatUnhandledQueue === true;
  const openOnly =
    !closedArchive && !pusatUnhandledQueue && options?.openOnly === true;
  return {
    keyword: "",
    status: closedArchive ? "CLOSED" : openOnly ? "OPEN" : "",
    intakeDisposition: "",
    createdBy: "",
    decidedBy: "",
    needsPusatHandling: pusatUnhandledQueue,
    page: 1,
    pageSize: 10,
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
    needsPusatHandling: ["1", "true", "yes"].includes(
      (params.get("needsPusatHandling") ?? "").trim().toLowerCase(),
    ),
    page: Number.isFinite(page) && page >= 1 ? Math.floor(page) : 1,
    pageSize:
      Number.isFinite(pageSize) && pageSize >= 1 && pageSize <= 100
        ? Math.floor(pageSize)
        : defaults.pageSize,
  };
}

/**
 * Bare `/complaints` for Pusat pins the unhandled queue.
 * Dashboard / SLA drill-downs already carry a filter — do not overwrite them.
 */
export function shouldDefaultPusatUnhandledQueue(
  filters: Pick<
    CmBatch1ListFilters,
    | "needsPusatHandling"
    | "intakeDisposition"
    | "status"
    | "keyword"
    | "createdBy"
    | "decidedBy"
  >,
): boolean {
  if (filters.needsPusatHandling) return false;
  if (filters.intakeDisposition) return false;
  if (filters.status) return false;
  if (filters.keyword.trim()) return false;
  if (filters.createdBy.trim() || filters.decidedBy.trim()) return false;
  return true;
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
  if (filters.needsPusatHandling) params.set("needsPusatHandling", "1");
  if (filters.page !== defaults.page) params.set("page", String(filters.page));
  if (filters.pageSize !== defaults.pageSize) {
    params.set("pageSize", String(filters.pageSize));
  }
  return params;
}
