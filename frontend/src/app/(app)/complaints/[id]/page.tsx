import { redirect } from "next/navigation";
import { FOUNDATION_RETIRED_LIST_HREF } from "@/features/complaints/foundationRetiredRedirect";

/** DEC-026 M-026-1 — Foundation detail is not mapped to CM (H1). */
export default function ComplaintDetailPage() {
  redirect(FOUNDATION_RETIRED_LIST_HREF);
}
