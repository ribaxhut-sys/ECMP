import { describe, expect, it } from "vitest";
import {
  CM_BATCH1_HQ_NOTE_MIN,
  canCmBatch1HqReview,
  cmBatch1BlobEventCodes,
  intakeHistoryIsCloseEvent,
  intakeHistoryShowsNote,
  intakeHistoryShowsPriority,
  isCmBatch1HqAcceptScheduleReady,
  isCmBatch1HqNoteReady,
  isCmBatch1HqRescheduleReady,
  isCmBatch1PusatUnitCode,
  isHqScheduleDestinationUnitCode,
  resolveCmBatch1BranchEscalationCtas,
  resolveCmBatch1HqActionVisibility,
  showBranchHandleComplaintCta,
} from "./cmBatch1HqActions";

describe("isCmBatch1PusatUnitCode", () => {
  it("accepts backend DEFAULT_PUSAT_UNIT_CODES aliases", () => {
    expect(isCmBatch1PusatUnitCode("PUSAT")).toBe(true);
    expect(isCmBatch1PusatUnitCode("ho")).toBe(true);
    expect(isCmBatch1PusatUnitCode("HEAD_OFFICE")).toBe(true);
    expect(isCmBatch1PusatUnitCode("HEAD-OFFICE")).toBe(true);
  });

  it("rejects branch and empty codes", () => {
    expect(isCmBatch1PusatUnitCode("UPPPD-A")).toBe(false);
    expect(isCmBatch1PusatUnitCode("")).toBe(false);
    expect(isCmBatch1PusatUnitCode(null)).toBe(false);
  });
});

describe("canCmBatch1HqReview", () => {
  it("allows HO_SCHEDULER with escalations:review", () => {
    expect(
      canCmBatch1HqReview({
        roles: ["HO_SCHEDULER"],
        hasPermission: (p) => p === "escalations:review",
        unitCode: null,
      }),
    ).toBe(true);
  });

  it("allows Agent on PUSAT with complaints:read", () => {
    expect(
      canCmBatch1HqReview({
        roles: ["AGENT"],
        hasPermission: (p) => p === "complaints:read",
        unitCode: "PUSAT",
      }),
    ).toBe(true);
  });

  it("denies Agent on branch unit", () => {
    expect(
      canCmBatch1HqReview({
        roles: ["AGENT"],
        hasPermission: (p) => p === "complaints:read",
        unitCode: "UPPPD-A",
      }),
    ).toBe(false);
  });

  it("denies escalations:review without HO/Admin role (align backend)", () => {
    expect(
      canCmBatch1HqReview({
        roles: ["SUPERVISOR"],
        hasPermission: (p) => p === "escalations:review",
        unitCode: "UPPPD-A",
      }),
    ).toBe(false);
  });
});

describe("resolveCmBatch1HqActionVisibility", () => {
  const approved = {
    status: "REGISTERED",
    intakeDisposition: "ESCALATE_APPROVED",
    hqAcceptedAt: null,
    hqArrivalDate: null,
    caseCreated: false,
  };

  it("shows accept/return for HQ reviewer before accept", () => {
    const v = resolveCmBatch1HqActionVisibility(approved, true);
    expect(v.showHqAcceptAndSchedule).toBe(true);
    expect(v.showHqReturn).toBe(true);
    expect(v.showHqReschedule).toBe(false);
    expect(v.showHqComplete).toBe(false);
    expect(v.showBranchNotifyBanner).toBe(false);
  });

  it("shows accept/return for IN_PROGRESS approved escalation (bound Case)", () => {
    const v = resolveCmBatch1HqActionVisibility(
      {
        status: "IN_PROGRESS",
        intakeDisposition: "ESCALATE_APPROVED",
        hqAcceptedAt: null,
        hqArrivalDate: null,
        caseCreated: true,
      },
      true,
    );
    expect(v.approvedEscalation).toBe(true);
    expect(v.showHqAcceptAndSchedule).toBe(true);
    expect(v.showHqReturn).toBe(true);
  });

  it("hides HQ actions from branch actors", () => {
    const v = resolveCmBatch1HqActionVisibility(approved, false);
    expect(v.showHqAcceptAndSchedule).toBe(false);
    expect(v.showHqReturn).toBe(false);
    expect(v.showHqComplete).toBe(false);
  });

  it("shows reschedule after HQ_SCHEDULED + accepted", () => {
    const v = resolveCmBatch1HqActionVisibility(
      {
        status: "REGISTERED",
        intakeDisposition: "HQ_SCHEDULED",
        hqAcceptedAt: "2026-08-01T00:00:00Z",
        hqArrivalDate: "2026-08-10",
        caseCreated: false,
      },
      true,
    );
    expect(v.hqScheduled).toBe(true);
    expect(v.showHqAcceptAndSchedule).toBe(false);
    expect(v.showHqReschedule).toBe(true);
    expect(v.showHqComplete).toBe(true);
  });

  it("does not duplicate a branch notify banner after the visit slot is scheduled", () => {
    const v = resolveCmBatch1HqActionVisibility(
      {
        status: "REGISTERED",
        intakeDisposition: "HQ_SCHEDULED",
        hqAcceptedAt: "2026-08-01T00:00:00Z",
        hqArrivalDate: "2026-08-10",
        caseCreated: false,
      },
      false,
    );
    expect(v.showBranchNotifyBanner).toBe(false);
    expect(v.showHqReschedule).toBe(false);
    expect(v.showHqComplete).toBe(false);
  });
});

describe("HQ note / schedule readiness", () => {
  it("enforces note min length", () => {
    expect(isCmBatch1HqNoteReady("short")).toBe(false);
    expect(isCmBatch1HqNoteReady("x".repeat(CM_BATCH1_HQ_NOTE_MIN))).toBe(true);
  });

  it("requires date+time+unit+note for accept-and-schedule", () => {
    expect(
      isCmBatch1HqAcceptScheduleReady({
        arrivalDate: "2026-08-10",
        arrivalTime: "09:00",
        arrivalNote: "short",
        destinationUnitId: "PUSAT-CRO",
      }),
    ).toBe(false);
    // Pusat is not one door — no destination unit, no schedule.
    expect(
      isCmBatch1HqAcceptScheduleReady({
        arrivalDate: "2026-08-10",
        arrivalTime: "09:00",
        arrivalNote: "Jadwal kedatangan wajib pajak ke Pusat.",
        destinationUnitId: "  ",
      }),
    ).toBe(false);
    expect(
      isCmBatch1HqAcceptScheduleReady({
        arrivalDate: "2026-08-10",
        arrivalTime: "09:00",
        arrivalNote: "Jadwal kedatangan wajib pajak ke Pusat.",
        destinationUnitId: "PUSAT-CRO",
      }),
    ).toBe(true);
  });

  it("treats Pusat sub-units as Pusat", () => {
    expect(isCmBatch1PusatUnitCode("PUSAT-CRO")).toBe(true);
    expect(isCmBatch1PusatUnitCode("pusat-suban-1")).toBe(true);
    expect(isCmBatch1PusatUnitCode("PUSATAKA")).toBe(false);
    expect(isCmBatch1PusatUnitCode("UPPPD-GAMBIR")).toBe(false);
  });

  it("limits HQ schedule destinations to CRO", () => {
    expect(isHqScheduleDestinationUnitCode("PUSAT-CRO")).toBe(true);
    expect(isHqScheduleDestinationUnitCode("ho-cro")).toBe(true);
    expect(isHqScheduleDestinationUnitCode("PUSAT")).toBe(false);
    expect(isHqScheduleDestinationUnitCode("PUSAT-SUBAN-1")).toBe(false);
    expect(isHqScheduleDestinationUnitCode("PUSAT-SEKRETARIAT")).toBe(false);
  });

  it("allows empty note on reschedule but not short note", () => {
    expect(
      isCmBatch1HqRescheduleReady({
        arrivalDate: "2026-08-10",
        arrivalTime: "09:00",
        arrivalNote: "",
      }),
    ).toBe(true);
    expect(
      isCmBatch1HqRescheduleReady({
        arrivalDate: "2026-08-10",
        arrivalTime: "09:00",
        arrivalNote: "short",
      }),
    ).toBe(false);
  });
});

describe("cmBatch1BlobEventCodes", () => {
  const base = {
    intakeDisposition: null as string | null,
    escalationReason: null as string | null,
    branchResolution: null as string | null,
    supervisorNote: null as string | null,
    rejectionNote: null as string | null,
    cancellationNote: null as string | null,
    hqReturnNote: null as string | null,
    hqAcceptedAt: null as string | null,
    hqArrivalDate: null as string | null,
    hqArrivalTime: null as string | null,
    intakeClosed: false,
  };

  it("always starts at REGISTERED", () => {
    expect(cmBatch1BlobEventCodes(base)).toEqual(["REGISTERED"]);
  });

  it("reconstructs the branch escalation chain", () => {
    expect(
      cmBatch1BlobEventCodes({
        ...base,
        intakeDisposition: "ESCALATE_APPROVED",
        escalationReason: "Butuh berkas pusat",
        supervisorNote: "Disetujui untuk Pusat",
      }),
    ).toEqual(["REGISTERED", "ESCALATION_REQUESTED", "ESCALATION_APPROVED"]);
  });

  it("emits HQ_RETURNED from disposition RETURNED_TO_BRANCH (API-519)", () => {
    const codes = cmBatch1BlobEventCodes({
      ...base,
      intakeDisposition: "RETURNED_TO_BRANCH",
      escalationReason: "Butuh berkas pusat",
      supervisorNote: "Disetujui untuk Pusat",
    });
    expect(codes).toContain("HQ_RETURNED");
    expect(codes.indexOf("HQ_RETURNED")).toBeGreaterThan(
      codes.indexOf("ESCALATION_APPROVED"),
    );
  });

  it("emits HQ_RETURNED from the return note even after re-escalation (API-518)", () => {
    // Blob keeps Pengembalian Pusat; disposition already moved back to pending.
    const codes = cmBatch1BlobEventCodes({
      ...base,
      intakeDisposition: "ESCALATE_PENDING_APPROVAL",
      escalationReason: "Berkas sudah dilengkapi",
      hqReturnNote: "[MISSING_ATTACHMENT] Lampirkan bukti bayar.",
    });
    expect(codes).toContain("HQ_RETURNED");
  });

  it("emits HQ accept and arrival codes when HQ accepted and scheduled", () => {
    expect(
      cmBatch1BlobEventCodes({
        ...base,
        intakeDisposition: "HQ_SCHEDULED",
        escalationReason: "Butuh berkas pusat",
        hqAcceptedAt: "2026-08-01T02:00:00Z",
        hqArrivalDate: "2026-08-10",
        hqArrivalTime: "09:00",
      }),
    ).toEqual([
      "REGISTERED",
      "ESCALATION_REQUESTED",
      "HQ_ACCEPTED",
      "HQ_ARRIVAL_SCHEDULED",
    ]);
  });

  it("does not emit HQ_ARRIVAL_SCHEDULED when only the date is known", () => {
    expect(
      cmBatch1BlobEventCodes({
        ...base,
        hqAcceptedAt: "2026-08-01T02:00:00Z",
        hqArrivalDate: "2026-08-10",
      }),
    ).toEqual(["REGISTERED", "HQ_ACCEPTED"]);
  });

  it("emits BRANCH_CLOSED from the intake=closed deep-link", () => {
    expect(
      cmBatch1BlobEventCodes({ ...base, intakeClosed: true }),
    ).toEqual(["REGISTERED", "BRANCH_CLOSED"]);
  });

  it("emits HQ_COMPLETED when disposition is HQ_CLOSED", () => {
    expect(
      cmBatch1BlobEventCodes({
        ...base,
        intakeDisposition: "HQ_CLOSED",
        hqAcceptedAt: "2026-08-01T02:00:00Z",
        hqArrivalDate: "2026-08-10",
        hqArrivalTime: "09:00",
      }),
    ).toEqual([
      "REGISTERED",
      "HQ_ACCEPTED",
      "HQ_ARRIVAL_SCHEDULED",
      "HQ_COMPLETED",
    ]);
  });
});

describe("intakeHistoryShowsPriority", () => {
  it("hides the tag on branch-close-at-intake history", () => {
    expect(intakeHistoryShowsPriority("BRANCH_CLOSED", "BRANCH_CLOSED")).toBe(
      false,
    );
    expect(intakeHistoryShowsPriority("REGISTERED", "BRANCH_CLOSED")).toBe(
      false,
    );
  });

  it("keeps the tag when the operator chose priority on register", () => {
    expect(intakeHistoryShowsPriority("REGISTERED", null)).toBe(true);
    expect(intakeHistoryShowsPriority("ESCALATION_APPROVED", "ESCALATE_APPROVED")).toBe(
      true,
    );
  });
});

describe("intakeHistoryShowsNote", () => {
  it("hides catatan on Ditutup di cabang", () => {
    expect(intakeHistoryShowsNote("BRANCH_CLOSED")).toBe(false);
    expect(intakeHistoryShowsNote("REGISTERED")).toBe(true);
  });

  it("hides Case milestone notes — those belong on the Case page", () => {
    expect(intakeHistoryShowsNote("CASE_CREATED")).toBe(false);
    expect(intakeHistoryShowsNote("CASE_CLOSED")).toBe(false);
    expect(intakeHistoryShowsNote("CASE_RESOLVED")).toBe(false);
    expect(intakeHistoryShowsNote("CASE_CANCELLED")).toBe(false);
    expect(intakeHistoryShowsNote("ESCALATION_APPROVED")).toBe(true);
  });
});

describe("intakeHistoryIsCloseEvent", () => {
  it("marks branch close and case close as closer rows", () => {
    expect(intakeHistoryIsCloseEvent("BRANCH_CLOSED")).toBe(true);
    expect(intakeHistoryIsCloseEvent("CASE_CLOSED")).toBe(true);
    expect(intakeHistoryIsCloseEvent("HQ_COMPLETED")).toBe(true);
    expect(intakeHistoryIsCloseEvent("REGISTERED")).toBe(false);
  });
});

describe("resolveCmBatch1BranchEscalationCtas", () => {
  const branch = {
    canDecideEscalation: true,
    canRequestEscalation: true,
    intakeClosed: false,
    isHqReviewer: false,
    isPusatUnitMember: false,
    intakeEscalateQuery: false,
  };

  it("shows Batalkan Eskalasi on the parent only when no Case exists yet", () => {
    const v = resolveCmBatch1BranchEscalationCtas({
      ...branch,
      status: "IN_PROGRESS",
      intakeDisposition: "ESCALATE_APPROVED",
      hqAcceptedAt: null,
    });
    expect(v.showCancelEscalation).toBe(true);
    expect(v.showManageCases).toBe(false);
    expect(v.showSupervisorActions).toBe(false);
    expect(v.showReRequestEscalation).toBe(false);
  });

  it("hides parent Batalkan Eskalasi once a bound Case exists", () => {
    const v = resolveCmBatch1BranchEscalationCtas({
      ...branch,
      status: "IN_PROGRESS",
      intakeDisposition: "ESCALATE_APPROVED",
      hqAcceptedAt: null,
      hasBoundCase: true,
    });
    expect(v.showCancelEscalation).toBe(false);
  });

  it("hides Batalkan Eskalasi after HQ accepted", () => {
    const v = resolveCmBatch1BranchEscalationCtas({
      ...branch,
      status: "IN_PROGRESS",
      intakeDisposition: "HQ_SCHEDULED",
      hqAcceptedAt: "2026-08-17T10:00:00Z",
    });
    expect(v.showCancelEscalation).toBe(false);
    expect(v.showManageCases).toBe(false);
  });

  it("restores Tangani after cancel, keeping the bound Case", () => {
    const v = resolveCmBatch1BranchEscalationCtas({
      ...branch,
      status: "IN_PROGRESS",
      intakeDisposition: "ESCALATE_CANCELLED",
      hqAcceptedAt: null,
    });
    expect(v.showCancelEscalation).toBe(false);
    expect(v.showManageCases).toBe(true);
    expect(v.showReRequestEscalation).toBe(false);
  });
});

describe("showBranchHandleComplaintCta", () => {
  const ready = {
    showManageCases: true,
    loading: false,
    handlingClaimedBy: null as string | null,
    openCount: 0,
    pusatCount: 0,
  };

  it("shows Tangani when the complaint has no Case yet", () => {
    expect(showBranchHandleComplaintCta(ready)).toBe(true);
  });

  it("hides Tangani when the only Case is already at Pusat", () => {
    expect(
      showBranchHandleComplaintCta({
        ...ready,
        openCount: 0,
        pusatCount: 1,
      }),
    ).toBe(false);
  });

  it("keeps Tangani when a sibling branch Case is still open", () => {
    expect(
      showBranchHandleComplaintCta({
        ...ready,
        openCount: 1,
        pusatCount: 1,
      }),
    ).toBe(true);
  });
});
