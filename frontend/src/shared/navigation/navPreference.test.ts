import { describe, expect, it } from "vitest";
import {
  DEFAULT_NAV_PREFERENCE_MODE,
  DEFAULT_NAV_PREFERENCE_STATE,
  isNavPreferenceMode,
  navPreferenceStorageKey,
  normalizeNavPreferenceMode,
  parseNavPreference,
  resolveExpandedSubgroups,
  serializeNavPreference,
} from "./navPreference";

describe("isNavPreferenceMode / normalizeNavPreferenceMode", () => {
  it("accepts the three documented modes", () => {
    expect(isNavPreferenceMode("auto")).toBe(true);
    expect(isNavPreferenceMode("remember")).toBe(true);
    expect(isNavPreferenceMode("expandAll")).toBe(true);
  });

  it("falls back to auto for unknown/invalid values (Scenario 8)", () => {
    expect(normalizeNavPreferenceMode("bogus")).toBe(DEFAULT_NAV_PREFERENCE_MODE);
    expect(normalizeNavPreferenceMode(null)).toBe(DEFAULT_NAV_PREFERENCE_MODE);
    expect(normalizeNavPreferenceMode(undefined)).toBe(DEFAULT_NAV_PREFERENCE_MODE);
    expect(normalizeNavPreferenceMode(42)).toBe(DEFAULT_NAV_PREFERENCE_MODE);
  });
});

describe("navPreferenceStorageKey", () => {
  it("scopes the key per user id", () => {
    expect(navPreferenceStorageKey("user-1")).not.toBe(
      navPreferenceStorageKey("user-2"),
    );
  });

  it("has a stable anonymous fallback", () => {
    expect(navPreferenceStorageKey(null)).toBe(navPreferenceStorageKey(undefined));
  });
});

describe("parseNavPreference", () => {
  it("returns the default state for null/undefined/empty input", () => {
    expect(parseNavPreference(null)).toEqual(DEFAULT_NAV_PREFERENCE_STATE);
    expect(parseNavPreference(undefined)).toEqual(DEFAULT_NAV_PREFERENCE_STATE);
    expect(parseNavPreference("")).toEqual(DEFAULT_NAV_PREFERENCE_STATE);
  });

  it("never throws on malformed JSON — falls back to default (Scenario 8)", () => {
    expect(() => parseNavPreference("{not json")).not.toThrow();
    expect(parseNavPreference("{not json")).toEqual(DEFAULT_NAV_PREFERENCE_STATE);
  });

  it("falls back on a non-object payload", () => {
    expect(parseNavPreference("42")).toEqual(DEFAULT_NAV_PREFERENCE_STATE);
    expect(parseNavPreference('"remember"')).toEqual(DEFAULT_NAV_PREFERENCE_STATE);
  });

  it("normalizes an invalid stored mode to auto", () => {
    const parsed = parseNavPreference(JSON.stringify({ mode: "garbage" }));
    expect(parsed.mode).toBe("auto");
  });

  it("round-trips a valid remember-mode payload", () => {
    const state = {
      mode: "remember" as const,
      expanded: { taxpayerComplaints: true, internalComplaints: false },
    };
    const parsed = parseNavPreference(serializeNavPreference(state));
    expect(parsed).toEqual(state);
  });

  it("drops non-boolean entries from a corrupted expanded map", () => {
    const parsed = parseNavPreference(
      JSON.stringify({ mode: "remember", expanded: { a: "yes", b: true } }),
    );
    expect(parsed.expanded).toEqual({ b: true });
  });
});

describe("resolveExpandedSubgroups", () => {
  const subgroupIds = ["taxpayerComplaints", "internalComplaints"];

  it("expandAll opens every rendered subgroup regardless of route or history (Scenario 4)", () => {
    const result = resolveExpandedSubgroups({
      mode: "expandAll",
      subgroupIds,
      activeSubgroupId: "internalComplaints",
      remembered: { taxpayerComplaints: false },
    });
    expect(result).toEqual({ taxpayerComplaints: true, internalComplaints: true });
  });

  it("auto opens only the subgroup owning the active route (Scenario 2, 6, 7)", () => {
    const result = resolveExpandedSubgroups({
      mode: "auto",
      subgroupIds,
      activeSubgroupId: "taxpayerComplaints",
    });
    expect(result).toEqual({ taxpayerComplaints: true, internalComplaints: false });
  });

  it("auto layers manual overrides on top of the active-route default", () => {
    const result = resolveExpandedSubgroups({
      mode: "auto",
      subgroupIds,
      activeSubgroupId: "taxpayerComplaints",
      overrides: { internalComplaints: true },
    });
    expect(result).toEqual({ taxpayerComplaints: true, internalComplaints: true });
  });

  it("remember uses the stored choice regardless of the active route (Scenario 3)", () => {
    const result = resolveExpandedSubgroups({
      mode: "remember",
      subgroupIds,
      activeSubgroupId: "internalComplaints",
      remembered: { taxpayerComplaints: true, internalComplaints: false },
    });
    expect(result).toEqual({ taxpayerComplaints: true, internalComplaints: false });
  });

  it("remember falls back to the active subgroup for a never-stored id", () => {
    const result = resolveExpandedSubgroups({
      mode: "remember",
      subgroupIds,
      activeSubgroupId: "internalComplaints",
      remembered: {},
    });
    expect(result).toEqual({ taxpayerComplaints: false, internalComplaints: true });
  });

  it("falls back to the first subgroup when nothing is active and nothing is remembered", () => {
    const result = resolveExpandedSubgroups({
      mode: "remember",
      subgroupIds,
      activeSubgroupId: null,
      remembered: {},
    });
    expect(result).toEqual({ taxpayerComplaints: true, internalComplaints: false });
  });

  it("only resolves subgroups actually passed in (permission filter already applied upstream, Scenario 5)", () => {
    const result = resolveExpandedSubgroups({
      mode: "expandAll",
      subgroupIds: ["taxpayerComplaints"],
    });
    expect(Object.keys(result)).toEqual(["taxpayerComplaints"]);
  });
});
