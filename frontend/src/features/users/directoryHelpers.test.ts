import { describe, expect, it } from "vitest";
import type { RoleRef, UserRef } from "@/lib/api";
import {
  directoryLocationTone,
  directoryRoleFamily,
  directoryRoleLabel,
  matchesDirectoryFilter,
  matchesDirectorySearch,
  roleDisplayName,
  userInitials,
  userLocationKind,
} from "./directoryHelpers";

function user(partial: Partial<UserRef>): UserRef {
  return {
    id: "1",
    username: "jdoe",
    email: "jdoe@example.com",
    fullName: "Jane Doe",
    roleId: "r1",
    roleCode: null,
    roleName: null,
    branchId: null,
    isActive: true,
    lastLoginAt: null,
    createdAt: "2026-01-01T00:00:00Z",
    updatedAt: "2026-01-02T00:00:00Z",
    ...partial,
  };
}

describe("userInitials", () => {
  it("uses two name parts", () => {
    expect(userInitials(user({ fullName: "Ada Lovelace" }))).toBe("AL");
  });

  it("falls back to username", () => {
    expect(userInitials(user({ fullName: "", username: "ops" }))).toBe("OP");
  });
});

describe("directoryRoleFamily", () => {
  it("classifies known families", () => {
    expect(directoryRoleFamily(user({ roleCode: "ADMIN" }))).toBe(
      "administrator",
    );
    expect(directoryRoleFamily(user({ roleName: "Supervisor Desk" }))).toBe(
      "supervisor",
    );
    expect(directoryRoleFamily(user({ roleCode: "AGENT" }))).toBe("agent");
    expect(directoryRoleFamily(user({ roleCode: "VIEWER" }))).toBe("viewer");
  });
});

describe("directoryRoleLabel", () => {
  it("prefers family label then raw role", () => {
    expect(
      directoryRoleLabel(
        user({ roleCode: "ADMIN" }),
        {
          administrator: "Administrator",
          supervisor: "Supervisor",
          agent: "Agent",
          viewer: "Viewer",
          other: "—",
        },
        "—",
      ),
    ).toBe("Administrator");

    expect(
      directoryRoleLabel(
        user({ roleName: "Custom Lead" }),
        {
          administrator: "Administrator",
          supervisor: "Supervisor",
          agent: "Agent",
          viewer: "Viewer",
          other: "—",
        },
        "—",
      ),
    ).toBe("Custom Lead");
  });
});

describe("matchesDirectoryFilter", () => {
  it("filters by status and role family", () => {
    const admin = user({ roleCode: "ADMIN", isActive: true });
    const inactive = user({ id: "2", isActive: false, roleCode: "AGENT" });
    expect(matchesDirectoryFilter(admin, "administrator")).toBe(true);
    expect(matchesDirectoryFilter(inactive, "active")).toBe(false);
    expect(matchesDirectoryFilter(inactive, "inactive")).toBe(true);
    expect(matchesDirectoryFilter(inactive, "agent")).toBe(true);
  });
});

describe("matchesDirectorySearch", () => {
  it("matches name username email and role", () => {
    const row = user({ roleName: "Supervisor" });
    expect(matchesDirectorySearch(row, "jane")).toBe(true);
    expect(matchesDirectorySearch(row, "superv")).toBe(true);
    expect(matchesDirectorySearch(row, "zzz")).toBe(false);
  });
});

describe("userLocationKind", () => {
  it("is headOffice when branchId is null (Commit 2 invariant)", () => {
    expect(userLocationKind(user({ branchId: null }))).toBe("headOffice");
  });

  it("is branch when branchId is present", () => {
    expect(userLocationKind(user({ branchId: "b1" }))).toBe("branch");
  });
});

describe("directoryLocationTone", () => {
  it("maps branch and headOffice to distinct tones", () => {
    expect(directoryLocationTone("branch")).toBe("info");
    expect(directoryLocationTone("headOffice")).toBe("primary");
  });
});

describe("roleDisplayName", () => {
  function role(partial: Partial<RoleRef>): Pick<RoleRef, "code" | "name"> {
    return {
      code: "AGENT",
      name: "Agent",
      ...partial,
    };
  }

  it("overrides BRANCH_SUPERVISOR with the given label", () => {
    expect(
      roleDisplayName(
        role({ code: "BRANCH_SUPERVISOR", name: "Branch Supervisor" }),
        "Manager Cabang",
      ),
    ).toBe("Manager Cabang");
  });

  it("leaves every other role code as the raw role name", () => {
    expect(
      roleDisplayName(role({ code: "SUPERVISOR", name: "Supervisor" }), "Manager Cabang"),
    ).toBe("Supervisor");
    expect(
      roleDisplayName(role({ code: "ADMIN", name: "Administrator" }), "Manager Cabang"),
    ).toBe("Administrator");
  });
});
