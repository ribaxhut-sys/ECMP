import { describe, expect, it } from "vitest";
import { isUserDirectoryId, officerDisplayName, officerInitials } from "./officerDisplayName";

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

  it("builds three-letter initials from a human name", () => {
    expect(officerInitials("Ahmad Santoso")).toBe("ASA");
    expect(officerInitials("Ahmad Santoso Adi")).toBe("ASA");
    expect(officerInitials("Ahmad")).toBe("AHM");
    expect(officerInitials("bd0b9a73-72f4-4173-93f2-c5f6733a0415")).toBeNull();
  });
});
