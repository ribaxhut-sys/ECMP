import { describe, expect, it } from "vitest";
import { mayManageAnnouncements } from "./announcementManageGate";

const allowManage = (code: string) => code === "announcement:manage";
const denyAll = () => false;

describe("mayManageAnnouncements", () => {
  it("allows unscoped Admin / SUPER_ADMIN (no branch)", () => {
    expect(
      mayManageAnnouncements({
        roles: ["SUPER_ADMIN"],
        hasPermission: allowManage,
        orgUnitCode: null,
      }),
    ).toBe(true);
  });

  it("allows Supervisor/Manager only on a Pusat unit code", () => {
    expect(
      mayManageAnnouncements({
        roles: ["SUPERVISOR"],
        hasPermission: allowManage,
        orgUnitCode: "PUSAT",
      }),
    ).toBe(true);
    expect(
      mayManageAnnouncements({
        roles: ["MANAGER"],
        hasPermission: allowManage,
        orgUnitCode: "HO",
      }),
    ).toBe(true);
  });

  it("denies Supervisor/Manager Cabang even with announcement:manage", () => {
    expect(
      mayManageAnnouncements({
        roles: ["SUPERVISOR"],
        hasPermission: allowManage,
        orgUnitCode: "UPPPD-TANAH-ABANG",
      }),
    ).toBe(false);
    expect(
      mayManageAnnouncements({
        roles: ["MANAGER"],
        hasPermission: allowManage,
        orgUnitCode: "UPPPD-GAMBIR",
      }),
    ).toBe(false);
  });

  it("denies unit roles with no resolvable org (fail closed)", () => {
    expect(
      mayManageAnnouncements({
        roles: ["MANAGER"],
        hasPermission: allowManage,
        orgUnitCode: null,
      }),
    ).toBe(false);
  });

  it("denies callers without announcement:manage", () => {
    expect(
      mayManageAnnouncements({
        roles: ["SUPER_ADMIN"],
        hasPermission: denyAll,
        orgUnitCode: null,
      }),
    ).toBe(false);
  });

  it("denies Agent even on Pusat", () => {
    expect(
      mayManageAnnouncements({
        roles: ["AGENT"],
        hasPermission: (code) => code === "announcement:read",
        orgUnitCode: "PUSAT",
      }),
    ).toBe(false);
  });
});
