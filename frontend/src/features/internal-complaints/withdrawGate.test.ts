import { describe, expect, it } from "vitest";
import {
  isWaitingForPusatReceive,
  mayDecideWithdraw,
  mayOwnerWithdraw,
  mayReceiveInternal,
  mayRequestWithdraw,
} from "./withdrawGate";

describe("withdrawGate", () => {
  it("treats branch ASSIGNED-to-Pusat as waiting for receive", () => {
    expect(
      isWaitingForPusatReceive({
        status: "ASSIGNED",
        ownerUnitId: "UPPPD-GAMBIR",
        handlingUnitId: "PUSAT",
      }),
    ).toBe(true);
    expect(
      isWaitingForPusatReceive({
        status: "IN_PROGRESS",
        ownerUnitId: "UPPPD-GAMBIR",
        handlingUnitId: "PUSAT",
      }),
    ).toBe(false);
  });

  it("hides Terima from the branch owner", () => {
    expect(
      mayReceiveInternal({
        status: "ASSIGNED",
        actorUnitCode: "UPPPD-GAMBIR",
        handlingUnitId: "PUSAT",
        hasUpdatePermission: true,
      }),
    ).toBe(false);
    expect(
      mayReceiveInternal({
        status: "ASSIGNED",
        actorUnitCode: "PUSAT",
        handlingUnitId: "PUSAT",
        hasUpdatePermission: true,
      }),
    ).toBe(true);
    expect(
      mayReceiveInternal({
        status: "ASSIGNED",
        actorUnitCode: "PUSAT",
        handlingUnitId: "PUSAT",
        hasUpdatePermission: true,
        completionRequestStatus: "PENDING",
      }),
    ).toBe(false);
  });

  it("lets any Pusat login Terima even when handling is a legacy sub-unit", () => {
    expect(
      mayReceiveInternal({
        status: "ASSIGNED",
        actorUnitCode: "PUSAT",
        handlingUnitId: "PUSAT-CRO",
        hasUpdatePermission: true,
        roles: ["AGENT"],
      }),
    ).toBe(true);
    expect(
      mayReceiveInternal({
        status: "ASSIGNED",
        actorUnitCode: null,
        handlingUnitId: "PUSAT",
        hasUpdatePermission: true,
        roles: ["ADMIN"],
      }),
    ).toBe(true);
    expect(
      mayReceiveInternal({
        status: "ASSIGNED",
        actorUnitCode: null,
        handlingUnitId: "PUSAT",
        hasUpdatePermission: true,
        roles: ["AGENT"],
      }),
    ).toBe(false);
  });

  it("allows creator or owner-unit supervisor to withdraw", () => {
    expect(
      mayOwnerWithdraw({
        roles: ["AGENT"],
        actorUserId: "u1",
        creatorUserId: "u1",
        actorUnitCode: "UPPPD-GAMBIR",
        ownerUnitId: "UPPPD-GAMBIR",
        hasAssignPermission: false,
      }),
    ).toBe(true);
    expect(
      mayOwnerWithdraw({
        roles: ["SUPERVISOR"],
        actorUserId: "sv",
        creatorUserId: "u1",
        actorUnitCode: "UPPPD-GAMBIR",
        ownerUnitId: "UPPPD-GAMBIR",
        hasAssignPermission: true,
      }),
    ).toBe(true);
  });

  it("allows a withdraw request only after Pusat received", () => {
    const base = {
      ownerUnitId: "UPPPD-GAMBIR",
      handlingUnitId: "PUSAT",
      withdrawRequestStatus: null as string | null,
      roles: ["SUPERVISOR"],
      actorUserId: "sv",
      creatorUserId: "u1",
      actorUnitCode: "UPPPD-GAMBIR",
      hasAssignPermission: true,
    };
    expect(mayRequestWithdraw({ ...base, status: "ASSIGNED" })).toBe(false);
    expect(mayRequestWithdraw({ ...base, status: "IN_PROGRESS" })).toBe(true);
    expect(
      mayRequestWithdraw({
        ...base,
        status: "IN_PROGRESS",
        withdrawRequestStatus: "PENDING",
      }),
    ).toBe(false);
  });

  it("lets Pusat decide a pending withdraw request", () => {
    expect(
      mayDecideWithdraw({
        withdrawRequestStatus: "PENDING",
        roles: ["SUPERVISOR"],
        actorUnitCode: "PUSAT",
        handlingUnitId: "PUSAT",
        hasAssignPermission: true,
        hasEscalateDecidePermission: false,
      }),
    ).toBe(true);
    expect(
      mayDecideWithdraw({
        withdrawRequestStatus: "PENDING",
        roles: ["SUPERVISOR"],
        actorUnitCode: "UPPPD-GAMBIR",
        handlingUnitId: "PUSAT",
        hasAssignPermission: true,
        hasEscalateDecidePermission: false,
      }),
    ).toBe(false);
    expect(
      mayDecideWithdraw({
        withdrawRequestStatus: "PENDING",
        roles: ["SUPERVISOR"],
        actorUnitCode: "PUSAT",
        handlingUnitId: "PUSAT-CRO",
        hasAssignPermission: true,
        hasEscalateDecidePermission: false,
      }),
    ).toBe(true);
  });
});
