import { describe, expect, it } from "vitest";
import {
  INTERNAL_RESOLUTION_SENTINEL,
  buildInternalResolveRequest,
} from "./resolvePayload";

describe("buildInternalResolveRequest", () => {
  it("sends IC_DONE and never a free-text code", () => {
    const result = buildInternalResolveRequest({
      action: "ACCEPT",
      summary: "Tindakan sudah diambil",
      comment: "Selesai di unit",
    });
    expect(result).toEqual({
      ok: true,
      body: {
        action: "ACCEPT",
        summary: "Tindakan sudah diambil",
        comment: "Selesai di unit",
        resolutionCode: INTERNAL_RESOLUTION_SENTINEL,
      },
    });
    expect(INTERNAL_RESOLUTION_SENTINEL).toBe("IC_DONE");
  });

  it("requires summary and comment", () => {
    expect(
      buildInternalResolveRequest({
        action: "PROPOSE",
        summary: "  ",
        comment: "ok",
      }),
    ).toEqual({ ok: false, error: "resolutionSummaryRequiredError" });
    expect(
      buildInternalResolveRequest({
        action: "PROPOSE",
        summary: "ok",
        comment: "",
      }),
    ).toEqual({ ok: false, error: "commentRequiredError" });
  });
});
