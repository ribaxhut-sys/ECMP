import { describe, expect, it } from "vitest";
import {
  announcementFormFromExisting,
  createEmptyAnnouncementForm,
  toAnnouncementCreateRequest,
  toAnnouncementPublishRequest,
  toAnnouncementUpdateRequest,
  validateAnnouncementForm,
} from "./announcementForm";

describe("createEmptyAnnouncementForm", () => {
  it("defaults to NORMAL priority with no start/expiry", () => {
    const values = createEmptyAnnouncementForm();
    expect(values.priority).toBe("NORMAL");
    expect(values.startAt).toBe("");
    expect(values.endAt).toBe("");
  });
});

describe("validateAnnouncementForm", () => {
  it("requires a title", () => {
    const errors = validateAnnouncementForm({
      ...createEmptyAnnouncementForm(),
      title: "   ",
      body: "Isi valid",
    });
    expect(errors.title).toBe("required");
  });

  it("requires a body", () => {
    const errors = validateAnnouncementForm({
      ...createEmptyAnnouncementForm(),
      title: "Judul valid",
      body: "  ",
    });
    expect(errors.body).toBe("required");
  });

  it("rejects a title over 200 characters", () => {
    const errors = validateAnnouncementForm({
      ...createEmptyAnnouncementForm(),
      title: "a".repeat(201),
      body: "Isi valid",
    });
    expect(errors.title).toBe("announcementTitleMax");
  });

  it("accepts a well-formed form with no expiry", () => {
    const errors = validateAnnouncementForm({
      ...createEmptyAnnouncementForm(),
      title: "Judul",
      body: "Isi",
    });
    expect(errors).toEqual({});
  });

  it("rejects an unparsable end date", () => {
    const errors = validateAnnouncementForm({
      ...createEmptyAnnouncementForm(),
      title: "Judul",
      body: "Isi",
      endAt: "not-a-date",
    });
    expect(errors.endAt).toBe("announcementEndAtInvalid");
  });

  it("rejects an unparsable start date", () => {
    const errors = validateAnnouncementForm({
      ...createEmptyAnnouncementForm(),
      title: "Judul",
      body: "Isi",
      startAt: "not-a-date",
    });
    expect(errors.startAt).toBe("announcementStartAtInvalid");
  });

  it("rejects startAt that is not before endAt", () => {
    const errors = validateAnnouncementForm({
      ...createEmptyAnnouncementForm(),
      title: "Judul",
      body: "Isi",
      startAt: "2026-12-31T12:00",
      endAt: "2026-12-31T11:00",
    });
    expect(errors.startAt).toBe("announcementStartBeforeEnd");
  });
});

describe("toAnnouncementCreateRequest", () => {
  it("trims title/body and never sets a status field (publish is separate)", () => {
    const request = toAnnouncementCreateRequest({
      title: "  Judul  ",
      body: "  Isi  ",
      priority: "IMPORTANT",
      startAt: "",
      endAt: "",
    });
    expect(request.title).toBe("Judul");
    expect(request.body).toBe("Isi");
    expect(request.priority).toBe("IMPORTANT");
    expect(request.endAt).toBeNull();
    expect(request).not.toHaveProperty("status");
    expect(request).not.toHaveProperty("startAt");
  });

  it("converts a datetime-local endAt to an ISO string", () => {
    const request = toAnnouncementCreateRequest({
      ...createEmptyAnnouncementForm(),
      title: "Judul",
      body: "Isi",
      endAt: "2026-12-31T23:59",
    });
    expect(request.endAt).not.toBeNull();
    expect(new Date(request.endAt as string).getUTCFullYear()).toBe(2026);
  });
});

describe("toAnnouncementPublishRequest", () => {
  it("returns undefined when startAt is empty (publish now)", () => {
    expect(toAnnouncementPublishRequest("")).toBeUndefined();
    expect(toAnnouncementPublishRequest("   ")).toBeUndefined();
  });

  it("converts datetime-local startAt to ISO", () => {
    const body = toAnnouncementPublishRequest("2026-08-12T08:00");
    expect(body).toBeDefined();
    expect(new Date(body!.startAt).getUTCFullYear()).toBe(2026);
  });
});

describe("announcementFormFromExisting", () => {
  it("round-trips an announcement with no end date", () => {
    const values = announcementFormFromExisting({
      title: "Judul",
      body: "Isi",
      priority: "NORMAL",
      endAt: null,
    });
    expect(values).toEqual({
      title: "Judul",
      body: "Isi",
      priority: "NORMAL",
      startAt: "",
      endAt: "",
    });
  });

  it("formats an ISO end date as a datetime-local value", () => {
    const values = announcementFormFromExisting({
      title: "Judul",
      body: "Isi",
      priority: "NORMAL",
      endAt: "2026-12-31T23:59:00.000Z",
    });
    expect(values.endAt).toMatch(/^2026-12-31T\d{2}:59$/);
  });

  it("formats an ISO start date as a datetime-local value", () => {
    const values = announcementFormFromExisting({
      title: "Judul",
      body: "Isi",
      priority: "NORMAL",
      startAt: "2026-08-15T08:30:00.000Z",
      endAt: null,
    });
    expect(values.startAt).toMatch(/^2026-08-15T\d{2}:30$/);
  });
});

describe("toAnnouncementUpdateRequest", () => {
  it("omits startAt unless includeStartAt is set", () => {
    const request = toAnnouncementUpdateRequest({
      ...createEmptyAnnouncementForm(),
      title: "Judul",
      body: "Isi",
      startAt: "2026-08-15T08:00",
    });
    expect(request).not.toHaveProperty("startAt");
  });

  it("includes startAt ISO when includeStartAt is true", () => {
    const request = toAnnouncementUpdateRequest(
      {
        ...createEmptyAnnouncementForm(),
        title: "Judul",
        body: "Isi",
        startAt: "2026-08-15T08:00",
      },
      { includeStartAt: true },
    );
    expect(request.startAt).toBeTruthy();
    expect(new Date(request.startAt as string).getUTCFullYear()).toBe(2026);
  });

  it("sends null startAt when includeStartAt and field is empty", () => {
    const request = toAnnouncementUpdateRequest(
      {
        ...createEmptyAnnouncementForm(),
        title: "Judul",
        body: "Isi",
        startAt: "",
      },
      { includeStartAt: true },
    );
    expect(request.startAt).toBeNull();
  });
});
