"use client";

import { use } from "react";
import { InternalFollowUpCaseView } from "@/features/internal-complaints";

export default function InternalFollowUpCasePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  return <InternalFollowUpCaseView id={id} />;
}
