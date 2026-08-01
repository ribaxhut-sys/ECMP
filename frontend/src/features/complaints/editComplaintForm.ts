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

/** Client-side validation aligned with ComplaintUpdateRequest (API-204). Returns i18n keys. */
export function validateEditComplaintForm(
  values: EditComplaintFormValues,
): EditComplaintFieldErrors {
  const errors: EditComplaintFieldErrors = {};

  const subject = values.subject.trim();
  if (!subject) {
    errors.subject = "subjectRequired";
  } else if (subject.length > 200) {
    errors.subject = "subjectMax";
  }

  const description = values.description.trim();
  if (!description) {
    errors.description = "descriptionRequired";
  } else if (description.length > 5000) {
    errors.description = "descriptionMax";
  }

  if (!values.priority) {
    errors.priority = "priorityRequired";
  }

  const branchId = values.branchId.trim();
  if (branchId && !UUID_RE.test(branchId)) {
    errors.branchId = "branchIdInvalid";
  }

  const channel = values.channel.trim();
  if (channel.length > 32) {
    errors.channel = "channelMax";
  }

  const category = values.category.trim();
  if (category.length > 64) {
    errors.category = "categoryMax";
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
