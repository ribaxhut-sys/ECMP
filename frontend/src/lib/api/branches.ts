import { apiRequest } from "./client";
import type { ListResponse } from "./types";

/** API-223 — branch reference row for Create Complaint selection. */
export interface Branch {
  id: string;
  code: string;
  name: string;
}

export function fetchBranches(
  pageSize = 100,
  q?: string,
): Promise<ListResponse<Branch>> {
  const params = new URLSearchParams({
    page: "1",
    pageSize: String(pageSize),
  });
  if (q?.trim()) params.set("q", q.trim());
  return apiRequest<ListResponse<Branch>>(
    `/api/v1/branches?${params.toString()}`,
  );
}
