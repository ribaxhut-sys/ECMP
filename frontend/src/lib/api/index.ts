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
export { fetchCustomers } from "./customers";
export type { Customer } from "./customers";
export { fetchUsers } from "./users";
export type { UserRef } from "./users";
export {
  fetchReportByBranch,
  fetchReportByStatus,
  fetchReportSummary,
} from "./reports";
export { fetchKpiSummary } from "./kpi";
export type { KpiSummaryFilters } from "./kpi";
export { fetchDashboardSummary } from "./dashboard";
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
  activateSlaPolicy,
  createSlaPolicy,
  fetchSlaPolicies,
} from "./sla";
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
export type * from "./types";
