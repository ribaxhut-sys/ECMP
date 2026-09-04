import { describe, expect, it } from "vitest";

import { appendPreset } from "./ReasonPresetTags";

describe("appendPreset", () => {
  it("mengisi field kosong dengan preset", () => {
    expect(appendPreset("", "Berkas kurang")).toBe("Berkas kurang");
    expect(appendPreset("   \n", "Berkas kurang")).toBe("Berkas kurang");
  });

  it("menambahkan preset tanpa menghapus teks yang sudah ada", () => {
    expect(appendPreset("Sudah dicek ke lapangan", "Berkas kurang")).toBe(
      "Sudah dicek ke lapangan\nBerkas kurang",
    );
  });

  it("tidak menambahkan preset yang sudah ada di teks", () => {
    const current = "Berkas kurang\nSudah dicek";
    expect(appendPreset(current, "Berkas kurang")).toBe(current);
  });
});
