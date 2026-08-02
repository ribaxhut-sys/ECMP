import { describe, expect, it } from "vitest";
import { APP_NAV_GROUPS, APP_NAV_ITEMS } from "./nav";

describe("APP_NAV_ITEMS", () => {
  it("includes reports and users routes", () => {
    const ids = APP_NAV_ITEMS.map((item) => item.id);
    expect(ids).toContain("reports");
    expect(ids).toContain("users");
    expect(ids).toContain("dashboard");
  });

  it("keeps hrefs under app paths (no external hosts)", () => {
    for (const item of APP_NAV_ITEMS) {
      expect(item.href.startsWith("/")).toBe(true);
      expect(item.href).not.toMatch(/^https?:/i);
    }
  });

  it("has unique ids", () => {
    const ids = APP_NAV_ITEMS.map((item) => item.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it("does not add Aggregate /cm UI routes to primary nav (DEC-020 dual SoT)", () => {
    for (const item of APP_NAV_ITEMS) {
      expect(item.href).not.toMatch(/\/cm(\/|$)/);
      expect(item.id).not.toMatch(/cm[_-]?batch/i);
    }
    // Foundation complaints list remains the Mode A create/lifecycle entry.
    expect(APP_NAV_ITEMS.some((item) => item.href === "/complaints")).toBe(
      true,
    );
  });
});

describe("APP_NAV_GROUPS", () => {
  it("covers every primary nav item exactly once (presentation-only grouping)", () => {
    const itemIds = APP_NAV_ITEMS.map((item) => item.id).sort();
    const groupedIds = APP_NAV_GROUPS.flatMap((group) => group.itemIds).sort();
    expect(groupedIds).toEqual(itemIds);
    expect(new Set(groupedIds).size).toBe(groupedIds.length);
  });
});
