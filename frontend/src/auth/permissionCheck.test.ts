import { describe, expect, it } from "vitest";
import { principalHasPermission } from "./permissionCheck";

describe("principalHasPermission", () => {
  it("grants an explicitly held code", () => {
    expect(principalHasPermission(["complaints:read"], "complaints:read")).toBe(
      true,
    );
  });

  it("lets wildcard cover unrelated codes", () => {
    expect(principalHasPermission(["*"], "complaints:read")).toBe(true);
    expect(principalHasPermission(["*"], "users:create")).toBe(true);
  });

  it("does not let wildcard grant complaints:create", () => {
    expect(principalHasPermission(["*"], "complaints:create")).toBe(false);
  });

  it("still grants complaints:create when the code is explicit", () => {
    expect(
      principalHasPermission(["*", "complaints:create"], "complaints:create"),
    ).toBe(true);
  });
});
