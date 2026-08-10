import { describe, expect, it } from "vitest";
import type { Announcement } from "@/lib/api/types";
import { selectLandingAnnouncements, sortAnnouncements } from "./announcements";

function make(id: string, publishedAt: string | null): Announcement {
  return {
    id,
    referenceNumber: `PGM-2608-${id.slice(0, 4).padStart(4, "0")}`,
    title: id,
    body: `Body for ${id}`,
    priority: "NORMAL",
    status: "PUBLISHED",
    effectiveStatus: "PUBLISHED",
    startAt: publishedAt,
    endAt: null,
    publishedAt,
    publishedBy: null,
    createdBy: null,
    createdAt: publishedAt ?? "2026-01-01T00:00:00Z",
    updatedBy: null,
    updatedAt: publishedAt ?? "2026-01-01T00:00:00Z",
    attachments: [],
    attachmentCount: 0,
  };
}

describe("sortAnnouncements", () => {
  it("puts the newest published announcement first", () => {
    const sorted = sortAnnouncements([
      make("old", "2026-07-01T00:00:00+07:00"),
      make("new", "2026-08-01T00:00:00+07:00"),
      make("mid", "2026-07-15T00:00:00+07:00"),
    ]);
    expect(sorted.map((a) => a.id)).toEqual(["new", "mid", "old"]);
  });

  it("does not mutate the input", () => {
    const input = [
      make("old", "2026-07-01T00:00:00+07:00"),
      make("new", "2026-08-01T00:00:00+07:00"),
    ];
    sortAnnouncements(input);
    expect(input.map((a) => a.id)).toEqual(["old", "new"]);
  });

  it("treats a null publishedAt as oldest", () => {
    const sorted = sortAnnouncements([
      make("no-date", null),
      make("dated", "2026-08-01T00:00:00+07:00"),
    ]);
    expect(sorted.map((a) => a.id)).toEqual(["dated", "no-date"]);
  });
});

describe("selectLandingAnnouncements", () => {
  it("returns the top item as featured and the rest after it", () => {
    const { featured, rest } = selectLandingAnnouncements([
      make("a", "2026-07-01T00:00:00+07:00"),
      make("b", "2026-08-01T00:00:00+07:00"),
      make("c", "2026-07-15T00:00:00+07:00"),
    ]);
    expect(featured?.id).toBe("b");
    expect(rest.map((a) => a.id)).toEqual(["c", "a"]);
  });

  it("caps the landing page so it never becomes a news archive", () => {
    const many = Array.from({ length: 10 }, (_, i) =>
      make(`a${i}`, `2026-08-0${(i % 9) + 1}T00:00:00+07:00`),
    );
    const { featured, rest } = selectLandingAnnouncements(many, 3);
    expect(featured).not.toBeNull();
    expect(rest).toHaveLength(2);
  });

  it("reports an empty state when there is nothing to show", () => {
    expect(selectLandingAnnouncements([])).toEqual({
      featured: null,
      rest: [],
    });
  });
});
