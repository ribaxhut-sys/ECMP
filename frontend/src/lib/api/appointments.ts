import { apiRequest } from "./client";
import type {
  Appointment,
  AppointmentBookResult,
  AppointmentCreate,
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
