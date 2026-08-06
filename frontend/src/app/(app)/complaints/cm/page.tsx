import { redirect } from "next/navigation";

/** Compat: Aggregate list lives at `/complaints`; keep old `/complaints/cm` bookmarks working. */
export default function CmBatch1ComplaintListRedirectPage() {
  redirect("/complaints");
}
