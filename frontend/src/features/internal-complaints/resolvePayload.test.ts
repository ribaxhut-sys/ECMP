import { describe, expect, it } from "vitest";
import {
  INTERNAL_RESOLUTION_SENTINEL,
  buildInternalResolveRequest,
} from "./resolvePayload";

describe("buildInternalResolveRequest", () => {
  it("sends IC_DONE for PROPOSE with summary and comment", () => {
    const result = buildInternalResolveRequest({
      action: "PROPOSE",
      summary: "Tindakan sudah diambil",
      comment: "Selesai di unit",
    });
    expect(result).toEqual({
      ok: true,
      body: {
        action: "PROPOSE",
        summary: "Tindakan sudah diambil",
        comment: "Selesai di unit",
        resolutionCode: INTERNAL_RESOLUTION_SENTINEL,
      },
    });
    expect(INTERNAL_RESOLUTION_SENTINEL).toBe("IC_DONE");
  });

  it("ACCEPT does not require a new summary", () => {
    expect(
      buildInternalResolveRequest({
        action: "ACCEPT",
        summary: "",
        comment: "",
      }),
    ).toEqual({
      ok: true,
      body: {
        action: "ACCEPT",
        comment: "Usulan diterima",
        resolutionCode: INTERNAL_RESOLUTION_SENTINEL,
      },
    });
  });

  it("REJECT requires a reason", () => {
    expect(
      buildInternalResolveRequest({
        action: "REJECT",
        summary: "",
        comment: "",
      }),
    ).toEqual({ ok: false, error: "rejectProposalReasonRequiredError" });
    expect(
      buildInternalResolveRequest({
        action: "REJECT",
        summary: "",
        comment: "Belum lengkap",
      }),
    ).toEqual({
      ok: true,
      body: {
        action: "REJECT",
        comment: "Belum lengkap",
        rejectionReason: "Belum lengkap",
        resolutionCode: INTERNAL_RESOLUTION_SENTINEL,
      },
    });
  });

  it("requires summary and comment for PROPOSE", () => {
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
