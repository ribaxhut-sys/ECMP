"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

/**
 * Legacy priority step. Intake decisions now live on `/complaints/new`.
 */
export function EscalateIntakeView() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/complaints/new");
  }, [router]);
  return null;
}
