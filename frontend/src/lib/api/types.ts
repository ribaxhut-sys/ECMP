/** Shared API envelope and domain types (aligned with complaint-service OpenAPI). */

export type ComplaintStatus =
  | "NEW"
  | "ASSIGNED"
  | "IN_PROGRESS"
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
