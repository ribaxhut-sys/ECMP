import { describe, expect, it } from "vitest";
import {
  isAwaitingCompletion,
  mayResendToPusat,
  mayReturnForCompletion,
} from "./completionGate";

describe("completionGate", () => {
  it("lets Pusat return a branch ticket before or after receive", () => {
    const base = {
      actorUnitCode: "PUSAT",
      ownerUnitId: "UPPPD-TANAH-ABANG",
      handlingUnitId: "PUSAT",
      hasUpdatePermission: true,
      completionRequestStatus: null as string | null,
    };
    expect(mayReturnForCompletion({ ...base, status: "ASSIGNED" })).toBe(true);
    expect(mayReturnForCompletion({ ...base, status: "IN_PROGRESS" })).toBe(true);
    expect(
      mayReturnForCompletion({
        ...base,
        status: "ASSIGNED",
        actorUnitCode: "UPPPD-TANAH-ABANG",
      }),
    ).toBe(false);
    expect(
      mayReturnForCompletion({
        ...base,
        status: "IN_PROGRESS",
        actorUnitCode: "PUSAT",
        handlingUnitId: "PUSAT-CRO",
        roles: ["AGENT"],
      }),
    ).toBe(true);
    expect(
      mayReturnForCompletion({
        ...base,
        status: "IN_PROGRESS",
        withdrawRequestStatus: "PENDING",
      }),
    ).toBe(false);
  });

  it("hides return once already awaiting completion", () => {
    expect(
      mayReturnForCompletion({
        status: "ASSIGNED",
        actorUnitCode: "PUSAT",
        ownerUnitId: "UPPPD-TANAH-ABANG",
        handlingUnitId: "PUSAT",
        hasUpdatePermission: true,
        completionRequestStatus: "PENDING",
      }),
    ).toBe(false);
  });

  it("lets the owner branch resend after completing documents", () => {
    expect(isAwaitingCompletion("PENDING")).toBe(true);
    expect(
      mayResendToPusat({
        status: "ASSIGNED",
        actorUnitCode: "UPPPD-TANAH-ABANG",
        ownerUnitId: "UPPPD-TANAH-ABANG",
        handlingUnitId: "UPPPD-TANAH-ABANG",
        hasUpdatePermission: true,
        completionRequestStatus: "PENDING",
      }),
    ).toBe(true);
    expect(
      mayResendToPusat({
        status: "ASSIGNED",
        actorUnitCode: "PUSAT",
        ownerUnitId: "UPPPD-TANAH-ABANG",
        handlingUnitId: "UPPPD-TANAH-ABANG",
        hasUpdatePermission: true,
        completionRequestStatus: "PENDING",
      }),
    ).toBe(false);
  });
});
