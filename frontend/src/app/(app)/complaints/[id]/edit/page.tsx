"use client";

import { use } from "react";
import { EditComplaintView } from "@/features/complaints";

export default function EditComplaintPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  return <EditComplaintView complaintId={id} />;
}
