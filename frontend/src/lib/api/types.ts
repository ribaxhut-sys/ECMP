/** Shared API envelope and domain types (aligned with complaint-service OpenAPI). */

export type ComplaintStatus =
  | "NEW"
  | "ASSIGNED"
  | "IN_PROGRESS"
  | "PENDING"
  | "ESCALATED"
  | "RESOLVED"
  | "CLOSED";

/** CM Aggregate lifecycle on API-210 / API-211 (DEC-025 §3.3). */
export type AggregateComplaintStatus =
  | "REGISTERED"
  | "IN_PROGRESS"
  | "CLOSED";

/**
 * Donut / report-card slices from aggregate-kpis.
 * IN_PROGRESS and CLOSED are real Aggregate statuses; the others are
 * operational slices (not Foundation NEW/ASSIGNED/PENDING/ESCALATED).
 */
export type OperationalKpiSlice =
  | "waitingAssignment"
  | "escalatePending"
  | "escalateApproved"
  | "escalateScheduled"
  | "IN_PROGRESS"
  | "CLOSED";

export type StatusCountStatus = AggregateComplaintStatus | OperationalKpiSlice;

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
  status: StatusCountStatus;
  count: number;
  /** Dashboard i18n key — do not fall back to Foundation status.NEW = "Baru". */
  labelKey?: string;
}

/** GET /api/v1/reports/cycle-time — how long closed cases took, in days. */
export interface CycleTimeBucket {
  key: string;
  count: number;
}

export interface CycleTimeSummary {
  closedCases: number;
  averageDays: number | null;
  medianDays: number | null;
  p90Days: number | null;
  fastestDays: number | null;
  slowestDays: number | null;
  buckets: CycleTimeBucket[];
}

export interface BranchCount {
  branchId: string | null;
  branchCode: string | null;
  branchName: string | null;
  /** Stable 3-letter unit code, embedded in the complaint number (e.g. "TAB" in CMTAB-2608-0001). */
  unitCode: string | null;
  total: number;
  open: number;
  closed: number;
  /** Complaints on the active escalation path, including HQ_SCHEDULED. */
  escalated: number;
  caseTotal: number;
  caseOpen: number;
  caseClosed: number;
}

export interface ReportSummary {
  total: number;
  byStatus: StatusCount[];
}

/** API-318 KPI Foundation summary (live aggregates; never persisted). */
export interface ComplaintKpiCounts {
  total: number;
  open: number;
  closed: number;
}

export interface SlaStageKpiCounts {
  completed: number;
  breached: number;
}

export interface KpiSummary {
  complaints: ComplaintKpiCounts;
  assignment: SlaStageKpiCounts;
  appointment: SlaStageKpiCounts;
  resolution: SlaStageKpiCounts;
  escalation: SlaStageKpiCounts;
  overall: SlaStageKpiCounts;
}

/** API-389 Dashboard complaint summary widget (CAPABILITY-013). */
export interface DashboardComplaintSummary {
  totalComplaints: number;
  openComplaints: number;
  closedComplaints: number;
  pendingComplaints: number;
  overdueComplaints: number;
  escalatedComplaints: number;
  todayComplaints: number;
  thisMonthComplaints: number;
}

/** API-403 unassign request (complaint domain). */
export interface UnassignComplaintRequest {
  releasedBy: string;
  reason?: string | null;
}

/** API-319 Dashboard Summary (orchestration; never persisted). */
export interface DashboardHeader {
  totalComplaints: number;
  openComplaints: number;
  closedComplaints: number;
}

export interface DashboardSlaStage {
  completed: number;
  breached: number;
}

export interface DashboardSlaSummary {
  assignment: DashboardSlaStage;
  appointment: DashboardSlaStage;
  resolution: DashboardSlaStage;
  escalation: DashboardSlaStage;
  overall: DashboardSlaStage;
}

export interface DashboardRecentActivityItem {
  eventType: string;
  complaintNumber: string;
  timestamp: string;
  actor: string;
  caseNumber?: string | null;
}

export interface DashboardSummary {
  header: DashboardHeader;
  sla: DashboardSlaSummary;
  recentActivity: DashboardRecentActivityItem[];
}

/** DEC-031 — 30 calendar-day resolution SLA status of one complaint. */
export type ComplaintSlaStatus = "ON_TRACK" | "OVERDUE" | "MET" | "MISSED";

/**
 * DEC-031 resolution SLA. Every value is computed server-side at read time —
 * never recomputed from the browser clock.
 */
export interface ComplaintSla {
  status: ComplaintSlaStatus;
  targetDays: number;
  dueAt: string;
  elapsedDays: number;
  remainingDays: number | null;
  overdueDays: number | null;
  /** Open and past the warning threshold, not yet overdue. */
  isWarning: boolean;
}

/**
 * DEC-031 dashboard rollup. The six counts partition every complaint in
 * scope, so they always sum to the total.
 */
export interface DashboardResolutionSla {
  targetDays: number;
  onTrack: number;
  warning: number;
  overdue: number;
  met: number;
  missed: number;
  /** Closed without a stamped closure time — excluded from compliance. */
  unknown: number;
  /** met / (met + missed); null until something has settled. */
  compliancePercentage: number | null;
}

/** GET /api/v1/dashboard/aggregate-kpis — CM Aggregate complaint KPIs (DEC-026). */
export interface DashboardAggregateKpis {
  total: number;
  open: number;
  closed: number;
  escalatePending: number;
  waitingAssignment: number;
  escalateApproved: number;
  /** HQ visit already scheduled — still on the escalation path. */
  escalateScheduled: number;
  inProgress: number;
  /** DEC-031 rollup; null when SLA measurement is switched off. */
  sla?: DashboardResolutionSla | null;
}

/** DEC-031 — one complaint approaching or past its resolution target. */
export interface ComplaintSlaAlertItem {
  complaintId: string;
  complaintNumber: string;
  subject: string | null;
  owningUnitId: string | null;
  priority: string | null;
  dueAt: string;
  elapsedDays: number;
  remainingDays: number | null;
  overdueDays: number | null;
  /** true = past the target; false = approaching it. */
  isOverdue: boolean;
}

/**
 * GET /api/v1/dashboard/sla-alerts. Counts cover the whole scope even when
 * `items` is truncated, so a badge never under-reports.
 */
export interface ComplaintSlaAlerts {
  targetDays: number;
  overdueCount: number;
  warningCount: number;
  items: ComplaintSlaAlertItem[];
}

/** API-393 daily complaint trend from CM Aggregate (DEC-026). */
export interface DashboardTrendItem {
  date: string;
  count: number;
}

export interface DashboardTrends {
  period: string;
  items: DashboardTrendItem[];
}

/** API-320–322 System Settings (TASK-028). */
export type SettingValueType =
  | "STRING"
  | "INTEGER"
  | "BOOLEAN"
  | "JSON"
  | "URL"
  | "EMAIL";

export type SettingVisibility = "PUBLIC" | "PROTECTED";

export interface Setting {
  id: string;
  key: string;
  value: string;
  valueType: SettingValueType;
  category: string;
  visibility: SettingVisibility;
  description: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface SettingUpdateRequest {
  value: string;
}

/** API-324 attachment metadata (TASK-029 / TASK-032 viewer). */
export type AttachmentAggregateType =
  | "Complaint"
  | "Queue"
  | "Notification"
  | "Announcement"
  | "Knowledge"
  | "InternalComplaint";
export type AttachmentStatus =
  | "UPLOADED"
  | "AVAILABLE"
  | "DELETED"
  | "FAILED";

/** CAPABILITY-011 Attachment metadata (API-323–326, 386–387). */
export interface Attachment {
  id: string;
  aggregateType: AttachmentAggregateType;
  aggregateId: string;
  fileName: string;
  originalName: string;
  mimeType: string;
  extension: string | null;
  sizeBytes: number;
  checksumSha256: string;
  storageProvider: string;
  uploadedBy: string | null;
  uploadedAt: string;
  status: AttachmentStatus;
}

export interface Complaint {
  id: string;
  complaintNumber: string;
  customerId: string | null;
  branchId: string | null;
  sourceType?: string;
  sourceId?: string;
  targetType?: string;
  targetId?: string | null;
  subject: string;
  description: string;
  status: ComplaintStatus;
  priority: Priority;
  channel: string | null;
  category: string | null;
  reportedAt: string;
  closedAt: string | null;
  closedBy: string | null;
  closureNotes: string | null;
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

/** API-204 update payload — status is not mutable here. */
export interface ComplaintUpdateRequest {
  subject?: string;
  description?: string;
  priority?: Priority;
  channel?: string | null;
  category?: string | null;
  branchId?: string | null;
}

export type ComplaintSortField =
  | "createdAt"
  | "updatedAt"
  | "priority"
  | "status"
  | "slaDueDate";

export type SortOrder = "asc" | "desc";

export interface SearchPagination {
  page: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

export interface SearchSort {
  field: ComplaintSortField;
  order: SortOrder;
}

/** API-388 search filters (all optional / combinable). */
export interface ComplaintSearchParams {
  keyword?: string;
  status?: ComplaintStatus;
  priority?: Priority;
  category?: string;
  branchId?: string;
  assignedTo?: string;
  createdBy?: string;
  createdFrom?: string;
  createdTo?: string;
  slaStatus?: SlaStatus;
  escalated?: boolean;
  page?: number;
  pageSize?: number;
  sort?: ComplaintSortField;
  order?: SortOrder;
}

/** API-388 Complaint search envelope. */
export interface ComplaintSearchResponse {
  items: Complaint[];
  pagination: SearchPagination;
  filtersApplied: Record<string, unknown>;
  sort: SearchSort;
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

/** API-310 final resolution request. */
export interface FinalResolutionRequest {
  summary: string;
  notes: string;
  followUpRequired?: boolean;
}

/** API-310 submit response. */
export interface FinalResolutionResult {
  complaintId: string;
  status: "FINAL_RESOLUTION_SUBMITTED";
  submittedAt: string;
  submittedBy: string;
}

/** API-311 final resolution detail. */
export interface FinalResolutionDetail {
  complaintId: string;
  status: "FINAL_RESOLUTION_SUBMITTED";
  summary: string;
  notes: string;
  followUpRequired: boolean;
  submittedAt: string;
  submittedBy: string;
  submittedByName: string | null;
}

/** API-312 close request. */
export interface CloseComplaintRequest {
  notes: string;
}

/** API-312 close response. */
export interface CloseComplaintResult {
  complaintId: string;
  status: "CLOSED";
  closedAt: string;
  closedBy: string;
}

/** API-314 SLA dimension status. */
export type SlaStatus = "PENDING" | "ON_TIME" | "BREACHED" | "COMPLETED";

/** API-314 SLA record (immutable deadline snapshot; statuses PENDING). */
export interface SlaRecord {
  id: string;
  complaintId: string;
  assignmentDueAt: string | null;
  resolutionDueAt: string | null;
  appointmentDueAt: string | null;
  escalationDueAt: string | null;
  overallDueAt: string | null;
  assignmentStatus: SlaStatus;
  resolutionStatus: SlaStatus;
  appointmentStatus: SlaStatus;
  escalationStatus: SlaStatus;
  overallStatus: SlaStatus;
  createdAt: string;
  updatedAt: string;
}

/** API-315 / API-316 / API-317 SLA policy (targets only). */
export interface SlaPolicy {
  id: string;
  name: string;
  description: string | null;
  assignmentTargetMinutes: number;
  appointmentTargetMinutes: number;
  resolutionTargetMinutes: number;
  escalationTargetMinutes: number;
  overallTargetMinutes: number;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

/** API-316 create payload. */
export interface SlaPolicyCreateRequest {
  name: string;
  description?: string | null;
  assignmentTargetMinutes: number;
  appointmentTargetMinutes: number;
  resolutionTargetMinutes: number;
  escalationTargetMinutes: number;
  overallTargetMinutes: number;
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
  closedAt?: string | null;
  closedBy?: string | null;
  closureNotes?: string | null;
  activeAppointment?: AppointmentSummary | null;
}

/** API-313 close request. */
export interface CloseEscalationRequest {
  notes: string;
}

/** API-313 close response. */
export interface CloseEscalationResult {
  escalationId: string;
  status: "CLOSED";
  closedAt: string;
  closedBy: string;
}

/** API-305 / API-302 appointment summary. */
export interface AppointmentSummary {
  id: string;
  status: "BOOKED" | "CHECKED_IN" | "COMPLETED" | "NO_SHOW" | string;
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

/** API-308 completion result values. */
export type AppointmentCompletionResult =
  | "COMPLETED"
  | "PARTIALLY_COMPLETED";

/** API-308 complete request. */
export interface AppointmentCompleteRequest {
  result?: AppointmentCompletionResult;
  notes?: string | null;
}

/** API-308 slim complete response. */
export interface AppointmentCompleteResult {
  id: string;
  status: "COMPLETED";
  completionResult: AppointmentCompletionResult;
  completedAt: string;
  completedBy: string;
}

/** API-309 no-show request. */
export interface AppointmentNoShowRequest {
  reason?: string | null;
}

/** API-309 slim no-show response. */
export interface AppointmentNoShowResult {
  id: string;
  status: "NO_SHOW";
  noShowAt: string;
  noShowBy: string;
}

/** API-306 appointment detail. */
export interface Appointment {
  id: string;
  escalationId: string;
  appointmentDate: string;
  appointmentStartTime: string;
  appointmentEndTime: string;
  status: "BOOKED" | "CHECKED_IN" | "COMPLETED" | "NO_SHOW" | string;
  assignedEngineerId: string;
  assignedEngineerName: string | null;
  notes: string | null;
  checkedInAt: string | null;
  checkedInBy: string | null;
  checkinNotes: string | null;
  completedAt: string | null;
  completedBy: string | null;
  completionNotes: string | null;
  completionResult: string | null;
  noShowAt: string | null;
  noShowBy: string | null;
  noShowReason: string | null;
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
    | "complaint.appointment_completed"
    | "complaint.appointment_no_show"
    | "complaint.final_resolution_submitted"
    | "complaint.resolved"
    | "complaint.closed"
    | "escalation.closed"
    | "sla.assignment.completed"
    | "sla.assignment.breached"
    | "sla.appointment.completed"
    | "sla.appointment.breached"
    | "sla.resolution.completed"
    | "sla.resolution.breached"
    | "sla.escalation.completed"
    | "sla.escalation.breached"
    | "sla.overall.completed"
    | "sla.overall.breached";
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
  forcePasswordChange: boolean;
  lastLoginAt: string | null;
  createdAt: string;
  updatedAt: string;
  preferredLanguage?: string;
  roles: string[];
  permissions: string[];
}

/** API-410 */
export interface ForgotPasswordResponse {
  message: string;
}

/** API-411 */
export interface ResetPasswordResponse {
  message: string;
}

/** API-412 */
export interface ChangePasswordResponse {
  message: string;
}

/** API-413 — temporary password is returned once to the caller. */
export interface AdminResetPasswordResponse {
  userId: string;
  temporaryPassword: string;
  forcePasswordChange: boolean;
  message: string;
}

// --- Announcements (Pengumuman) ---

export type AnnouncementPriority = "NORMAL" | "IMPORTANT";
export type AnnouncementStatus = "DRAFT" | "PUBLISHED" | "ARCHIVED";
/** Derived, read-only — never stored. SCHEDULED = PUBLISHED with future startAt;
 * EXPIRED = PUBLISHED whose endAt has elapsed. */
export type AnnouncementEffectiveStatus =
  | AnnouncementStatus
  | "EXPIRED"
  | "SCHEDULED";

/**
 * IMMEDIATE = visible as soon as uploaded, even while the announcement is
 * still DRAFT. PUBLISHED (default, safest) = follows the announcement's own
 * status — only visible once the announcement is PUBLISHED.
 */
export type AnnouncementAttachmentVisibility = "IMMEDIATE" | "PUBLISHED";

/** Attachment as seen through an announcement — `id` is the underlying
 * platform attachment id, so /api/v1/attachments/{id}/... routes work
 * unchanged (download, preview). */
export interface AnnouncementAttachment {
  id: string;
  fileName: string;
  mimeType: string;
  sizeBytes: number;
  visibility: AnnouncementAttachmentVisibility;
  createdAt: string;
}

/** Reusable announcement-domain file for the link picker / catalog. */
export interface AnnouncementAttachmentLibraryItem {
  id: string;
  fileName: string;
  mimeType: string;
  sizeBytes: number;
  createdAt: string;
  accessLevel: "PUBLIC" | "PRIVATE";
  uploadedOrgUnitId: string | null;
  uploadedBy: string | null;
  uploadedByName: string | null;
  usageCount: number;
  /** Pinned by the caller — presentation only, scoped per user. */
  pinned: boolean;
}

export interface AnnouncementAttachmentLinkRequest {
  attachmentId: string;
  visibility: AnnouncementAttachmentVisibility;
}

export interface AnnouncementAttachmentAccessUpdateRequest {
  accessLevel: "PUBLIC" | "PRIVATE";
}

export interface Announcement {
  id: string;
  /** Human reference — PGM-YYMM-NNNN; allocated at create. */
  referenceNumber: string;
  title: string;
  body: string;
  priority: AnnouncementPriority;
  status: AnnouncementStatus;
  effectiveStatus: AnnouncementEffectiveStatus;
  startAt: string | null;
  endAt: string | null;
  publishedAt: string | null;
  publishedBy: string | null;
  createdBy: string | null;
  createdAt: string;
  updatedBy: string | null;
  updatedAt: string;
  /** Already filtered per-caller by the backend — never filter again in FE. */
  attachments: AnnouncementAttachment[];
  attachmentCount: number;
  /** Reader lists only — null on the management list. */
  isRead?: boolean | null;
}

export interface AnnouncementCreateRequest {
  title: string;
  body: string;
  priority: AnnouncementPriority;
  endAt?: string | null;
}

/** Optional publish body — omit / null startAt = publish now. */
export interface AnnouncementPublishRequest {
  startAt?: string | null;
}

/** Update may include startAt to reschedule; omit to leave schedule unchanged. */
export interface AnnouncementUpdateRequest extends AnnouncementCreateRequest {
  startAt?: string | null;
}

// --- Knowledge (Pengetahuan) ---

export type KnowledgeType =
  | "SOP"
  | "PERATURAN"
  | "SURAT_EDARAN"
  | "KEPUTUSAN"
  | "PANDUAN";
export type KnowledgeStatus = "DRAFT" | "ACTIVE" | "ARCHIVED";
export type KnowledgeFileRole = "PRIMARY" | "SUPPORTING";

/** File as seen through a Knowledge record — `id` is the underlying platform
 * attachment id, so /api/v1/attachments/{id}/... routes work unchanged
 * (download, preview). */
export interface KnowledgeFile {
  id: string;
  fileName: string;
  mimeType: string;
  sizeBytes: number;
  role: KnowledgeFileRole;
  createdAt: string;
}

export interface Knowledge {
  id: string;
  title: string;
  knowledgeType: KnowledgeType;
  status: KnowledgeStatus;
  documentNumber: string | null;
  summary: string | null;
  versionLabel: string | null;
  effectiveFrom: string | null;
  effectiveTo: string | null;
  ownerOrgUnitId: string | null;
  publishedAt: string | null;
  publishedBy: string | null;
  supersedesKnowledgeId: string | null;
  supersedesTitle: string | null;
  createdBy: string | null;
  createdAt: string;
  updatedBy: string | null;
  updatedAt: string;
  /** Post-publish edit window (DEC-030) — server-computed from `publishedAt`;
   * never derive this from the client clock. `editableUntil` is null when
   * DRAFT (no deadline) or already locked — read `editable` to tell those
   * two apart. */
  editable: boolean;
  editableUntil: string | null;
  /** Already access-filtered per-caller by the backend — never filter again in FE. */
  files: KnowledgeFile[];
}

export interface KnowledgeCreateRequest {
  title: string;
  knowledgeType: KnowledgeType;
  documentNumber?: string | null;
  summary?: string | null;
  versionLabel?: string | null;
  effectiveFrom?: string | null;
  effectiveTo?: string | null;
  supersedesKnowledgeId?: string | null;
}

export interface KnowledgeUpdateRequest {
  title: string;
  knowledgeType: KnowledgeType;
  documentNumber?: string | null;
  summary?: string | null;
  versionLabel?: string | null;
  effectiveFrom?: string | null;
  effectiveTo?: string | null;
}

export interface KnowledgeSearchParams {
  q?: string;
  type?: KnowledgeType;
  status?: KnowledgeStatus;
  /** `@` Knowledge Reference (Complaint Resolution) — always ACTIVE + within
   * the effective window, even for a knowledge:manage caller. */
  referenceOnly?: boolean;
  /** Max rows (referenceOnly is capped at 10 on the server). */
  limit?: number;
}

/** Citable (ACTIVE + in-window) counts for the `@` type picker. */
export type KnowledgeTypeCounts = Record<KnowledgeType, number>;

/** One row of the generic platform audit log, scoped to a Knowledge record
 * (entityType="Knowledge"). ``oldValues``/``newValues`` carry only the
 * fields that actually changed — see KnowledgeService._log. */
export interface KnowledgeHistoryEntry {
  id: string;
  /** "KnowledgeCreated" | "KnowledgeUpdated" | "KnowledgePublished" |
   * "KnowledgeArchived" | "KnowledgeUnarchived" | "KnowledgeDeleted" |
   * "KnowledgeFileUploaded" | "KnowledgeFileReplaced" |
   * "KnowledgeFilePrimaryChanged" | "KnowledgeFileRemoved" */
  eventType: string;
  action: "CREATE" | "UPDATE" | "DELETE" | "LOGIN" | "LOGOUT" | "EXPORT" | "IMPORT";
  actorId: string | null;
  actorName: string | null;
  oldValues: Record<string, unknown> | null;
  newValues: Record<string, unknown> | null;
  /** DEC-030: `{ postPublish: true, statusAtChange, editableUntil }` set on
   * any change made after publication — lets the UI flag entries made in
   * the post-publish grace window. Null on a DRAFT-time change. */
  metadata: Record<string, unknown> | null;
  createdAt: string;
}
