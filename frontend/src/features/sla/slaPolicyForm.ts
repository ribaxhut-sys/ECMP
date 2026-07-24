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

function parsePositiveInt(raw: string, label: string): string | null {
  const trimmed = raw.trim();
  if (!trimmed) return `${label} is required.`;
  if (!/^\d+$/.test(trimmed)) return `${label} must be a whole number.`;
  const value = Number(trimmed);
  if (!Number.isFinite(value) || value < 1) {
    return `${label} must be at least 1.`;
  }
  return null;
}

export function validateSlaPolicyForm(
  values: SlaPolicyFormValues,
): SlaPolicyFieldErrors {
  const errors: SlaPolicyFieldErrors = {};

  const name = values.name.trim();
  if (!name) {
    errors.name = "Name is required.";
  } else if (name.length > 100) {
    errors.name = "Name must be 100 characters or fewer.";
  }

  const fields: Array<{
    key: keyof SlaPolicyFormValues;
    label: string;
  }> = [
    { key: "assignmentTargetMinutes", label: "Assignment target" },
    { key: "appointmentTargetMinutes", label: "Appointment target" },
    { key: "resolutionTargetMinutes", label: "Resolution target" },
    { key: "escalationTargetMinutes", label: "Escalation target" },
    { key: "overallTargetMinutes", label: "Overall target" },
  ];

  for (const field of fields) {
    const message = parsePositiveInt(values[field.key], field.label);
    if (message) errors[field.key] = message;
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

export function formatTargetMinutes(minutes: number): string {
  if (minutes < 60) return `${minutes} min`;
  if (minutes % 60 === 0) {
    const hours = minutes / 60;
    return hours === 1 ? "1 hr" : `${hours} hrs`;
  }
  return `${minutes} min`;
}
