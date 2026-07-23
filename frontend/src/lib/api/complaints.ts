import { apiRequest } from "./client";
import type { Complaint, ListResponse } from "./types";

export function fetchLatestComplaints(
  pageSize = 10,
): Promise<ListResponse<Complaint>> {
  const params = new URLSearchParams({
    page: "1",
    pageSize: String(pageSize),
  });
  return apiRequest<ListResponse<Complaint>>(
    `/api/v1/complaints?${params.toString()}`,
  );
}
