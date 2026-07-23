export { ApiError, apiRequest, getAuthToken, setAuthToken } from "./client";
export {
  fetchCurrentUser,
  login,
  logout,
  refreshAccessToken,
} from "./auth";
export {
  assignComplaint,
  changeComplaintStatus,
  createComplaint,
  fetchComplaint,
  fetchComplaintAssignments,
  fetchComplaintResolution,
  fetchComplaintTimeline,
  fetchLatestComplaints,
  resolveComplaint,
} from "./complaints";
export {
  approveEscalation,
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
export type * from "./types";
