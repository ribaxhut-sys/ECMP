import { describe, expect, it } from "vitest";
import {
  humanizeSettingKey,
  localizedSettingDescription,
  localizedSettingTitle,
  matchesSearch,
  settingDisplayTitle,
  settingI18nId,
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

describe("settingI18nId", () => {
  it("flattens dot keys for message lookup", () => {
    expect(settingI18nId("hq.schedule.capacity_per_slot")).toBe(
      "hq_schedule_capacity_per_slot",
    );
  });
});

describe("localizedSettingTitle", () => {
  const catalog: Record<string, string> = {
    "settingKey.hq_schedule_capacity_per_slot.label": "Kapasitas per slot",
  };
  const t = Object.assign((key: string) => catalog[key] ?? key, {
    has: (key: string) => key in catalog,
  });

  it("uses the catalog label when present", () => {
    expect(
      localizedSettingTitle(
        {
          key: "hq.schedule.capacity_per_slot",
          description: "Max taxpayer arrivals accommodated per HQ schedule slot",
        },
        t,
      ),
    ).toBe("Kapasitas per slot");
  });

  it("falls back to the English description when the catalog misses the key", () => {
    expect(
      localizedSettingTitle(
        { key: "unknown.setting", description: "Fallback copy" },
        t,
      ),
    ).toBe("Fallback copy");
  });
});

describe("localizedSettingDescription", () => {
  const catalog: Record<string, string> = {
    "settingKey.hq_schedule_capacity_per_slot.description":
      "Jumlah maksimum kedatangan wajib pajak per slot jadwal HQ.",
  };
  const t = Object.assign((key: string) => catalog[key] ?? key, {
    has: (key: string) => key in catalog,
  });

  it("uses the catalog description when present", () => {
    expect(
      localizedSettingDescription(
        {
          key: "hq.schedule.capacity_per_slot",
          description: "Max taxpayer arrivals accommodated per HQ schedule slot",
        },
        t,
        "No description",
      ),
    ).toBe("Jumlah maksimum kedatangan wajib pajak per slot jadwal HQ.");
  });
});
