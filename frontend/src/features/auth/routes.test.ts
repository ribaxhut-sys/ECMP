import { describe, expect, it } from "vitest";
import { PASSWORD_CHANGE_ROUTE } from "./routes";

describe("PASSWORD_CHANGE_ROUTE", () => {
  it("matches Mode A credential inventory app path (K-3 / FE-ARCH §5.3)", () => {
    expect(PASSWORD_CHANGE_ROUTE).toBe("/profile/security/change-password");
    expect(PASSWORD_CHANGE_ROUTE.startsWith("/")).toBe(true);
    expect(PASSWORD_CHANGE_ROUTE).not.toMatch(/^https?:/i);
  });
});
