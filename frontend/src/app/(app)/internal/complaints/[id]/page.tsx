"use client";

import { use } from "react";
import { InternalComplaintDetailView } from "@/features/internal-complaints";

export default function InternalComplaintDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  return <InternalComplaintDetailView id={id} />;
}
