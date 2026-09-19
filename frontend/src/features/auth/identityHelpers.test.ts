import { describe, expect, it } from "vitest";
import {
  formatIdentityBranch,
  identityInitials,
  isOwnModuleActivity,
  moduleRoleDisplayLabels,
  primaryRoleLabel,
  resolveIdentityUnitLabel,
} from "./identityHelpers";

describe("identityInitials", () => {
  it("builds three-letter initials from full name", () => {
    expect(identityInitials("Ada Lovelace")).toBe("ALO");
    expect(identityInitials("Budi Santoso")).toBe("BSA");
    expect(identityInitials("Budi Santoso Pratama")).toBe("BSP");
  });

  it("keeps three letters for single-word names", () => {
    expect(identityInitials("Administrator")).toBe("ADM");
  });

  it("falls back for empty values", () => {
    expect(identityInitials("")).toBe("?");
    expect(identityInitials("   ", "U")).toBe("U");
  });
});

describe("formatIdentityBranch", () => {
  it("shortens long identifiers", () => {
    expect(
      formatIdentityBranch("1234567890abcdef", "Unassigned"),
    ).toBe("12345678…cdef");
  });
});

describe("resolveIdentityUnitLabel", () => {
  const units = [
    { id: "uuid-1", code: "JKT01", name: "Cabang Jakarta Selatan" },
  ];

  it("prefers name and code over the raw id", () => {
    expect(resolveIdentityUnitLabel("uuid-1", units, "Unassigned")).toBe(
      "Cabang Jakarta Selatan (JKT01)",
    );
    expect(resolveIdentityUnitLabel("JKT01", units, "Unassigned")).toBe(
      "Cabang Jakarta Selatan (JKT01)",
    );
  });

  it("does not echo a truncated UUID when the unit is unknown", () => {
    expect(
      resolveIdentityUnitLabel("1234567890abcdef", units, "Unassigned"),
    ).toBe("Unassigned");
  });
});

describe("isOwnModuleActivity", () => {
  const user = {
    id: "u-1",
    username: "ani",
    email: "ani@example.com",
    fullName: "Ani Petugas",
  };

  it("matches username, display name, or email", () => {
    expect(isOwnModuleActivity("ani", user)).toBe(true);
    expect(isOwnModuleActivity("Ani Petugas", user)).toBe(true);
    expect(isOwnModuleActivity("ani@example.com", user)).toBe(true);
  });

  it("rejects system and other actors", () => {
    expect(isOwnModuleActivity("SYSTEM", user)).toBe(false);
    expect(isOwnModuleActivity("budi", user)).toBe(false);
  });
});

describe("primaryRoleLabel", () => {
  it("maps AGENT and VIEWER when labels are provided", () => {
    const labels = moduleRoleDisplayLabels((key) =>
      key === "roleAgent" ? "CRO" : key,
    );
    expect(primaryRoleLabel({ roles: ["AGENT"] }, "Pengguna", labels)).toBe(
      "CRO",
    );
    expect(primaryRoleLabel({ roles: ["VIEWER"] }, "Pengguna", labels)).toBe(
      "roleViewer",
    );
  });

  it("returns first role or fallback", () => {
    expect(
      primaryRoleLabel({ roles: ["Supervisor"] }, "Unassigned"),
    ).toBe("Supervisor");
    expect(primaryRoleLabel({ roles: [] }, "Unassigned")).toBe("Unassigned");
  });
});
