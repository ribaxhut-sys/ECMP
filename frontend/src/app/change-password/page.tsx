import { redirect } from "next/navigation";
import { PASSWORD_CHANGE_ROUTE } from "@/features/auth";

/** Legacy route — redirect to the canonical password-change page. */
export default function ChangePasswordRedirectPage() {
  redirect(PASSWORD_CHANGE_ROUTE);
}
