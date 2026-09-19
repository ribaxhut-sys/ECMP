import { redirect } from "next/navigation";
import { FOUNDATION_RETIRED_LIST_HREF } from "@/features/complaints/foundationRetiredRedirect";

/** DEC-026 M-026-1 — Foundation edit is not a product door. */
export default function EditComplaintPage() {
  redirect(FOUNDATION_RETIRED_LIST_HREF);
}
