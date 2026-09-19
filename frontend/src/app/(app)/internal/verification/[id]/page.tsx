"use client";

import { use } from "react";
import { InternalVerificationCaseView } from "@/features/internal-complaints";

export default function InternalVerificationCasePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  return <InternalVerificationCaseView id={id} />;
}
