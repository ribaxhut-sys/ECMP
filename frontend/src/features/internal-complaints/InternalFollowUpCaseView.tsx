"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export function InternalFollowUpCaseView({ id }: { id: string }) {
  const router = useRouter();
  useEffect(() => {
    router.replace(`/internal/complaints/${encodeURIComponent(id)}`);
  }, [id, router]);
  return null;
}
