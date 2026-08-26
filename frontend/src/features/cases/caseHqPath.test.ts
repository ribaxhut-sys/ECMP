import { describe, expect, it } from "vitest";
import {
  hideCaseBranchWorkActions,
  isCaseCurrentlyReturnedFromPusat,
  resolveCaseHqPath,
  showCaseCancelEscalation,
  showCaseLevelCancelEscalation,
  showCaseReturnEscalation,
  actorMayHandleEscalatedCase,
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

  it("lets the branch work again after Pusat returned the Case", () => {
    expect(
      hideCaseBranchWorkActions(true, "IN_PROGRESS", false, false, true),
    ).toBe(false);
  });

  it("lets the branch work when this Case was returned even if parent HQ path is stale", () => {
    expect(
      hideCaseBranchWorkActions(true, "IN_PROGRESS", false, false, false, true),
    ).toBe(false);
  });

  it("lets a Pusat actor work an escalated Case", () => {
    expect(hideCaseBranchWorkActions(false, "IN_PROGRESS", true, true)).toBe(
      false,
    );
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

  it("hides when parent was returned to the branch", () => {
    expect(
      showCaseCancelEscalation({
        ...approved,
        intakeDisposition: "RETURNED_TO_BRANCH",
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

describe("showCaseLevelCancelEscalation", () => {
  const open = {
    escalatedToPusat: true,
    handlingClaimedBy: null as string | null,
    canCancel: true,
    actorIsPusat: false,
    caseStatus: "IN_PROGRESS",
  };

  it("shows for the originating branch before Pusat claims", () => {
    expect(showCaseLevelCancelEscalation(open)).toBe(true);
  });

  it("hides after Pusat claims handling", () => {
    expect(
      showCaseLevelCancelEscalation({
        ...open,
        handlingClaimedBy: "pusat-1",
      }),
    ).toBe(false);
  });

  it("hides for a Pusat actor", () => {
    expect(showCaseLevelCancelEscalation({ ...open, actorIsPusat: true })).toBe(
      false,
    );
  });

  it("hides after HQ accepted even if handling is unclaimed", () => {
    expect(
      showCaseLevelCancelEscalation({
        ...open,
        hqAcceptedAt: "2026-08-17T10:00:00Z",
      }),
    ).toBe(false);
  });

  it("hides once parent is HQ_SCHEDULED", () => {
    expect(
      showCaseLevelCancelEscalation({
        ...open,
        intakeDisposition: "HQ_SCHEDULED",
      }),
    ).toBe(false);
  });

  it("hides after Pusat returned the Case", () => {
    expect(
      showCaseLevelCancelEscalation({
        ...open,
        escalatedToPusat: false,
        intakeDisposition: "RETURNED_TO_BRANCH",
      }),
    ).toBe(false);
  });
});

describe("showCaseReturnEscalation", () => {
  const open = {
    escalatedToPusat: true,
    actorIsPusat: true,
    canUpdate: true,
    caseStatus: "IN_PROGRESS",
  };

  it("shows for Pusat while the Case is with HQ", () => {
    expect(showCaseReturnEscalation(open)).toBe(true);
  });

  it("hides for the branch", () => {
    expect(showCaseReturnEscalation({ ...open, actorIsPusat: false })).toBe(
      false,
    );
  });

  it("hides after the Case is resolved", () => {
    expect(showCaseReturnEscalation({ ...open, caseStatus: "RESOLVED" })).toBe(
      false,
    );
  });
});

describe("actorMayHandleEscalatedCase", () => {
  it("treats a Pusat unit officer as able to work the Case", () => {
    expect(
      actorMayHandleEscalatedCase({
        roles: ["AGENT"],
        hasPermission: () => true,
        unitCode: "PUSAT",
      }),
    ).toBe(true);
  });

  it("does not treat a branch officer as Pusat", () => {
    expect(
      actorMayHandleEscalatedCase({
        roles: ["AGENT"],
        hasPermission: () => true,
        unitCode: "JKT-SELATAN",
      }),
    ).toBe(false);
  });
});

describe("isCaseCurrentlyReturnedFromPusat", () => {
  it("follows the last Case-level return even when the parent is still approved", () => {
    expect(
      isCaseCurrentlyReturnedFromPusat({
        escalatedToPusat: false,
        intakeDisposition: "ESCALATE_APPROVED",
        historyEventCodes: [
          "CASE_CREATED",
          "CASE_ESCALATED_TO_PUSAT",
          "CASE_ESCALATION_RETURNED",
        ],
      }),
    ).toBe(true);
  });

  it("is false after the Case is sent to Pusat again", () => {
    expect(
      isCaseCurrentlyReturnedFromPusat({
        escalatedToPusat: true,
        intakeDisposition: "RETURNED_TO_BRANCH",
        historyEventCodes: [
          "CASE_ESCALATION_RETURNED",
          "CASE_ESCALATED_TO_PUSAT",
        ],
      }),
    ).toBe(false);
  });

  it("is false when the branch cancelled the escalation", () => {
    expect(
      isCaseCurrentlyReturnedFromPusat({
        escalatedToPusat: false,
        intakeDisposition: "ESCALATE_APPROVED",
        historyEventCodes: [
          "CASE_ESCALATED_TO_PUSAT",
          "CASE_ESCALATION_TO_PUSAT_CANCELLED",
        ],
      }),
    ).toBe(false);
  });

  it("falls back to parent RETURNED_TO_BRANCH when history has no cycle event", () => {
    expect(
      isCaseCurrentlyReturnedFromPusat({
        escalatedToPusat: false,
        intakeDisposition: "RETURNED_TO_BRANCH",
        historyEventCodes: ["CASE_CREATED"],
      }),
    ).toBe(true);
  });
});
