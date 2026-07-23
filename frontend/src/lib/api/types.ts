/** Shared API envelope and domain types (aligned with complaint-service OpenAPI). */

export type ComplaintStatus =
  | "NEW"
  | "ASSIGNED"
  | "IN_PROGRESS"
  | "PENDING"
  | "ESCALATED"
  | "RESOLVED"
  | "CLOSED";

export type Priority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface ApiErrorBody {
  code: string;
  message: string;
  details: Record<string, unknown> | null;
}

export interface DataResponse<T> {
  data: T;
}

export interface PageMeta {
  page: number;
  pageSize: number;
  totalItems: number;
}

export interface ListResponse<T> {
  data: T[];
  meta: PageMeta;
}

export interface StatusCount {
  status: ComplaintStatus;
  count: number;
}

export interface BranchCount {
  branchId: string | null;
  branchCode: string | null;
  branchName: string | null;
  total: number;
}

export interface ReportSummary {
  total: number;
  byStatus: StatusCount[];
}

export interface Complaint {
  id: string;
  complaintNumber: string;
  customerId: string;
  branchId: string | null;
  subject: string;
  description: string;
  status: ComplaintStatus;
  priority: Priority;
  channel: string | null;
  category: string | null;
  reportedAt: string;
  closedAt: string | null;
  createdAt: string;
  createdBy: string | null;
  updatedAt: string;
}

/** API-201 create payload (complaint-service OpenAPI ComplaintCreateRequest). */
export interface ComplaintCreateRequest {
  customerId: string;
  subject: string;
  description: string;
  priority: Priority;
  branchId?: string | null;
  channel?: string | null;
  category?: string | null;
  reportedAt?: string | null;
}

/** API-205 assign request. */
export interface AssignComplaintRequest {
  assigneeId: string;
  reason?: string | null;
  notes?: string | null;
}

/** API-206 assignment row. */
export interface Assignment {
  id: string;
  complaintId: string;
  assigneeId: string;
  assigneeName: string | null;
  assignedBy: string | null;
  assignedAt: string;
  unassignedAt: string | null;
  isCurrent: boolean;
  notes: string | null;
  reason: string | null;
}

/** API-205 assign response data. */
export interface AssignComplaintResult {
  assignment: Assignment;
  complaintId: string;
  status: ComplaintStatus;
  reassigned: boolean;
}

/** API-209 timeline entry (read-only activity log). */
export interface TimelineEntry {
  id: string;
  complaintId: string;
  actorUserId: string | null;
  actorName: string | null;
  eventType:
    | "complaint.created"
    | "complaint.updated"
    | "complaint.assigned"
    | "complaint.reassigned"
    | "complaint.escalated"
    | "complaint.resolved"
    | "complaint.closed";
  eventAt: string;
  fromStatus: ComplaintStatus | null;
  toStatus: ComplaintStatus | null;
  summary: string;
  metadata: Record<string, unknown> | null;
  createdAt: string;
}

export interface TokenResponse {
  accessToken: string;
  tokenType: string;
  expiresIn: number;
}

export interface AuthMe {
  id: string;
  username: string;
  email: string;
  fullName: string;
  roleId: string;
  branchId: string | null;
  isActive: boolean;
  lastLoginAt: string | null;
  createdAt: string;
  updatedAt: string;
  roles: string[];
  permissions: string[];
}
