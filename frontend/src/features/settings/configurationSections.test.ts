import { describe, expect, it } from "vitest";
import {
  compactSettingValue,
  formatSettingDraft,
  humanizeSettingKey,
  localizedSettingDescription,
  localizedSettingTitle,
  matchesSearch,
  mimeChipLabel,
  parseStringArraySetting,
  settingDisplayTitle,
  settingI18nId,
  settingStatus,
  settingValuesEquivalent,
  usesMultilineSettingEditor,
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

describe("parseStringArraySetting", () => {
  it("parses a JSON string array and rejects invalid payloads", () => {
    expect(parseStringArraySetting('["application/pdf","image/png"]')).toEqual([
      "application/pdf",
      "image/png",
    ]);
    expect(parseStringArraySetting("not-json")).toBeNull();
    expect(parseStringArraySetting("[]")).toBeNull();
  });
});

describe("mimeChipLabel", () => {
  it("maps known MIME types to short labels", () => {
    expect(mimeChipLabel("application/pdf")).toBe("PDF");
    expect(
      mimeChipLabel(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      ),
    ).toBe("DOCX");
    expect(mimeChipLabel("application/zip")).toBe("ZIP");
  });
});

describe("setting JSON draft helpers", () => {
  const compact = '["application/pdf","image/jpeg"]';

  it("pretty-prints and compact-roundtrips an array setting", () => {
    expect(formatSettingDraft(compact)).toContain("\n");
    expect(compactSettingValue(formatSettingDraft(compact))).toBe(compact);
    expect(settingValuesEquivalent(formatSettingDraft(compact), compact)).toBe(
      true,
    );
  });

  it("uses a multiline editor for JSON arrays", () => {
    expect(usesMultilineSettingEditor(compact, "JSON")).toBe(true);
    expect(usesMultilineSettingEditor("2", "INTEGER")).toBe(false);
  });
});
