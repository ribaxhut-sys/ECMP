import { redirect } from "next/navigation";
import { cmCompatListRedirectHref } from "@/features/complaints/cmListRedirect";

/** Compat: Aggregate list lives at `/complaints`; keep old `/complaints/cm` bookmarks working. */
export default async function CmBatch1ComplaintListRedirectPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  redirect(cmCompatListRedirectHref(await searchParams));
}
