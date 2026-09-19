/** Deep-link: `/complaints/new?mode=add-case&complaintId=…` (FR-002 Add Case). */

export const ADD_CASE_QUERY_MODE = "add-case";

/** Matches backend BQ-003 / MAX_CASES_PER_COMPLAINT. */
export const MAX_CASES_PER_COMPLAINT = 5;

export function isAddCaseMode(mode: string | null | undefined): boolean {
  return (mode || "").trim().toLowerCase() === ADD_CASE_QUERY_MODE;
}

export function addCaseToComplaintHref(complaintId: string): string {
  const id = complaintId.trim();
  const qs = new URLSearchParams({
    mode: ADD_CASE_QUERY_MODE,
    complaintId: id,
  });
  return `/complaints/new?${qs.toString()}`;
}
