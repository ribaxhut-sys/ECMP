import { describe, expect, it } from "vitest";
import {
  allowedInternalAcceptanceParties,
  mayRecordInternalAcceptance,
  visibleInternalAcceptanceActions,
} from "./acceptanceGate";

const ticket = {
  ownerUnitId: "UPPPD-TANAH-ABANG",
  handlingUnitId: "PUSAT",
  creatorUserId: "user-3102",
};

describe("mayRecordInternalAcceptance", () => {
  it("allows agent only on own handling unit", () => {
    const base = {
      roles: ["AGENT"],
      actorUnitCode: "PUSAT",
      actorUserId: "user-31206",
      ...ticket,
    };
    expect(
      mayRecordInternalAcceptance({ ...base, party: "HANDLING_UNIT" }),
    ).toBe(true);
    expect(mayRecordInternalAcceptance({ ...base, party: "OWNER" })).toBe(
      false,
    );
  });

  it("allows agent owner only when actor unit is owner", () => {
    const base = {
      roles: ["AGENT"],
      actorUnitCode: "UPPPD-TANAH-ABANG",
      actorUserId: "user-3101",
      ...ticket,
    };
    expect(mayRecordInternalAcceptance({ ...base, party: "OWNER" })).toBe(
      true,
    );
    expect(
      mayRecordInternalAcceptance({ ...base, party: "HANDLING_UNIT" }),
    ).toBe(false);
  });

  it("allows both parties when owner and handling are the same unit", () => {
    expect(
      allowedInternalAcceptanceParties({
        roles: ["AGENT"],
        actorUnitCode: "PUSAT",
        actorUserId: "u1",
        ownerUnitId: "PUSAT",
        handlingUnitId: "PUSAT",
        creatorUserId: "other",
      }),
    ).toEqual(["HANDLING_UNIT", "OWNER"]);
  });

  it("allows admin any party without a branch", () => {
    expect(
      allowedInternalAcceptanceParties({
        roles: ["ADMIN"],
        actorUnitCode: null,
        actorUserId: "admin-1",
        ...ticket,
      }),
    ).toEqual(["HANDLING_UNIT", "OWNER"]);
  });

  it("allows supervisor who created the complaint to act on their own unit", () => {
    expect(
      allowedInternalAcceptanceParties({
        roles: ["SUPERVISOR"],
        actorUnitCode: "UPPPD-TANAH-ABANG",
        actorUserId: "user-3102",
        ...ticket,
      }),
    ).toEqual(["OWNER"]);
  });

  it("blocks supervisor who created the complaint when acting cross-unit", () => {
    expect(
      allowedInternalAcceptanceParties({
        roles: ["SUPERVISOR"],
        actorUnitCode: "OTHER-UNIT",
        actorUserId: "user-3102",
        ...ticket,
      }),
    ).toEqual([]);
  });

  it("allows agent to accept own-unit even if they created it", () => {
    expect(
      mayRecordInternalAcceptance({
        roles: ["AGENT"],
        actorUnitCode: "PUSAT",
        actorUserId: "creator-agent",
        ownerUnitId: "UPPPD-TANAH-ABANG",
        handlingUnitId: "PUSAT",
        creatorUserId: "creator-agent",
        party: "HANDLING_UNIT",
      }),
    ).toBe(true);
  });
});

describe("visibleInternalAcceptanceActions", () => {
  const actor = {
    hasUpdatePermission: true,
    actorUnitReady: true,
    roles: ["AGENT"],
    actorUnitCode: "PUSAT",
    actorUserId: "user-31206",
    ...ticket,
    status: "RESOLVED",
    handlingUnitAcceptance: null as string | null,
    ownerAcceptance: null as string | null,
  };

  it("shows only handling accept for Pusat agent before they accept", () => {
    expect(visibleInternalAcceptanceActions(actor)).toEqual({
      acceptHandling: true,
      acceptOwner: false,
      rejectParties: ["HANDLING_UNIT"],
      gate: "transferred",
    });
  });

  it("hides handling accept after that party already accepted", () => {
    expect(
      visibleInternalAcceptanceActions({
        ...actor,
        handlingUnitAcceptance: "ACCEPT",
      }),
    ).toEqual({
      acceptHandling: false,
      acceptOwner: false,
      rejectParties: ["HANDLING_UNIT"],
      gate: "transferred",
    });
  });

  it("hides actions until org unit is resolved", () => {
    expect(
      visibleInternalAcceptanceActions({ ...actor, actorUnitReady: false }),
    ).toEqual({
      acceptHandling: false,
      acceptOwner: false,
      rejectParties: [],
      gate: "transferred",
    });
  });

  it("local gate: supervisor sees a single owner close, not handling accept", () => {
    expect(
      visibleInternalAcceptanceActions({
        hasUpdatePermission: true,
        actorUnitReady: true,
        roles: ["SUPERVISOR"],
        actorUnitCode: "UPPPD-TANAH-ABANG",
        actorUserId: "sup-1",
        ownerUnitId: "UPPPD-TANAH-ABANG",
        handlingUnitId: "UPPPD-TANAH-ABANG",
        creatorUserId: "agent-1",
        status: "RESOLVED",
        handlingUnitAcceptance: "ACCEPT",
        ownerAcceptance: null,
      }),
    ).toEqual({
      acceptHandling: false,
      acceptOwner: true,
      rejectParties: ["OWNER"],
      gate: "local",
    });
  });

  it("local gate: agent cannot close after resolve", () => {
    expect(
      visibleInternalAcceptanceActions({
        hasUpdatePermission: true,
        actorUnitReady: true,
        roles: ["AGENT"],
        actorUnitCode: "UPPPD-TANAH-ABANG",
        actorUserId: "agent-1",
        ownerUnitId: "UPPPD-TANAH-ABANG",
        handlingUnitId: "UPPPD-TANAH-ABANG",
        creatorUserId: "agent-1",
        status: "RESOLVED",
        handlingUnitAcceptance: "ACCEPT",
        ownerAcceptance: null,
      }),
    ).toEqual({
      acceptHandling: false,
      acceptOwner: false,
      rejectParties: [],
      gate: "local",
    });
  });
});
