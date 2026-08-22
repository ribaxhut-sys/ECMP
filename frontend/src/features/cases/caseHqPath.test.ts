import { describe, expect, it } from "vitest";
import {
  hideCaseBranchWorkActions,
  resolveCaseHqPath,
  showCaseCancelEscalation,
} from "./caseHqPath";

describe("resolveCaseHqPath", () => {
  it("is off the HQ path for branch-closed or unset disposition", () => {
    expect(resolveCaseHqPath({ intakeDisposition: null }).onHqPath).toBe(false);
    expect(
      resolveCaseHqPath({ intakeDisposition: "BRANCH_CLOSED" }).onHqPath,
    ).toBe(false);
  });

  it("uses taxpayer-arrival copy once HQ_SCHEDULED", () => {
    const path = resolveCaseHqPath({
      intakeDisposition: "HQ_SCHEDULED",
      hqAcceptedAt: "2026-08-17T10:00:00Z",
    });
    expect(path.onHqPath).toBe(true);
    expect(path.phase).toBe("scheduled");
    expect(path.copy?.pageTitle).toBe("hqPathScheduledPageTitle");
  });

  it("keeps approved-escalation copy before HQ accept", () => {
    const path = resolveCaseHqPath({
      intakeDisposition: "ESCALATE_APPROVED",
    });
    expect(path.onHqPath).toBe(true);
    expect(path.phase).toBe("awaiting_accept");
    expect(path.copy?.pageTitle).toBe("escalationApproved");
  });
});

describe("hideCaseBranchWorkActions", () => {
  it("hides resolve on open Case while parent is HQ_SCHEDULED", () => {
    expect(hideCaseBranchWorkActions(true, "IN_PROGRESS")).toBe(true);
    expect(hideCaseBranchWorkActions(true, "ASSIGNED")).toBe(true);
    expect(hideCaseBranchWorkActions(true, "CREATED")).toBe(true);
  });

  it("does not hide after Case is resolved or closed", () => {
    expect(hideCaseBranchWorkActions(true, "RESOLVED")).toBe(false);
    expect(hideCaseBranchWorkActions(true, "CLOSED")).toBe(false);
    expect(hideCaseBranchWorkActions(true, "CANCELLED")).toBe(false);
  });

  it("does not hide when parent is not on the HQ path", () => {
    expect(hideCaseBranchWorkActions(false, "IN_PROGRESS")).toBe(false);
  });

  it("hides branch work when this Case is with Pusat (DEC-029)", () => {
    expect(hideCaseBranchWorkActions(false, "IN_PROGRESS", true)).toBe(true);
    expect(hideCaseBranchWorkActions(false, "RESOLVED", true)).toBe(false);
  });
});

describe("showCaseCancelEscalation", () => {
  const approved = {
    canDecideEscalation: true,
    complaintStatus: "IN_PROGRESS",
    intakeDisposition: "ESCALATE_APPROVED",
    hqAcceptedAt: null,
  };

  it("shows while parent is approved and HQ has not accepted", () => {
    expect(showCaseCancelEscalation(approved)).toBe(true);
  });

  it("hides without complaints:escalate", () => {
    expect(
      showCaseCancelEscalation({ ...approved, canDecideEscalation: false }),
    ).toBe(false);
  });

  it("hides after HQ accepted", () => {
    expect(
      showCaseCancelEscalation({
        ...approved,
        hqAcceptedAt: "2026-08-22T08:00:00Z",
      }),
    ).toBe(false);
  });

  it("hides when parent is already cancelled or scheduled", () => {
    expect(
      showCaseCancelEscalation({
        ...approved,
        intakeDisposition: "ESCALATE_CANCELLED",
      }),
    ).toBe(false);
    expect(
      showCaseCancelEscalation({
        ...approved,
        intakeDisposition: "HQ_SCHEDULED",
        hqAcceptedAt: "2026-08-22T08:00:00Z",
      }),
    ).toBe(false);
  });
});
