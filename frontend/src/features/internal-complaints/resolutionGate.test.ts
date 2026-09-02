import { describe, expect, it } from "vitest";
import {
  isPendingResolutionProposal,
  mayDecideResolutionProposal,
  mayProposeResolution,
  visibleInternalResolutionActions,
} from "./resolutionGate";

const transferred = {
  status: "IN_PROGRESS",
  ownerUnitId: "UPPPD-TANAH-ABANG",
  handlingUnitId: "PUSAT",
  hasUpdatePermission: true,
};

describe("resolutionGate", () => {
  it("treats only PENDING_APPROVAL as a live proposal", () => {
    expect(isPendingResolutionProposal("PENDING_APPROVAL")).toBe(true);
    expect(isPendingResolutionProposal("ACCEPTED")).toBe(false);
    expect(isPendingResolutionProposal(null)).toBe(false);
  });

  it("lets the handling unit propose, not the owner unit", () => {
    expect(
      mayProposeResolution({
        ...transferred,
        actorUnitCode: "PUSAT",
        roles: ["AGENT"],
      }),
    ).toBe(true);
    expect(
      mayProposeResolution({
        ...transferred,
        actorUnitCode: "UPPPD-TANAH-ABANG",
        roles: ["AGENT"],
      }),
    ).toBe(false);
    expect(
      mayProposeResolution({
        ...transferred,
        actorUnitCode: "PUSAT",
        handlingUnitId: "PUSAT-CRO",
        roles: ["AGENT"],
      }),
    ).toBe(true);
    expect(
      mayProposeResolution({
        ...transferred,
        actorUnitCode: null,
        roles: ["ADMIN"],
      }),
    ).toBe(true);
    expect(
      mayProposeResolution({
        ...transferred,
        status: "ASSIGNED",
        actorUnitCode: "PUSAT",
        roles: ["AGENT"],
      }),
    ).toBe(true);
    expect(
      mayProposeResolution({
        ...transferred,
        status: "ASSIGNED",
        actorUnitCode: "PUSAT",
        roles: ["AGENT"],
        completionRequestStatus: "PENDING",
      }),
    ).toBe(false);
    expect(
      mayProposeResolution({
        ...transferred,
        status: "ASSIGNED",
        actorUnitCode: "UPPPD-TANAH-ABANG",
        roles: ["AGENT"],
      }),
    ).toBe(false);
  });

  it("lets the owner unit accept a pending proposal, not the proposer", () => {
    const pending = {
      ...transferred,
      resolutionStatus: "PENDING_APPROVAL",
      proposedBy: "handler-1",
      roles: ["AGENT"] as const,
    };
    expect(
      mayDecideResolutionProposal({
        ...pending,
        actorUnitCode: "UPPPD-TANAH-ABANG",
        actorUserId: "owner-1",
      }),
    ).toBe(true);
    expect(
      mayDecideResolutionProposal({
        ...pending,
        actorUnitCode: "PUSAT",
        actorUserId: "handler-2",
      }),
    ).toBe(false);
    expect(
      mayDecideResolutionProposal({
        ...pending,
        actorUnitCode: "UPPPD-TANAH-ABANG",
        actorUserId: "handler-1",
      }),
    ).toBe(false);
  });

  it("hides accept when there is no pending proposal", () => {
    expect(
      mayDecideResolutionProposal({
        ...transferred,
        actorUnitCode: "UPPPD-TANAH-ABANG",
        actorUserId: "owner-1",
        proposedBy: null,
        resolutionStatus: null,
        roles: ["AGENT"],
      }),
    ).toBe(false);
  });

  it("shows waiting for the handling unit after they propose", () => {
    const actions = visibleInternalResolutionActions({
      ...transferred,
      actorUnitCode: "PUSAT",
      actorUserId: "handler-1",
      proposedBy: "handler-1",
      resolutionStatus: "PENDING_APPROVAL",
      roles: ["AGENT"],
    });
    expect(actions.mayDecide).toBe(false);
    expect(actions.waiting).toBe(true);
    expect(actions.showToolbar).toBe(true);
  });

  it("hides propose and review while a withdraw request is pending", () => {
    expect(
      mayProposeResolution({
        ...transferred,
        actorUnitCode: "PUSAT",
        roles: ["AGENT"],
        withdrawRequestStatus: "PENDING",
      }),
    ).toBe(false);
    const actions = visibleInternalResolutionActions({
      ...transferred,
      actorUnitCode: "PUSAT",
      actorUserId: "handler-1",
      proposedBy: "handler-1",
      resolutionStatus: "PENDING_APPROVAL",
      roles: ["AGENT"],
      withdrawRequestStatus: "PENDING",
    });
    expect(actions.showToolbar).toBe(false);
    expect(actions.mayPropose).toBe(false);
    expect(actions.waiting).toBe(false);
  });
});
