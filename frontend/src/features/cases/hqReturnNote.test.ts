import { describe, expect, it } from "vitest";
import {
  formatHqReturnNoteDisplay,
  splitHqReturnNote,
} from "./hqReturnNote";

describe("splitHqReturnNote", () => {
  it("reads a known reason code prefix", () => {
    expect(
      splitHqReturnNote(
        "[INCOMPLETE_CHRONOLOGY] Pendaftaran dapat dilakukan di kantor upppd",
      ),
    ).toEqual({
      code: "INCOMPLETE_CHRONOLOGY",
      body: "Pendaftaran dapat dilakukan di kantor upppd",
    });
  });

  it("leaves unknown brackets as body", () => {
    expect(splitHqReturnNote("[NOT_A_REASON] hello")).toEqual({
      code: null,
      body: "[NOT_A_REASON] hello",
    });
  });
});

describe("formatHqReturnNoteDisplay", () => {
  it("replaces the code with a human label", () => {
    expect(
      formatHqReturnNoteDisplay(
        "[INCOMPLETE_CHRONOLOGY] Pendaftaran dapat dilakukan di kantor upppd",
        () => "Kronologi tidak lengkap",
      ),
    ).toBe(
      "Kronologi tidak lengkap — Pendaftaran dapat dilakukan di kantor upppd",
    );
  });
});
