import { describe, expect, it } from "vitest";
import {
  formatIdentityBranch,
  identityInitials,
  moduleRoleDisplayLabels,
  primaryRoleLabel,
} from "./identityHelpers";

describe("identityInitials", () => {
  it("builds initials from full name", () => {
    expect(identityInitials("Ada Lovelace")).toBe("AL");
  });

  it("falls back for empty values", () => {
    expect(identityInitials("")).toBe("?");
  });
});

describe("formatIdentityBranch", () => {
  it("shortens long identifiers", () => {
    expect(
      formatIdentityBranch("1234567890abcdef", "Unassigned"),
    ).toBe("12345678…cdef");
  });
});

describe("primaryRoleLabel", () => {
  it("maps AGENT to Petugas when labels are provided", () => {
    const labels = moduleRoleDisplayLabels((key) =>
      key === "roleAgent" ? "Petugas" : key,
    );
    expect(primaryRoleLabel({ roles: ["AGENT"] }, "Pengguna", labels)).toBe(
      "Petugas",
    );
  });

  it("returns first role or fallback", () => {
    expect(
      primaryRoleLabel({ roles: ["Supervisor"] }, "Unassigned"),
    ).toBe("Supervisor");
    expect(primaryRoleLabel({ roles: [] }, "Unassigned")).toBe("Unassigned");
  });
});
