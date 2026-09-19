import { describe, expect, it } from "vitest";
import {
  INTERNAL_ACTION_HREF,
  INTERNAL_LIST_HREF,
  internalComplaintsNavHref,
  isActionNeededInternalComplaint,
  isIncomingInternalComplaint,
  isInternalInboxStatus,
} from "./internalInbox";

describe("internalInbox", () => {
  it("treats CREATED and ASSIGNED as inbox statuses", () => {
    expect(isInternalInboxStatus("CREATED")).toBe(true);
    expect(isInternalInboxStatus("ASSIGNED")).toBe(true);
    expect(isInternalInboxStatus("IN_PROGRESS")).toBe(false);
  });

  it("counts Cabang incoming only when handling is that branch", () => {
    expect(
      isIncomingInternalComplaint(
        { status: "ASSIGNED", handlingUnitId: "UPPPD-GAMBIR" },
        "UPPPD-GAMBIR",
      ),
    ).toBe(true);
    expect(
      isIncomingInternalComplaint(
        { status: "ASSIGNED", handlingUnitId: "PUSAT" },
        "UPPPD-GAMBIR",
      ),
    ).toBe(false);
    expect(
      isIncomingInternalComplaint(
        { status: "IN_PROGRESS", handlingUnitId: "UPPPD-GAMBIR" },
        "UPPPD-GAMBIR",
      ),
    ).toBe(false);
  });

  it("counts Pusat incoming for any Pusat handling unit", () => {
    expect(
      isIncomingInternalComplaint(
        { status: "ASSIGNED", handlingUnitId: "PUSAT" },
        "PUSAT-CRO",
      ),
    ).toBe(true);
    expect(
      isIncomingInternalComplaint(
        { status: "CREATED", handlingUnitId: "PUSAT-CRO" },
        "PUSAT",
      ),
    ).toBe(true);
    expect(
      isIncomingInternalComplaint(
        { status: "ASSIGNED", handlingUnitId: "UPPPD-GAMBIR" },
        "PUSAT",
      ),
    ).toBe(false);
  });

  it("badges owner-branch usulan, not the Pusat proposer", () => {
    const row = {
      status: "IN_PROGRESS",
      handlingUnitId: "PUSAT",
      ownerUnitId: "UPPPD-JOHAR-BARU",
      resolutionStatus: "PENDING_APPROVAL",
    };
    expect(isActionNeededInternalComplaint(row, "UPPPD-JOHAR-BARU")).toBe(true);
    expect(isActionNeededInternalComplaint(row, "PUSAT")).toBe(false);
  });

  it("does not badge Cabang when the latest resolution is already ACCEPTED", () => {
    const row = {
      status: "IN_PROGRESS",
      handlingUnitId: "PUSAT",
      ownerUnitId: "UPPPD-JOHAR-BARU",
      resolutionStatus: "ACCEPTED",
    };
    expect(isActionNeededInternalComplaint(row, "UPPPD-JOHAR-BARU")).toBe(
      false,
    );
    expect(isActionNeededInternalComplaint(row, "PUSAT")).toBe(true);
  });

  it("rebounds to Pusat after Cabang rejects a live usulan", () => {
    const row = {
      status: "IN_PROGRESS",
      handlingUnitId: "PUSAT",
      ownerUnitId: "UPPPD-JOHAR-BARU",
      resolutionStatus: "REJECTED",
    };
    expect(isActionNeededInternalComplaint(row, "PUSAT")).toBe(true);
    expect(isActionNeededInternalComplaint(row, "UPPPD-JOHAR-BARU")).toBe(
      false,
    );
  });

  it("badges Pusat for pending withdraw and both units for close-gate", () => {
    const withdraw = {
      status: "IN_PROGRESS",
      handlingUnitId: "PUSAT",
      ownerUnitId: "UPPPD-GAMBIR",
      withdrawRequestStatus: "PENDING",
    };
    expect(isActionNeededInternalComplaint(withdraw, "PUSAT")).toBe(true);
    expect(isActionNeededInternalComplaint(withdraw, "UPPPD-GAMBIR")).toBe(
      false,
    );

    const resolved = {
      status: "RESOLVED",
      handlingUnitId: "PUSAT",
      ownerUnitId: "UPPPD-GAMBIR",
    };
    expect(isActionNeededInternalComplaint(resolved, "PUSAT")).toBe(true);
    expect(isActionNeededInternalComplaint(resolved, "UPPPD-GAMBIR")).toBe(true);
  });

  it("opens the action queue only when the badge is non-zero", () => {
    expect(INTERNAL_ACTION_HREF).toBe("/internal/complaints?needsAction=1");
    expect(INTERNAL_LIST_HREF).toBe("/internal/complaints");
    expect(internalComplaintsNavHref(3)).toBe(INTERNAL_ACTION_HREF);
    expect(internalComplaintsNavHref(0)).toBe(INTERNAL_LIST_HREF);
  });
});
