import { describe, expect, it } from "vitest";
import { isUserDirectoryId, officerDisplayName } from "./officerDisplayName";

describe("officerDisplayName", () => {
  it("prefers a human name over a user id", () => {
    expect(
      officerDisplayName(
        "bd0b9a73-72f4-4173-93f2-c5f6733a0415",
        "Ahmad Santoso",
      ),
    ).toBe("Ahmad Santoso");
  });

  it("returns null when only a user id is available", () => {
    expect(
      officerDisplayName("bd0b9a73-72f4-4173-93f2-c5f6733a0415"),
    ).toBeNull();
  });

  it("detects directory ids", () => {
    expect(isUserDirectoryId("bd0b9a73-72f4-4173-93f2-c5f6733a0415")).toBe(
      true,
    );
    expect(isUserDirectoryId("Ahmad Santoso")).toBe(false);
  });
});
