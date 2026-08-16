import { describe, expect, it } from "vitest";
import { disambiguateInitials, nameInitials } from "./initials";

describe("nameInitials", () => {
  it("uses the first letter of the first three words", () => {
    expect(nameInitials("Budi Santoso Pratama")).toBe("BSP");
    expect(nameInitials("Muhammad Ali Akbar Sitorus")).toBe("MAA");
  });

  it("uses first letter + two letters of the last word for two-word names", () => {
    expect(nameInitials("Budi Santoso")).toBe("BSA");
    expect(nameInitials("Andi Wijaya")).toBe("AWI");
    expect(nameInitials("John Doe")).toBe("JDO");
  });

  it("falls back to the leading letters when the last word is a single letter", () => {
    expect(nameInitials("Ali B")).toBe("ALB");
  });

  it("uses the first three letters of a single-word name", () => {
    expect(nameInitials("Administrator")).toBe("ADM");
    expect(nameInitials("Elena")).toBe("ELE");
    expect(nameInitials("ops")).toBe("OPS");
  });

  it("ignores surrounding whitespace and extra spaces", () => {
    expect(nameInitials("  Budi   Santoso  ")).toBe("BSA");
  });

  it("returns null for empty input", () => {
    expect(nameInitials("")).toBeNull();
    expect(nameInitials("   ")).toBeNull();
    expect(nameInitials(null)).toBeNull();
    expect(nameInitials(undefined)).toBeNull();
  });

  it("never returns more than three characters", () => {
    for (const name of [
      "Budi Santoso",
      "Budi Santoso Pratama",
      "Muhammad Ali Akbar Sitorus",
      "Administrator",
      "a b c d e",
      "user@example.com",
    ]) {
      expect(nameInitials(name)!.length).toBeLessThanOrEqual(3);
    }
  });
});

describe("disambiguateInitials", () => {
  it("keeps the natural code when nobody collides", () => {
    const map = disambiguateInitials([
      { key: "u1", name: "Budi Santoso" },
      { key: "u2", name: "Andi Wijaya" },
    ]);
    expect(map.get("u1")).toBe("BSA");
    expect(map.get("u2")).toBe("AWI");
  });

  it("gives two people with the same name different initials", () => {
    const map = disambiguateInitials([
      { key: "u1", name: "Budi Santoso" },
      { key: "u2", name: "Budi Santoso" },
    ]);
    expect(map.get("u1")).toBe("BSA");
    expect(map.get("u2")).toBe("BSN");
    expect(map.get("u1")).not.toBe(map.get("u2"));
  });

  it("separates different names that collapse to the same code", () => {
    const map = disambiguateInitials([
      { key: "u1", name: "Budi Santoso" },
      { key: "u2", name: "Bagus Sanjaya" },
    ]);
    expect(map.get("u1")).toBe("BSA");
    expect(map.get("u2")).toBe("BSN");
  });

  it("is stable regardless of input order", () => {
    const entries = [
      { key: "u2", name: "Budi Santoso" },
      { key: "u1", name: "Budi Santoso" },
    ];
    const forward = disambiguateInitials(entries);
    const reverse = disambiguateInitials([...entries].reverse());
    expect(forward.get("u1")).toBe(reverse.get("u1"));
    expect(forward.get("u2")).toBe(reverse.get("u2"));
  });

  it("treats repeated keys as one person", () => {
    const map = disambiguateInitials([
      { key: "u1", name: "Budi Santoso" },
      { key: "u1", name: "Budi Santoso" },
    ]);
    expect(map.get("u1")).toBe("BSA");
    expect(map.size).toBe(1);
  });

  it("keeps every assignment unique and exactly three letters", () => {
    const map = disambiguateInitials(
      Array.from({ length: 12 }, (_, i) => ({
        key: `u${i}`,
        name: "Budi Santoso",
      })),
    );
    const codes = [...map.values()];
    expect(codes).toHaveLength(12);
    expect(new Set(codes).size).toBe(12);
    for (const code of codes) expect(code).toHaveLength(3);
  });

  it("skips entries without a usable name", () => {
    const map = disambiguateInitials([
      { key: "u1", name: "" },
      { key: "u2", name: null },
    ]);
    expect(map.size).toBe(0);
  });
});
