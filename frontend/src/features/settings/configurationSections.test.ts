import { describe, expect, it } from "vitest";
import {
  humanizeSettingKey,
  matchesSearch,
  settingDisplayTitle,
  settingStatus,
} from "./configurationSections";

describe("humanizeSettingKey", () => {
  it("uses the last segment and title-cases it", () => {
    expect(humanizeSettingKey("app.company_name")).toBe("Company Name");
  });
});

describe("settingDisplayTitle", () => {
  it("prefers short description", () => {
    expect(
      settingDisplayTitle({
        key: "app.timezone",
        description: "Default timezone",
      }),
    ).toBe("Default timezone");
  });

  it("falls back to humanized key", () => {
    expect(
      settingDisplayTitle({
        key: "storage.max_upload_mb",
        description: null,
      }),
    ).toBe("Max Upload Mb");
  });
});

describe("settingStatus", () => {
  it("maps empty, protected, and configured states", () => {
    expect(settingStatus({ value: "", visibility: "PUBLIC" }).key).toBe(
      "default",
    );
    expect(
      settingStatus({ value: "x", visibility: "PROTECTED" }).key,
    ).toBe("needsReview");
    expect(settingStatus({ value: "x", visibility: "PUBLIC" }).key).toBe(
      "configured",
    );
  });
});

describe("matchesSearch", () => {
  it("matches any haystack", () => {
    expect(matchesSearch("sla", "Policies", "SLA targets")).toBe(true);
    expect(matchesSearch("zzz", "Policies")).toBe(false);
    expect(matchesSearch("", "anything")).toBe(true);
  });
});
