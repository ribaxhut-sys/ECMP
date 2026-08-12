export {
  ApiError,
  apiRequest,
  apiRequestBlob,
  axiosClient,
  getAuthToken,
  setAuthToken,
  subscribeApiErrors,
  subscribeLoading,
} from "./client";
export type { ApiBlobResult, ApiRequestInit } from "./client";
export {
  fetchCurrentUser,
  login,
  logout,
  refreshAccessToken,
} from "./auth";
export {
  assignComplaint,
  changeComplaintStatus,
  closeComplaint,
  createComplaint,
  fetchComplaint,
  fetchComplaintAssignments,
  fetchComplaintResolution,
  fetchComplaintTimeline,
  fetchComplaintSla,
  fetchFinalResolution,
  fetchLatestComplaints,
  resolveComplaint,
  searchComplaints,
  submitFinalResolution,
  updateComplaint,
} from "./complaints";
export {
  approveEscalation,
  closeEscalation,
  fetchComplaintEscalations,
  fetchEscalation,
  rejectEscalation,
  requestEscalation,
} from "./escalations";
export {
  bookAppointment,
  checkInAppointment,
  completeAppointment,
  fetchAppointment,
  markAppointmentNoShow,
} from "./appointments";
export { fetchBranches } from "./branches";
export type { Branch } from "./branches";
export { fetchCustomers, updateCustomerPhone } from "./customers";
export type { Customer } from "./customers";
export {
  createUser,
  fetchUsers,
  updateUserRole,
  updateUserStatus,
} from "./users";
export type { UserRef, CreateUserPayload } from "./users";
export { fetchRoles } from "./roles";
export type { RoleRef } from "./roles";
export {
  fetchReportByBranch,
  fetchReportByStatus,
  fetchReportSummary,
} from "./reports";
export { fetchKpiSummary } from "./kpi";
export type { KpiSummaryFilters } from "./kpi";
export {
  fetchDashboardAggregateKpis,
  fetchDashboardRecentActivity,
  fetchDashboardSummary,
  fetchDashboardTrends,
} from "./dashboard";
export {
  fetchQueueAssignments,
  fetchQueueList,
  fetchQueueSla,
  fetchQueueSummary,
  releaseQueue,
  takeQueue,
  updateQueueStatus,
} from "./queue";
export {
  assignComplaintHandler,
  cancelAssignment,
  fetchAssignmentHistory,
  fetchAssignmentsList,
  reassignComplaintHandler,
} from "./assignments";
export {
  closeComplaintFromResolution,
  closeEscalationForComplaint,
  fetchFinalResolutionDetail,
  fetchResolution,
  fetchResolutionAssignee,
  fetchResolutionEscalations,
  fetchResolutionsList,
  requestEscalationForComplaint,
  submitFinalResolutionForComplaint,
  submitResolution,
} from "./resolutions";
export {
  activateSlaPolicy,
  createSlaPolicy,
  fetchSlaPolicies,
} from "./sla";
export {
  createAnnouncement,
  deleteAnnouncement,
  fetchActiveAnnouncements,
  fetchAnnouncement,
  fetchAnnouncementHistory,
  fetchAnnouncements,
  fetchHasUnreadAnnouncements,
  markAnnouncementRead,
  publishAnnouncement,
  removeAnnouncementAttachment,
  unpublishAnnouncement,
  updateAnnouncement,
  updateAnnouncementAttachmentVisibility,
  uploadAnnouncementAttachment,
  uploadAnnouncementAttachmentToCatalog,
  fetchAnnouncementAttachmentLibrary,
  linkAnnouncementAttachment,
  updateAnnouncementAttachmentAccess,
  deleteAnnouncementAttachmentFromCatalog,
} from "./announcements";
export {
  archiveKnowledge,
  createKnowledge,
  deleteKnowledge,
  fetchKnowledge,
  fetchKnowledgeHistory,
  publishKnowledge,
  removeKnowledgeFile,
  searchKnowledge,
  setPrimaryKnowledgeFile,
  unarchiveKnowledge,
  updateKnowledge,
  uploadKnowledgeFile,
} from "./knowledge";
export {
  fetchPublicSettings,
  fetchSettings,
  updateSetting,
} from "./settings";
export {
  downloadAttachment,
  fetchAttachment,
  fetchComplaintAttachments,
  uploadAttachment,
} from "./attachments";
export type { AttachmentDownloadResult } from "./attachments";
export {
  CM_BATCH1_BASE,
  buildCmBatch1CreateHeaders,
  checkCmBatch1Duplicates,
  cmBatch1Paths,
  confirmCmBatch1Customer,
  createCmBatch1Complaint,
  decideCmBatch1IntakeEscalation,
  requestCmBatch1IntakeEscalation,
  acceptCmBatch1HqEscalation,
  acceptAndScheduleCmBatch1HqEscalation,
  returnCmBatch1HqEscalation,
  scheduleCmBatch1HqArrival,
  fetchCmBatch1Complaint,
  fetchCmBatch1ComplaintHistory,
  fetchCmBatch1Complaints,
  fetchCmBatch1Customer360,
  fetchCmBatch1UserWorkStats,
  recordCmBatch1DuplicateDecision,
  searchCmBatch1Customer,
  transferCmBatch1Attachments,
  uploadCmBatch1Attachment,
  fetchCmBatch1ComplaintAttachments,
  fetchCmBatch1SupervisorQueue,
  voidCmBatch1Attachment,
} from "./cmBatch1";
export type {
  CmBatch1AgingComplaintItem,
  CmBatch1AttachmentClassification,
  CmBatch1AttachmentResponse,
  CmBatch1AttachmentStatus,
  CmBatch1ComplaintResponse,
  CmBatch1ComplaintBrief,
  CmBatch1ConfirmCustomerRequest,
  CmBatch1ConfirmCustomerResponse,
  CmBatch1CreateComplaintOptions,
  CmBatch1CreateComplaintRequest,
  CmBatch1Customer360Response,
  CmBatch1CustomerCandidate,
  CmBatch1CustomerSearchRequest,
  CmBatch1CustomerSearchResponse,
  CmBatch1DuplicateCheckRequest,
  CmBatch1DuplicateCheckResponse,
  CmBatch1DuplicateDecision,
  CmBatch1DuplicateDecisionRequest,
  CmBatch1DuplicateDecisionResponse,
  CmBatch1HistoryEventCode,
  CmBatch1IntakeEscalationDecisionRequest,
  CmBatch1IntakeEscalationRequestBody,
  CmBatch1IntakeHistoryEntry,
  CmBatch1HqAcceptRequest,
  CmBatch1HqAcceptAndScheduleRequest,
  CmBatch1HqReturnReasonCode,
  CmBatch1HqReturnRequest,
  CmBatch1HqScheduleArrivalRequest,
  CmBatch1LaterReviewWorkItem,
  CmBatch1SupervisorQueueQuery,
  CmBatch1SupervisorQueueResponse,
  CmBatch1TransferAttachmentsRequest,
  CmBatch1TransferAttachmentsResponse,
  CmBatch1UserWorkStats,
  CmBatch1VerificationStatus,
  UploadCmBatch1AttachmentInput,
} from "./cmBatch1";
export {
  CM_BATCH1_AGGREGATE_BASE,
  FOUNDATION_COMPLAINTS_BASE,
  dualSotNamespaceOf,
  isCmBatch1AggregatePath,
  isFoundationComplaintsPath,
} from "./dualSotNamespaces";
export {
  CM_CASE_BASE,
  addCmCase,
  buildCmCaseMutateHeaders,
  closeCmCase,
  cmCasePaths,
  createCmCase,
  fetchCmCase,
  fetchCmCases,
  recordCmCaseAcceptance,
  resolveCmCase,
  updateCmCaseStatus,
} from "./cmCase";
export type {
  AddCmCaseRequest,
  CloseCmCaseRequest,
  CmCase,
  CmCaseAcceptanceDecision,
  CmCaseAcceptanceParty,
  CmCaseCancelReason,
  CmCaseMutateOptions,
  CmCaseResolution,
  CmCaseResolveAction,
  CmCaseStatus,
  CmCaseSummary,
  CreateCmCaseRequest,
  RecordCmCaseAcceptanceRequest,
  ResolveCmCaseRequest,
  UpdateCmCaseStatusRequest,
} from "./cmCase";
export {
  INTERNAL_COMPLAINTS_BASE,
  closeInternalComplaint,
  createInternalComplaint,
  fetchInternalComplaint,
  fetchInternalComplaints,
  internalComplaintPaths,
  receiveInternalComplaint,
  recordInternalAcceptance,
  resolveInternalComplaint,
  transferInternalComplaint,
} from "./internalComplaints";
export type {
  CreateInternalComplaintRequest,
  InternalAcceptance,
  InternalAcceptanceDecision,
  InternalAcceptanceParty,
  InternalComplaint,
  InternalComplaintStatus,
  InternalComplaintSummary,
  InternalHistoryEvent,
  InternalResolution,
  InternalResolveAction,
  RecordInternalAcceptanceRequest,
  ResolveInternalComplaintRequest,
  TransferInternalComplaintRequest,
} from "./internalComplaints";
export type * from "./types";
