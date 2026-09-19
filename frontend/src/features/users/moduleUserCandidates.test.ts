import { describe, expect, it } from "vitest";
import {
  MODULE_USER_CANDIDATES,
  highlightMatchSegments,
  isHeadOfficeCandidate,
  searchModuleUserCandidates,
} from "./moduleUserCandidates";

describe("searchModuleUserCandidates", () => {
  it("loads 210 pending candidates with short lab usernames", () => {
    expect(MODULE_USER_CANDIDATES).toHaveLength(210);
    expect(MODULE_USER_CANDIDATES[0]?.username).toBe("3101");
    expect(MODULE_USER_CANDIDATES[1]?.username).toBe("3102");
  });

  it("covers both branch and head-office home units", () => {
    const headOffice = MODULE_USER_CANDIDATES.filter(isHeadOfficeCandidate);
    expect(headOffice.length).toBeGreaterThan(0);
    expect(headOffice.length).toBeLessThan(MODULE_USER_CANDIDATES.length);
  });

  it("finds by id fragment and by name", () => {
    const byId = searchModuleUserCandidates("3101");
    expect(byId[0]?.username).toBe("3101");

    const sampleName = MODULE_USER_CANDIDATES[0]!.displayName.split(" ")[0]!;
    const byName = searchModuleUserCandidates(sampleName);
    expect(byName.length).toBeGreaterThan(0);
    expect(
      byName.every((row) =>
        row.displayName.toLowerCase().includes(sampleName.toLowerCase()),
      ),
    ).toBe(true);
  });

  it("finds the same person by 16-digit identity, short id, name, or unit", () => {
    const joko = MODULE_USER_CANDIDATES.find((row) => row.username === "3104");
    expect(joko?.displayName).toBe("Joko Siregar");

    expect(searchModuleUserCandidates("3104")[0]?.username).toBe("3104");
    expect(searchModuleUserCandidates("3100000000000004")[0]?.username).toBe(
      "3104",
    );
    expect(searchModuleUserCandidates("joko")[0]?.username).toBe("3104");
    expect(
      searchModuleUserCandidates("Tanah Abang").some((row) => row.username === "3104"),
    ).toBe(true);
  });

  it("excludes already-registered usernames", () => {
    const first = MODULE_USER_CANDIDATES[0]!.username;
    const hits = searchModuleUserCandidates(first, {
      excludeUsernames: new Set([first]),
    });
    expect(hits.every((row) => row.username !== first)).toBe(true);
  });

  it("excludes a registered short id when searching the 16-digit identity", () => {
    const hits = searchModuleUserCandidates("3100000000000001", {
      excludeUsernames: new Set(["3101"]),
    });
    expect(hits.every((row) => row.username !== "3101")).toBe(true);
  });
});

describe("highlightMatchSegments", () => {
  it("bolds the typed ID prefix and leaves the rest unmatched", () => {
    expect(highlightMatchSegments("3101", "31")).toEqual([
      { text: "31", matched: true },
      { text: "01", matched: false },
    ]);
  });

  it("is case-insensitive for names", () => {
    expect(highlightMatchSegments("Ahmad Santoso", "ahmad")).toEqual([
      { text: "Ahmad", matched: true },
      { text: " Santoso", matched: false },
    ]);
  });

  it("returns the full text unmatched when query is empty or missing", () => {
    expect(highlightMatchSegments("3101", "")).toEqual([
      { text: "3101", matched: false },
    ]);
    expect(highlightMatchSegments("3101", "999")).toEqual([
      { text: "3101", matched: false },
    ]);
  });
});
