import { redirect } from "next/navigation";
import { FOUNDATION_RETIRED_CASES_HREF } from "@/features/complaints/foundationRetiredRedirect";

/** DEC-026 M-026-1 — Foundation assignments list is not a product door. */
export default function AssignmentsPage() {
  redirect(FOUNDATION_RETIRED_CASES_HREF);
}
