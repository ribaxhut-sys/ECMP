import type {
  AnnouncementCreateRequest,
  AnnouncementPriority,
  AnnouncementUpdateRequest,
} from "@/lib/api/types";

export interface AnnouncementFormValues {
  title: string;
  body: string;
  priority: AnnouncementPriority;
  /** datetime-local — when Publish is pressed, used as startAt ("" = now). */
  startAt: string;
  /** datetime-local input value ("" = no expiry). */
  endAt: string;
}

export type AnnouncementFieldErrors = Partial<
  Record<keyof AnnouncementFormValues, string>
>;

export function createEmptyAnnouncementForm(): AnnouncementFormValues {
  return {
    title: "",
    body: "",
    priority: "NORMAL",
    startAt: "",
    endAt: "",
  };
}

export function announcementFormFromExisting(input: {
  title: string;
  body: string;
  priority: AnnouncementPriority;
  startAt?: string | null;
  endAt: string | null;
}): AnnouncementFormValues {
  return {
    title: input.title,
    body: input.body,
    priority: input.priority,
    startAt: input.startAt ? toDatetimeLocalValue(input.startAt) : "",
    endAt: input.endAt ? toDatetimeLocalValue(input.endAt) : "",
  };
}

/** ISO 8601 → "YYYY-MM-DDTHH:mm" for a native datetime-local input. */
function toDatetimeLocalValue(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function validateAnnouncementForm(
  values: AnnouncementFormValues,
): AnnouncementFieldErrors {
  const errors: AnnouncementFieldErrors = {};

  if (!values.title.trim()) {
    errors.title = "required";
  } else if (values.title.trim().length > 200) {
    errors.title = "announcementTitleMax";
  }

  if (!values.body.trim()) {
    errors.body = "required";
  }

  let startDate: Date | null = null;
  if (values.startAt) {
    startDate = new Date(values.startAt);
    if (Number.isNaN(startDate.getTime())) {
      errors.startAt = "announcementStartAtInvalid";
      startDate = null;
    }
  }

  let endDate: Date | null = null;
  if (values.endAt) {
    endDate = new Date(values.endAt);
    if (Number.isNaN(endDate.getTime())) {
      errors.endAt = "announcementEndAtInvalid";
      endDate = null;
    }
  }

  if (startDate && endDate && startDate >= endDate) {
    errors.startAt = "announcementStartBeforeEnd";
  }

  return errors;
}

export function toAnnouncementCreateRequest(
  values: AnnouncementFormValues,
): AnnouncementCreateRequest {
  return {
    title: values.title.trim(),
    body: values.body.trim(),
    priority: values.priority,
    endAt: values.endAt ? new Date(values.endAt).toISOString() : null,
  };
}

/** Body for update — include startAt when editing a scheduled announcement. */
export function toAnnouncementUpdateRequest(
  values: AnnouncementFormValues,
  opts?: { includeStartAt?: boolean },
): AnnouncementUpdateRequest {
  const base = toAnnouncementCreateRequest(values);
  if (!opts?.includeStartAt) return base;
  return {
    ...base,
    startAt: values.startAt.trim()
      ? new Date(values.startAt).toISOString()
      : null,
  };
}

/** Body for publish — empty startAt means publish now (omit startAt). */
export function toAnnouncementPublishRequest(
  startAtLocal: string,
): { startAt: string } | undefined {
  if (!startAtLocal.trim()) return undefined;
  return { startAt: new Date(startAtLocal).toISOString() };
}
