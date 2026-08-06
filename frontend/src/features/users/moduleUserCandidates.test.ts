import { describe, expect, it } from "vitest";
import {
  MODULE_USER_CANDIDATES,
  highlightMatchSegments,
  isHeadOfficeCandidate,
  searchModuleUserCandidates,
} from "./moduleUserCandidates";

describe("searchModuleUserCandidates", () => {
  it("loads 210 pending candidates with 16-digit usernames", () => {
    expect(MODULE_USER_CANDIDATES).toHaveLength(210);
    expect(MODULE_USER_CANDIDATES[0]?.username).toMatch(/^\d{16}$/);
  });

  it("covers both branch and head-office home units", () => {
    const headOffice = MODULE_USER_CANDIDATES.filter(isHeadOfficeCandidate);
    expect(headOffice.length).toBeGreaterThan(0);
    expect(headOffice.length).toBeLessThan(MODULE_USER_CANDIDATES.length);
  });

  it("finds by id fragment and by name", () => {
    const byId = searchModuleUserCandidates("3100000000000001");
    expect(byId[0]?.username).toBe("3100000000000001");

    const sampleName = MODULE_USER_CANDIDATES[0]!.displayName.split(" ")[0]!;
    const byName = searchModuleUserCandidates(sampleName);
    expect(byName.length).toBeGreaterThan(0);
    expect(
      byName.every((row) =>
        row.displayName.toLowerCase().includes(sampleName.toLowerCase()),
      ),
    ).toBe(true);
  });

  it("excludes already-registered usernames", () => {
    const first = MODULE_USER_CANDIDATES[0]!.username;
    const hits = searchModuleUserCandidates(first, {
      excludeUsernames: new Set([first]),
    });
    expect(hits.every((row) => row.username !== first)).toBe(true);
  });
});

describe("highlightMatchSegments", () => {
  it("bolds the typed ID prefix and leaves the rest unmatched", () => {
    expect(highlightMatchSegments("3100000000000001", "31000")).toEqual([
      { text: "31000", matched: true },
      { text: "00000000001", matched: false },
    ]);
  });

  it("is case-insensitive for names", () => {
    expect(highlightMatchSegments("Ahmad Santoso", "ahmad")).toEqual([
      { text: "Ahmad", matched: true },
      { text: " Santoso", matched: false },
    ]);
  });

  it("returns the full text unmatched when query is empty or missing", () => {
    expect(highlightMatchSegments("3100000000000001", "")).toEqual([
      { text: "3100000000000001", matched: false },
    ]);
    expect(highlightMatchSegments("3100000000000001", "999")).toEqual([
      { text: "3100000000000001", matched: false },
    ]);
  });
});
