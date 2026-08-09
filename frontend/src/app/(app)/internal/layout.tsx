import type { ReactNode } from "react";
import { redirect } from "next/navigation";
import { isInternalComplaintsUiEnabled } from "@/shared/config/internalComplaintsUi";

/**
 * Deep-link guard: routes under /internal stay in the tree for lab review,
 * but redirect when the prototype flag is off (default).
 */
export default function InternalLayout({
  children,
}: {
  children: ReactNode;
}) {
  if (!isInternalComplaintsUiEnabled()) {
    redirect("/dashboard");
  }
  return children;
}
