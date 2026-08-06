import { apiRequest } from "./client";
import type { DataResponse, ListResponse } from "./types";

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

/** Mode A lab — local customers cache phone only (not Customer Master SoR). */
export async function updateCustomerPhone(
  customerId: string,
  phone: string,
): Promise<Customer> {
  const body = await apiRequest<DataResponse<Customer>>(
    `/api/v1/customers/${customerId}`,
    {
      method: "PATCH",
      body: JSON.stringify({ phone }),
    },
  );
  return body.data;
}
