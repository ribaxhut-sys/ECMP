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

export type ResolutionCategory =
  | "SOLVED"
  | "WORKAROUND"
  | "DUPLICATE"
  | "INVALID_REQUEST"
  | "USER_ERROR"
  | "THIRD_PARTY";

export type EscalationReasonCode =
  | "SPECIALIST_REQUIRED"
  | "COMPLEX_CASE"
  | "POLICY_EXCEPTION"
  | "CUSTOMER_REQUEST"
  | "OTHER";

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

/** API-225 resolve request. */
export interface ResolveComplaintRequest {
  resolutionCategory: ResolutionCategory;
  rootCause: string;
  resolutionNotes: string;
  resolvedBy?: string | null;
}

/** API-226 resolution row. */
export interface Resolution {
  id: string;
  complaintId: string;
  resolutionCategory: ResolutionCategory;
  rootCause: string;
  resolutionNotes: string;
  resolvedBy: string;
  resolvedByName: string | null;
  resolvedAt: string;
  isCurrent: boolean;
}

/** API-225 resolve response data. */
export interface ResolveComplaintResult {
  resolution: Resolution;
  complaintId: string;
  status: ComplaintStatus;
}

/** API-301 escalation request body. */
export interface EscalationRequestCreate {
  reasonCode: EscalationReasonCode;
  reasonDescription: string;
  diagnosis: string;
  notes?: string | null;
}

/** API-301 create response. */
export interface EscalationRequestResult {
  id: string;
  complaintId: string;
  status: "REQUESTED";
  requestedBy: string;
  requestedAt: string;
}

/** API-303 / API-304 review body. */
export interface EscalationReviewRequest {
  reviewNotes: string;
}

/** API-303 / API-304 slim review response. */
export interface EscalationReviewResult {
  id: string;
  status: "APPROVED" | "REJECTED";
  reviewedBy: string;
  reviewedAt: string;
}

/** API-208 / API-302 escalation row. */
export interface Escalation {
  id: string;
  complaintId: string;
  escalatedFromUserId: string | null;
  escalatedToUserId: string | null;
  escalatedToRoleId: string | null;
  reason: string;
  level: number;
  status: string;
  escalatedAt: string;
  resolvedAt: string | null;
  reasonCode: string | null;
  reasonDescription: string | null;
  diagnosis: string | null;
  notes: string | null;
  requestedBy: string | null;
  requestedByName: string | null;
  requestedAt: string | null;
  reviewedBy: string | null;
  reviewedByName: string | null;
  reviewedAt: string | null;
  reviewNotes: string | null;
  activeAppointment?: AppointmentSummary | null;
}

/** API-305 / API-302 appointment summary. */
export interface AppointmentSummary {
  id: string;
  status: "BOOKED" | "CHECKED_IN" | string;
  appointmentDate: string;
  appointmentStartTime: string;
  appointmentEndTime: string;
  assignedEngineerId: string;
}

/** API-305 book request. */
export interface AppointmentCreate {
  appointmentDate: string;
  startTime: string;
  endTime: string;
  assignedEngineerId: string;
  notes?: string | null;
}

/** API-305 slim create response. */
export interface AppointmentBookResult {
  id: string;
  status: "BOOKED";
}

/** API-307 check-in request. */
export interface AppointmentCheckInRequest {
  notes?: string | null;
}

/** API-307 slim check-in response. */
export interface AppointmentCheckInResult {
  id: string;
  status: "CHECKED_IN";
  checkedInAt: string;
  checkedInBy: string;
}

/** API-306 appointment detail. */
export interface Appointment {
  id: string;
  escalationId: string;
  appointmentDate: string;
  appointmentStartTime: string;
  appointmentEndTime: string;
  status: "BOOKED" | "CHECKED_IN" | string;
  assignedEngineerId: string;
  assignedEngineerName: string | null;
  notes: string | null;
  checkedInAt: string | null;
  checkedInBy: string | null;
  checkinNotes: string | null;
  createdBy: string | null;
  createdAt: string;
  updatedAt: string;
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
    | "complaint.escalation_requested"
    | "complaint.escalation_approved"
    | "complaint.escalation_rejected"
    | "complaint.appointment_booked"
    | "complaint.appointment_checked_in"
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
