import { apiRequest } from "./client";
import type { ListResponse } from "./types";

export interface Customer {
  id: string;
  externalCustomerId: string;
  fullName: string;
  email: string | null;
  phone: string | null;
}

export function fetchCustomers(
  pageSize = 100,
  q?: string,
): Promise<ListResponse<Customer>> {
  const params = new URLSearchParams({
    page: "1",
    pageSize: String(pageSize),
  });
  if (q?.trim()) params.set("q", q.trim());
  return apiRequest<ListResponse<Customer>>(
    `/api/v1/customers?${params.toString()}`,
  );
}
