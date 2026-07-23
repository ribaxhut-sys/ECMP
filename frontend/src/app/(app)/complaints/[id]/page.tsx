"use client";

import { use } from "react";
import { ComplaintDetailView } from "@/features/complaints";

export default function ComplaintDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  return <ComplaintDetailView complaintId={id} />;
}
