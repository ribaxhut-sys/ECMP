import { describe, expect, it } from "vitest";
import { prefersComplaintNumberIdentity, isPusatWorkAudience } from "./cmBatch1ComplaintListIdentity";

describe("prefersComplaintNumberIdentity", () => {
  it("is true for branch unit codes", () => {
    expect(prefersComplaintNumberIdentity("UPPPD-TANAH-ABANG")).toBe(true);
    expect(prefersComplaintNumberIdentity("UPPPD-GAMBIR")).toBe(true);
  });

  it("is false for Pusat root and sub-units", () => {
    expect(prefersComplaintNumberIdentity("PUSAT")).toBe(false);
    expect(prefersComplaintNumberIdentity("PUSAT-CRO")).toBe(false);
    expect(prefersComplaintNumberIdentity("HO")).toBe(false);
    expect(prefersComplaintNumberIdentity("HEAD_OFFICE")).toBe(false);
  });

  it("is false while loading or for users without a branch", () => {
    expect(prefersComplaintNumberIdentity(undefined)).toBe(false);
    expect(prefersComplaintNumberIdentity(null)).toBe(false);
    expect(prefersComplaintNumberIdentity("")).toBe(false);
    expect(prefersComplaintNumberIdentity("   ")).toBe(false);
  });
});

describe("isPusatWorkAudience", () => {
  it("is null while the org unit is loading", () => {
    expect(isPusatWorkAudience(undefined)).toBeNull();
  });

  it("is true for Pusat units and users without a branch", () => {
    expect(isPusatWorkAudience("PUSAT")).toBe(true);
    expect(isPusatWorkAudience("PUSAT-CRO")).toBe(true);
    expect(isPusatWorkAudience(null)).toBe(true);
  });

  it("is false for Cabang units", () => {
    expect(isPusatWorkAudience("UPPPD-TANAH-ABANG")).toBe(false);
  });
});
