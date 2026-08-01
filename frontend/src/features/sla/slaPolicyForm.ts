import type { SlaPolicyCreateRequest } from "@/lib/api/types";

export interface SlaPolicyFormValues {
  name: string;
  description: string;
  assignmentTargetMinutes: string;
  appointmentTargetMinutes: string;
  resolutionTargetMinutes: string;
  escalationTargetMinutes: string;
  overallTargetMinutes: string;
}

export type SlaPolicyFieldErrors = Partial<
  Record<keyof SlaPolicyFormValues, string>
>;

export function createEmptySlaPolicyForm(): SlaPolicyFormValues {
  return {
    name: "",
    description: "",
    assignmentTargetMinutes: "60",
    appointmentTargetMinutes: "1440",
    resolutionTargetMinutes: "2880",
    escalationTargetMinutes: "480",
    overallTargetMinutes: "4320",
  };
}

function parsePositiveInt(raw: string): string | null {
  const trimmed = raw.trim();
  if (!trimmed) return "required";
  if (!/^\d+$/.test(trimmed)) return "fieldWholeNumber";
  const value = Number(trimmed);
  if (!Number.isFinite(value) || value < 1) {
    return "fieldAtLeast";
  }
  return null;
}

export function validateSlaPolicyForm(
  values: SlaPolicyFormValues,
): SlaPolicyFieldErrors {
  const errors: SlaPolicyFieldErrors = {};

  const name = values.name.trim();
  if (!name) {
    errors.name = "policyNameRequired";
  } else if (name.length > 100) {
    errors.name = "policyNameMax";
  }

  const fields: Array<keyof SlaPolicyFormValues> = [
    "assignmentTargetMinutes",
    "appointmentTargetMinutes",
    "resolutionTargetMinutes",
    "escalationTargetMinutes",
    "overallTargetMinutes",
  ];

  for (const field of fields) {
    const message = parsePositiveInt(values[field]);
    if (message) errors[field] = message;
  }

  return errors;
}

export function toSlaPolicyCreateRequest(
  values: SlaPolicyFormValues,
): SlaPolicyCreateRequest {
  const description = values.description.trim();
  return {
    name: values.name.trim(),
    description: description || null,
    assignmentTargetMinutes: Number(values.assignmentTargetMinutes.trim()),
    appointmentTargetMinutes: Number(values.appointmentTargetMinutes.trim()),
    resolutionTargetMinutes: Number(values.resolutionTargetMinutes.trim()),
    escalationTargetMinutes: Number(values.escalationTargetMinutes.trim()),
    overallTargetMinutes: Number(values.overallTargetMinutes.trim()),
  };
}
