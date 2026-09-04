import { describe, expect, it } from "vitest";
import {
  allowedInternalAcceptanceParties,
  isBlockedBySelfApproval,
  mayRecordInternalAcceptance,
  visibleInternalAcceptanceActions,
} from "./acceptanceGate";

const ticket = {
  ownerUnitId: "UPPPD-TANAH-ABANG",
  handlingUnitId: "PUSAT",
  creatorUserId: "user-3102",
};

describe("mayRecordInternalAcceptance", () => {
  it("does not let CRO close — Staff KaSatPel/KaSatPel must approve", () => {
    const base = {
      roles: ["AGENT"],
      actorUnitCode: "PUSAT",
      actorUserId: "user-31206",
      ...ticket,
    };
    expect(
      mayRecordInternalAcceptance({ ...base, party: "HANDLING_UNIT" }),
    ).toBe(false);
    expect(
      mayRecordInternalAcceptance({ ...base, party: "OWNER" }),
    ).toBe(false);
    expect(
      mayRecordInternalAcceptance({
        roles: ["AGENT"],
        actorUnitCode: "UPPPD-TANAH-ABANG",
        actorUserId: "user-3101",
        ...ticket,
        party: "OWNER",
      }),
    ).toBe(false);
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
    ).toBe(false);
  });

  it("lets Staff KaSatPel Pusat accept handling on a legacy CRO unit", () => {
    expect(
      mayRecordInternalAcceptance({
        roles: ["SUPERVISOR"],
        actorUnitCode: "PUSAT",
        actorUserId: "user-31206",
        ownerUnitId: "UPPPD-TANAH-ABANG",
        handlingUnitId: "PUSAT-CRO",
        creatorUserId: "user-3102",
        party: "HANDLING_UNIT",
      }),
    ).toBe(true);
  });

  it("lets Staff KaSatPel owner accept when actor unit is owner", () => {
    expect(
      mayRecordInternalAcceptance({
        roles: ["SUPERVISOR"],
        actorUnitCode: "UPPPD-TANAH-ABANG",
        actorUserId: "user-3101",
        ...ticket,
        party: "OWNER",
      }),
    ).toBe(true);
  });

  it("does not let CRO close a local ticket they created", () => {
    expect(
      allowedInternalAcceptanceParties({
        roles: ["AGENT"],
        actorUnitCode: "PUSAT",
        actorUserId: "u1",
        ownerUnitId: "PUSAT",
        handlingUnitId: "PUSAT",
        creatorUserId: "u1",
      }),
    ).toEqual([]);
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

  it("blocks CRO from accepting even if they created it", () => {
    expect(
      mayRecordInternalAcceptance({
        roles: ["AGENT"],
        actorUnitCode: "UPPPD-TANAH-ABANG",
        actorUserId: "creator-agent",
        ownerUnitId: "UPPPD-TANAH-ABANG",
        handlingUnitId: "PUSAT",
        creatorUserId: "creator-agent",
        party: "OWNER",
      }),
    ).toBe(false);
  });
});

describe("visibleInternalAcceptanceActions", () => {
  const actor = {
    hasUpdatePermission: true,
    actorUnitReady: true,
    roles: ["SUPERVISOR"],
    actorUnitCode: "PUSAT",
    actorUserId: "user-31206",
    ...ticket,
    status: "RESOLVED",
    handlingUnitAcceptance: null as string | null,
    ownerAcceptance: null as string | null,
  };

  it("shows only handling accept for Pusat Staff KaSatPel before they accept", () => {
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

  it("hides close actions for CRO Pusat", () => {
    expect(
      visibleInternalAcceptanceActions({
        ...actor,
        roles: ["AGENT"],
      }),
    ).toEqual({
      acceptHandling: false,
      acceptOwner: false,
      rejectParties: [],
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

  it("local gate: Staff KaSatPel who created the ticket may close it", () => {
    expect(
      visibleInternalAcceptanceActions({
        hasUpdatePermission: true,
        actorUnitReady: true,
        roles: ["SUPERVISOR"],
        actorUnitCode: "UPPPD-TANAH-ABANG",
        actorUserId: "sv-creator",
        ownerUnitId: "UPPPD-TANAH-ABANG",
        handlingUnitId: "UPPPD-TANAH-ABANG",
        creatorUserId: "sv-creator",
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
});

describe("isBlockedBySelfApproval", () => {
  const base = {
    status: "RESOLVED",
    hasUpdatePermission: true,
    actorUnitReady: true,
    actorUserId: "creator-1",
    creatorUserId: "creator-1",
    actorUnitCode: "UPPPD-TANAH-ABANG",
    ownerUnitId: "UPPPD-TANAH-ABANG",
  };

  it("does not block Staff KaSatPel or KaSatPel on their own owner unit", () => {
    expect(isBlockedBySelfApproval({ ...base, roles: ["SUPERVISOR"] })).toBe(
      false,
    );
    expect(isBlockedBySelfApproval({ ...base, roles: ["MANAGER"] })).toBe(
      false,
    );
  });

  it("blocks Admin creators", () => {
    expect(isBlockedBySelfApproval({ ...base, roles: ["ADMIN"] })).toBe(true);
  });

  it("blocks CRO creators — they need Staff KaSatPel/KaSatPel to close", () => {
    expect(isBlockedBySelfApproval({ ...base, roles: ["AGENT"] })).toBe(true);
  });
});
