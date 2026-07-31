import { describe, expect, it } from "vitest";
import { PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH } from "./passwordPolicy";

describe("passwordPolicy", () => {
  it("matches backend-aligned length bounds", () => {
    expect(PASSWORD_MIN_LENGTH).toBe(8);
    expect(PASSWORD_MAX_LENGTH).toBe(72);
    expect(PASSWORD_MAX_LENGTH).toBeGreaterThan(PASSWORD_MIN_LENGTH);
  });
});
