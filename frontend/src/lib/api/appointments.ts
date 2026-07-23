import { apiRequest } from "./client";
import type {
  Appointment,
  AppointmentBookResult,
  AppointmentCheckInRequest,
  AppointmentCheckInResult,
  AppointmentCompleteRequest,
  AppointmentCompleteResult,
  AppointmentCreate,
  AppointmentNoShowRequest,
  AppointmentNoShowResult,
  DataResponse,
} from "./types";

/** API-305 — POST /api/v1/escalations/{id}/appointments */
export function bookAppointment(
  escalationId: string,
  body: AppointmentCreate,
): Promise<DataResponse<AppointmentBookResult>> {
  return apiRequest<DataResponse<AppointmentBookResult>>(
    `/api/v1/escalations/${encodeURIComponent(escalationId)}/appointments`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}

/** API-306 — GET /api/v1/appointments/{id} */
export function fetchAppointment(
  id: string,
): Promise<DataResponse<Appointment>> {
  return apiRequest<DataResponse<Appointment>>(
    `/api/v1/appointments/${encodeURIComponent(id)}`,
  );
}

/** API-307 — POST /api/v1/appointments/{id}/check-in */
export function checkInAppointment(
  id: string,
  body: AppointmentCheckInRequest = {},
): Promise<DataResponse<AppointmentCheckInResult>> {
  return apiRequest<DataResponse<AppointmentCheckInResult>>(
    `/api/v1/appointments/${encodeURIComponent(id)}/check-in`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}

/** API-308 — POST /api/v1/appointments/{id}/complete */
export function completeAppointment(
  id: string,
  body: AppointmentCompleteRequest = {},
): Promise<DataResponse<AppointmentCompleteResult>> {
  return apiRequest<DataResponse<AppointmentCompleteResult>>(
    `/api/v1/appointments/${encodeURIComponent(id)}/complete`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}

/** API-309 — POST /api/v1/appointments/{id}/no-show */
export function markAppointmentNoShow(
  id: string,
  body: AppointmentNoShowRequest = {},
): Promise<DataResponse<AppointmentNoShowResult>> {
  return apiRequest<DataResponse<AppointmentNoShowResult>>(
    `/api/v1/appointments/${encodeURIComponent(id)}/no-show`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}
