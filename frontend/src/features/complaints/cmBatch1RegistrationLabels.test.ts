import { describe, expect, it } from "vitest";
import {
  cmBatch1ChannelLabelKey,
  formatCmBatch1CustomerLabel,
  resolveCmBatch1RegistrationUnitLabel,
  shouldShowCmBatch1Category,
} from "./cmBatch1RegistrationLabels";

describe("cmBatch1ChannelLabelKey", () => {
  it("maps known channel codes", () => {
    expect(cmBatch1ChannelLabelKey("BRANCH")).toBe("channelBranch");
    expect(cmBatch1ChannelLabelKey("call")).toBe("channelCall");
    expect(cmBatch1ChannelLabelKey("EMAIL")).toBe("channelEmail");
  });

  it("returns null for unknown or empty", () => {
    expect(cmBatch1ChannelLabelKey("")).toBeNull();
    expect(cmBatch1ChannelLabelKey("SMS")).toBeNull();
  });
});

describe("shouldShowCmBatch1Category", () => {
  it("hides empty and GENERAL defaults", () => {
    expect(shouldShowCmBatch1Category(null)).toBe(false);
    expect(shouldShowCmBatch1Category("")).toBe(false);
    expect(shouldShowCmBatch1Category("GENERAL")).toBe(false);
    expect(shouldShowCmBatch1Category("general")).toBe(false);
  });

  it("shows non-default categories", () => {
    expect(shouldShowCmBatch1Category("SERVICE")).toBe(true);
    expect(shouldShowCmBatch1Category("BILLING")).toBe(true);
  });
});

describe("formatCmBatch1CustomerLabel", () => {
  it("formats name with business number", () => {
    expect(formatCmBatch1CustomerLabel("Budi Santoso", "CUST-1042")).toBe(
      "Budi Santoso / CUST-1042",
    );
  });

  it("falls back to name or number alone", () => {
    expect(formatCmBatch1CustomerLabel("Budi", null)).toBe("Budi");
    expect(formatCmBatch1CustomerLabel(null, "CUST-1")).toBe("CUST-1");
    expect(formatCmBatch1CustomerLabel(null, null, "uuid-1")).toBe("uuid-1");
    expect(formatCmBatch1CustomerLabel(null, null, null)).toBeNull();
  });
});

describe("resolveCmBatch1RegistrationUnitLabel", () => {
  const units = [
    { id: "b-1", code: "PUSAT", name: "Kantor Pusat" },
    { id: "b-2", code: "JKT01", name: "Cabang Menteng" },
  ];

  it("resolves by id or code to the unit name", () => {
    expect(resolveCmBatch1RegistrationUnitLabel("b-1", units)).toBe("Kantor Pusat");
    expect(resolveCmBatch1RegistrationUnitLabel("JKT01", units)).toBe(
      "Cabang Menteng",
    );
  });

  it("returns the raw id when unknown", () => {
    expect(resolveCmBatch1RegistrationUnitLabel("unknown", units)).toBe("unknown");
    expect(resolveCmBatch1RegistrationUnitLabel(null, units)).toBeNull();
  });
});
