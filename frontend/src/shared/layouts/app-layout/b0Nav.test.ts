import { describe, expect, it } from "vitest";
import { B0_NAV_GROUPS, B0_NAV_ITEMS } from "./b0Nav";
import { SHELL_PERMISSIONS } from "@/auth/mockAuth";

describe("B0_NAV_ITEMS", () => {
  it("only exposes shell destinations (no complaint feature routes)", () => {
    const hrefs = B0_NAV_ITEMS.map((item) => item.href);
    expect(hrefs).toEqual(["/workspace", "/queue", "/settings"]);
    for (const item of B0_NAV_ITEMS) {
      expect(item.href).not.toMatch(/complaints|assignments|resolutions|dashboard|reports/i);
    }
  });

  it("gates items with shell permission placeholders", () => {
    expect(B0_NAV_ITEMS.find((i) => i.id === "workspace")?.requiredPermissions).toEqual([
      SHELL_PERMISSIONS.workspaceIntake,
    ]);
    expect(B0_NAV_ITEMS.find((i) => i.id === "queue")?.requiredPermissions).toEqual([
      SHELL_PERMISSIONS.queueAssigned,
      SHELL_PERMISSIONS.queueSupervisor,
    ]);
  });

  it("groups cover every B0 item once", () => {
    const ids = B0_NAV_ITEMS.map((i) => i.id).sort();
    const grouped = B0_NAV_GROUPS.flatMap((g) => [...g.itemIds]).sort();
    expect(grouped).toEqual(ids);
  });
});
