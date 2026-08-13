import { afterEach, describe, expect, it } from "vitest";
import { isInternalComplaintsUiEnabled } from "@/shared/config/internalComplaintsUi";
import {
  APP_NAV_GROUPS,
  APP_NAV_ITEMS,
  INTERNAL_COMPLAINTS_SUBGROUP_ID,
  INTERNAL_NAV_ITEM_IDS,
  TAXPAYER_COMPLAINTS_SUBGROUP_ID,
  isInternalNavItemId,
  isNavItemActive,
  isNavItemVisible,
  resolveActiveNavHref,
  resolveActiveSubgroupId,
} from "./nav";

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

  it("points Pengaduan nav to Aggregate list at /complaints", () => {
    const complaints = APP_NAV_ITEMS.find((item) => item.id === "complaints");
    expect(complaints?.href).toBe("/complaints");
    // Dual SoT remains: Aggregate detail stays under /complaints/cm/[id].
    expect(complaints?.id).not.toMatch(/cm[_-]?batch/i);
  });

  it("keeps leftover Foundation hrefs in the catalog (DEC-026 pages redirect)", () => {
    const byId = Object.fromEntries(APP_NAV_ITEMS.map((item) => [item.id, item]));
    expect(byId.queue.href).toBe("/queue");
    expect(byId.assignments.href).toBe("/assignments");
    expect(byId.resolutions.href).toBe("/resolutions");
  });
});

describe("Pengaduan Internal nav (prototype catalog, gated by env flag)", () => {
  const original = process.env.NEXT_PUBLIC_ECMP_INTERNAL_COMPLAINTS_UI;

  afterEach(() => {
    if (original === undefined) {
      delete process.env.NEXT_PUBLIC_ECMP_INTERNAL_COMPLAINTS_UI;
    } else {
      process.env.NEXT_PUBLIC_ECMP_INTERNAL_COMPLAINTS_UI = original;
    }
  });

  it("lives as a collapsible subgroup under the PENGADUAN group, alongside Wajib Pajak", () => {
    const complaintsGroup = APP_NAV_GROUPS.find((g) => g.id === "complaints")!;
    const subgroupIds = (complaintsGroup.subgroups ?? []).map((s) => s.id);
    expect(subgroupIds).toContain(INTERNAL_COMPLAINTS_SUBGROUP_ID);
    expect(subgroupIds).toContain(TAXPAYER_COMPLAINTS_SUBGROUP_ID);
    expect(subgroupIds.indexOf(INTERNAL_COMPLAINTS_SUBGROUP_ID)).toBeGreaterThan(
      subgroupIds.indexOf(TAXPAYER_COMPLAINTS_SUBGROUP_ID),
    );
  });

  it("catalog exposes the six internal destinations (routes stay in tree)", () => {
    const ids = APP_NAV_ITEMS.map((item) => item.id);
    for (const id of INTERNAL_NAV_ITEM_IDS) {
      expect(ids).toContain(id);
      expect(isInternalNavItemId(id)).toBe(true);
    }
  });

  it("hrefs live under /internal, distinct from /complaints (Wajib Pajak)", () => {
    const complaintsGroup = APP_NAV_GROUPS.find((g) => g.id === "complaints")!;
    const internalSubgroup = complaintsGroup.subgroups!.find(
      (s) => s.id === INTERNAL_COMPLAINTS_SUBGROUP_ID,
    )!;
    const itemsById = Object.fromEntries(APP_NAV_ITEMS.map((i) => [i.id, i]));
    for (const itemId of internalSubgroup.itemIds) {
      expect(itemsById[itemId].href.startsWith("/internal")).toBe(true);
    }
  });

  it("flag defaults off so Sidebar must hide the group without Board/FRD", () => {
    delete process.env.NEXT_PUBLIC_ECMP_INTERNAL_COMPLAINTS_UI;
    expect(isInternalComplaintsUiEnabled()).toBe(false);
  });
});

describe("APP_NAV_GROUPS", () => {
  it("sidebar groups reference known items exactly once (hidden catalog items omitted)", () => {
    const itemIds = new Set(APP_NAV_ITEMS.map((item) => item.id));
    const groupedIds = APP_NAV_GROUPS.flatMap((group) => group.itemIds);
    expect(new Set(groupedIds).size).toBe(groupedIds.length);
    for (const id of groupedIds) {
      expect(itemIds.has(id)).toBe(true);
    }
    // Antrian / Penugasan / Resolusi remain routable but off the main sidebar.
    expect(groupedIds).not.toContain("queue");
    expect(groupedIds).not.toContain("assignments");
    expect(groupedIds).not.toContain("resolutions");
    expect(groupedIds).not.toContain("internalAssignments");
  });

  it("matches the target sidebar hierarchy", () => {
    const byId = Object.fromEntries(APP_NAV_GROUPS.map((g) => [g.id, g]));
    expect(byId.complaints.itemIds).toEqual([
      "dashboard",
      "complaints",
      "cases",
      "followUp",
      "reports",
      "internalDashboard",
      "internalComplaints",
      "internalFollowUp",
      "internalVerification",
      "internalReports",
    ]);
    expect(byId.information.itemIds).toEqual([
      "announcements",
      "announcementsManage",
      "knowledge",
      "attachments",
    ]);
    expect(byId.administration.itemIds).toEqual(["users", "settings"]);
    expect(byId.overview).toBeUndefined();
  });
});

describe("complaints nav permission gate (Commit 6)", () => {
  const complaintsItem = APP_NAV_ITEMS.find((item) => item.id === "complaints")!;

  it("gates only the complaints, cases, followUp, announcements, and knowledge items", () => {
    const gatedItemIds = new Set([
      "complaints",
      "cases",
      "followUp",
      "announcements",
      "announcementsManage",
      "knowledge",
    ]);
    for (const item of APP_NAV_ITEMS) {
      if (gatedItemIds.has(item.id)) {
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

  it("gates the announcements archive on announcement:read", () => {
    const announcementsItem = APP_NAV_ITEMS.find((item) => item.id === "announcements")!;
    expect(announcementsItem.requiredPermissions).toEqual(["announcement:read"]);
    expect(announcementsItem.href).toBe("/announcements");
  });

  it("gates announcements manage on announcement:manage at a separate route", () => {
    const manageItem = APP_NAV_ITEMS.find((item) => item.id === "announcementsManage")!;
    expect(manageItem.requiredPermissions).toEqual(["announcement:manage"]);
    expect(manageItem.href).toBe("/announcements/manage");
  });

  it("gates followUp on complaints:read at /tindak-lanjut", () => {
    const followUpItem = APP_NAV_ITEMS.find((item) => item.id === "followUp")!;
    expect(followUpItem.requiredPermissions).toEqual(["complaints:read"]);
    expect(followUpItem.href).toBe("/tindak-lanjut");
  });

  it("gates Case inbox on complaints:read at /complaints/cm/cases (DEC-025)", () => {
    const casesItem = APP_NAV_ITEMS.find((item) => item.id === "cases")!;
    expect(casesItem.requiredPermissions).toEqual(["complaints:read"]);
    expect(casesItem.href).toBe("/complaints/cm/cases");
  });

  it("gates knowledge on knowledge:read", () => {
    const knowledgeItem = APP_NAV_ITEMS.find((item) => item.id === "knowledge")!;
    expect(knowledgeItem.requiredPermissions).toEqual(["knowledge:read"]);
    expect(knowledgeItem.href).toBe("/knowledge");
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

describe("isNavItemActive (longest prefix)", () => {
  const internalHrefs = [
    "/internal",
    "/internal/complaints",
    "/internal/assignments",
    "/internal/follow-up",
    "/internal/verification",
    "/internal/reports",
  ];

  it("activates only Dasbor on /internal", () => {
    expect(resolveActiveNavHref("/internal", internalHrefs)).toBe("/internal");
    expect(isNavItemActive("/internal", "/internal", internalHrefs)).toBe(true);
    expect(
      isNavItemActive("/internal", "/internal/follow-up", internalHrefs),
    ).toBe(false);
  });

  it("does not keep Dasbor active on /internal/follow-up", () => {
    expect(resolveActiveNavHref("/internal/follow-up", internalHrefs)).toBe(
      "/internal/follow-up",
    );
    expect(
      isNavItemActive("/internal/follow-up", "/internal", internalHrefs),
    ).toBe(false);
    expect(
      isNavItemActive("/internal/follow-up", "/internal/follow-up", internalHrefs),
    ).toBe(true);
  });

  it("keeps child active on nested detail paths", () => {
    expect(
      resolveActiveNavHref("/internal/complaints/abc", internalHrefs),
    ).toBe("/internal/complaints");
  });

  it("activates Case inbox without stealing Pengaduan on /complaints/cm/[id]", () => {
    const hrefs = ["/complaints", "/complaints/cm/cases"];
    expect(resolveActiveNavHref("/complaints/cm/cases", hrefs)).toBe(
      "/complaints/cm/cases",
    );
    expect(resolveActiveNavHref("/complaints/cm/abc", hrefs)).toBe("/complaints");
    expect(isNavItemActive("/complaints/cm/cases", "/complaints", hrefs)).toBe(
      false,
    );
  });
});

describe("complaints group subgroups (collapsible Wajib Pajak / Internal)", () => {
  const complaintsGroup = APP_NAV_GROUPS.find((g) => g.id === "complaints")!;

  it("splits Wajib Pajak and Internal into distinct subgroups covering the group's items exactly once", () => {
    const subgroupItemIds = complaintsGroup
      .subgroups!.flatMap((s) => s.itemIds)
      .sort();
    expect(subgroupItemIds).toEqual([...complaintsGroup.itemIds].sort());
    expect(new Set(subgroupItemIds).size).toBe(subgroupItemIds.length);
  });

  it("Wajib Pajak subgroup carries Dasbor, Pengaduan, Case, Tindak lanjut, Laporan", () => {
    const taxpayer = complaintsGroup.subgroups!.find(
      (s) => s.id === TAXPAYER_COMPLAINTS_SUBGROUP_ID,
    )!;
    expect(taxpayer.itemIds).toEqual([
      "dashboard",
      "complaints",
      "cases",
      "followUp",
      "reports",
    ]);
    expect(taxpayer.labelKey).toBe("subgroupTaxpayerComplaints");
  });

  it("Internal subgroup omits Penugasan from the sidebar", () => {
    const internal = complaintsGroup.subgroups!.find(
      (s) => s.id === INTERNAL_COMPLAINTS_SUBGROUP_ID,
    )!;
    expect(internal.itemIds).toEqual([
      "internalDashboard",
      "internalComplaints",
      "internalFollowUp",
      "internalVerification",
      "internalReports",
    ]);
    expect(internal.itemIds).not.toContain("internalAssignments");
    expect(internal.labelKey).toBe("subgroupInternalComplaints");
  });

  it("keeps distinct report routes per domain (no shared /reports)", () => {
    const byId = Object.fromEntries(APP_NAV_ITEMS.map((i) => [i.id, i]));
    expect(byId.reports.href).toBe("/reports");
    expect(byId.internalReports.href).toBe("/internal/reports");
    const information = APP_NAV_GROUPS.find((g) => g.id === "information")!;
    expect(information.itemIds).toEqual([
      "announcements",
      "announcementsManage",
      "knowledge",
      "attachments",
    ]);
    expect(information.itemIds).not.toContain("reports");
    expect(information.itemIds).not.toContain("internalReports");
  });
});

describe("resolveActiveSubgroupId", () => {
  const subgroups = [
    {
      id: TAXPAYER_COMPLAINTS_SUBGROUP_ID,
      hrefs: ["/dashboard", "/complaints", "/reports"],
    },
    {
      id: INTERNAL_COMPLAINTS_SUBGROUP_ID,
      hrefs: ["/internal", "/internal/verification"],
    },
  ];
  const allHrefs = subgroups.flatMap((s) => s.hrefs);

  it("resolves the subgroup owning the active route (Pengaduan → Wajib Pajak)", () => {
    expect(resolveActiveSubgroupId("/complaints", subgroups, allHrefs)).toBe(
      TAXPAYER_COMPLAINTS_SUBGROUP_ID,
    );
  });

  it("resolves the subgroup owning the active route (Verifikasi → Internal)", () => {
    expect(
      resolveActiveSubgroupId("/internal/verification", subgroups, allHrefs),
    ).toBe(INTERNAL_COMPLAINTS_SUBGROUP_ID);
  });

  it("returns null when the route matches no subgroup href", () => {
    expect(resolveActiveSubgroupId("/settings", subgroups, allHrefs)).toBeNull();
  });
});
