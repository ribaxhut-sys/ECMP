import { describe, expect, it } from "vitest";
import { APP_NAV_ITEMS, isNavItemVisible } from "./nav";

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

describe("complaints nav permission gate (Commit 6)", () => {
  const complaintsItem = APP_NAV_ITEMS.find((item) => item.id === "complaints")!;

  it("gates only the complaints item", () => {
    for (const item of APP_NAV_ITEMS) {
      if (item.id === "complaints") {
        expect(item.requiredPermissions).toBeDefined();
      } else {
        expect(item.requiredPermissions).toBeUndefined();
      }
    }
  });

  it("lists the canonical complaints permission catalog (backend/app/core/rbac.py)", () => {
    expect(complaintsItem.requiredPermissions).toEqual([
      "complaints:read",
      "complaints:create",
      "complaints:update",
      "complaints:assign",
      "complaints:escalate",
      "complaints:close",
    ]);
  });
});

describe("isNavItemVisible", () => {
  it("is visible with no requiredPermissions gate", () => {
    expect(isNavItemVisible({}, () => false)).toBe(true);
  });

  it("is visible when the caller holds at least one required permission", () => {
    const item = { requiredPermissions: ["complaints:read", "complaints:create"] };
    expect(isNavItemVisible(item, (p) => p === "complaints:create")).toBe(true);
  });

  it("is hidden when the caller holds none of the required permissions", () => {
    const item = { requiredPermissions: ["complaints:read", "complaints:create"] };
    expect(isNavItemVisible(item, () => false)).toBe(false);
  });

  it("respects wildcard permission without reimplementing AuthProvider's matching", () => {
    const item = { requiredPermissions: ["complaints:read", "complaints:create"] };
    // Mirrors AuthProvider.hasPermission verbatim (permissions.includes("*")
    // || permissions.includes(permission)) — isNavItemVisible never inspects
    // "*" itself, it only calls hasPermission with its own permission
    // strings and trusts the caller's wildcard resolution.
    const permissions = ["*"];
    const hasPermission = (permission: string) =>
      permissions.includes("*") || permissions.includes(permission);
    expect(isNavItemVisible(item, hasPermission)).toBe(true);
  });
});
