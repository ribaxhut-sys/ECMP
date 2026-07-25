import type { Complaint, ComplaintUpdateRequest, Priority } from "@/lib/api/types";
import {
  CHANNEL_OPTIONS,
  PRIORITY_OPTIONS,
} from "./createComplaintForm";

export interface EditComplaintFormValues {
  subject: string;
  description: string;
  priority: Priority | "";
  branchId: string;
  channel: string;
  category: string;
}

export type EditComplaintFieldErrors = Partial<
  Record<keyof EditComplaintFormValues, string>
>;

export { CHANNEL_OPTIONS, PRIORITY_OPTIONS };

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function formFromComplaint(complaint: Complaint): EditComplaintFormValues {
  return {
    subject: complaint.subject ?? "",
    description: complaint.description ?? "",
    priority: complaint.priority ?? "",
    branchId: complaint.branchId ?? "",
    channel: complaint.channel ?? "",
    category: complaint.category ?? "",
  };
}

/** Client-side validation aligned with ComplaintUpdateRequest (API-204). */
export function validateEditComplaintForm(
  values: EditComplaintFormValues,
): EditComplaintFieldErrors {
  const errors: EditComplaintFieldErrors = {};

  const subject = values.subject.trim();
  if (!subject) {
    errors.subject = "Subject is required.";
  } else if (subject.length > 200) {
    errors.subject = "Subject must be 200 characters or fewer.";
  }

  const description = values.description.trim();
  if (!description) {
    errors.description = "Description is required.";
  } else if (description.length > 5000) {
    errors.description = "Description must be 5000 characters or fewer.";
  }

  if (!values.priority) {
    errors.priority = "Priority is required.";
  }

  const branchId = values.branchId.trim();
  if (branchId && !UUID_RE.test(branchId)) {
    errors.branchId = "Selected branch ID is invalid.";
  }

  const channel = values.channel.trim();
  if (channel.length > 32) {
    errors.channel = "Channel must be 32 characters or fewer.";
  }

  const category = values.category.trim();
  if (category.length > 64) {
    errors.category = "Category must be 64 characters or fewer.";
  }

  return errors;
}

export function toUpdateComplaintRequest(
  values: EditComplaintFormValues,
): ComplaintUpdateRequest {
  const channel = values.channel.trim();
  const category = values.category.trim();
  const branchId = values.branchId.trim();

  return {
    subject: values.subject.trim(),
    description: values.description.trim(),
    priority: values.priority as Priority,
    channel: channel || null,
    category: category || null,
    branchId: branchId || null,
  };
}
