import { redirect } from "next/navigation";
import { isShellUiBatch } from "@/shared/config/uiBatch";

/**
 * Root entry. Shell batches (B0/B1) → Workspace Entry Point (auth gate on (app) layout).
 * Default lab/prod → dashboard.
 */
export default function HomePage() {
  if (isShellUiBatch()) {
    redirect("/workspace");
  }
  redirect("/dashboard");
}
