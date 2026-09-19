import { afterEach, describe, expect, it } from "vitest";
import { isInternalComplaintsUiEnabled } from "./internalComplaintsUi";

describe("isInternalComplaintsUiEnabled", () => {
  const original = process.env.NEXT_PUBLIC_ECMP_INTERNAL_COMPLAINTS_UI;

  afterEach(() => {
    if (original === undefined) {
      delete process.env.NEXT_PUBLIC_ECMP_INTERNAL_COMPLAINTS_UI;
    } else {
      process.env.NEXT_PUBLIC_ECMP_INTERNAL_COMPLAINTS_UI = original;
    }
  });

  it("is off by default (unauthorized prototype must not surface in lab/prod nav)", () => {
    delete process.env.NEXT_PUBLIC_ECMP_INTERNAL_COMPLAINTS_UI;
    expect(isInternalComplaintsUiEnabled()).toBe(false);
  });

  it("is on only for explicit true", () => {
    process.env.NEXT_PUBLIC_ECMP_INTERNAL_COMPLAINTS_UI = "true";
    expect(isInternalComplaintsUiEnabled()).toBe(true);
  });

  it("rejects non-true values", () => {
    process.env.NEXT_PUBLIC_ECMP_INTERNAL_COMPLAINTS_UI = "1";
    expect(isInternalComplaintsUiEnabled()).toBe(false);
    process.env.NEXT_PUBLIC_ECMP_INTERNAL_COMPLAINTS_UI = "yes";
    expect(isInternalComplaintsUiEnabled()).toBe(false);
  });
});
