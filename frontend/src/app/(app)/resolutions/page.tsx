import { redirect } from "next/navigation";
import { FOUNDATION_RETIRED_CASES_HREF } from "@/features/complaints/foundationRetiredRedirect";

/** DEC-026 M-026-1 — Foundation resolutions list is not a product door. */
export default function ResolutionsPage() {
  redirect(FOUNDATION_RETIRED_CASES_HREF);
}
