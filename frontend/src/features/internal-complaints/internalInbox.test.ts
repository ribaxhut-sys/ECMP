import { describe, expect, it } from "vitest";
import {
  INTERNAL_INBOX_HREF,
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

  it("points the sidebar door at the receive queue", () => {
    expect(INTERNAL_INBOX_HREF).toBe("/internal/complaints?needsReceive=1");
  });
});
