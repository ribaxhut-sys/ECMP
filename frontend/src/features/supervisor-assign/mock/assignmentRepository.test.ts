import { describe, expect, it, beforeEach } from "vitest";
import {
  assignComplaintToUnit,
  getComplaintById,
  holdIntakeDraft,
  listActiveCasesByCustomerRef,
  listHeldDrafts,
  listOfficerAssigned,
  listUnassigned,
  recordProgress,
  registerIntake,
  resetAssignmentRepository,
  saveFollowUp,
  searchCustomers,
  startHandling,
  submitForReview,
  addMinimalEvidence,
  listPendingReview,
  listNewEscalations,
  listSlaAtRisk,
  approveAndClose,
  rejectReview,
  saveCorrection,
  hasRejectContinuity,
  hasRequiredRejectHistory,
  latestRejectHistory,
  requestReopen,
  approveReopen,
  rejectReopen,
  continueReopened,
  listClosedCasesByCustomerRef,
  listPendingReopen,
  hasReopenContinuity,
  hasRequiredClosureHistory,
  hasRequiredEscalationHistory,
  hasEscalationContextRequest,
  requestEscalationContext,
  submitEscalationContext,
  handleEscalation,
  forwardEscalation,
  MOCK_OFFICER_ID,
} from "./assignmentRepository";

describe("assignmentRepository (B1–B6 + R2-B1/R2-B2/R2-B3 mock)", () => {
  beforeEach(() => {
    resetAssignmentRepository();
  });

  it("lists only REGISTERED complaints as unassigned", () => {
    const items = listUnassigned();
    expect(items.length).toBeGreaterThan(0);
    expect(items.every((c) => c.status === "REGISTERED")).toBe(true);
  });

  it("assigns unit, binds officer, and removes from unassigned queue", () => {
    const first = listUnassigned()[0]!;
    const before = listUnassigned().length;

    const result = assignComplaintToUnit(first.id, "unit-cs-north");
    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(result.complaint.status).toBe("ASSIGNED");
    expect(result.complaint.assignedUnitId).toBe("unit-cs-north");
    expect(result.complaint.assigneeOfficerId).toBe(MOCK_OFFICER_ID);
    expect(result.complaint.slaDueAt).toBeTruthy();

    const after = listUnassigned();
    expect(after.length).toBe(before - 1);
    expect(listOfficerAssigned().some((c) => c.id === first.id)).toBe(true);
  });

  it("lists officer assigned sorted by SLA due", () => {
    const items = listOfficerAssigned();
    expect(items.length).toBeGreaterThan(0);
    expect(
      items.every(
        (c) =>
          c.assigneeOfficerId === MOCK_OFFICER_ID &&
          (c.status === "ASSIGNED" ||
            c.status === "IN_PROGRESS" ||
            c.status === "REOPENED"),
      ),
    ).toBe(true);
    for (let i = 1; i < items.length; i += 1) {
      const prev = items[i - 1]!.slaDueAt
        ? new Date(items[i - 1]!.slaDueAt!).getTime()
        : Number.MAX_SAFE_INTEGER;
      const curr = items[i]!.slaDueAt
        ? new Date(items[i]!.slaDueAt!).getTime()
        : Number.MAX_SAFE_INTEGER;
      expect(prev).toBeLessThanOrEqual(curr);
    }
  });

  it("starts handling ASSIGNED → IN_PROGRESS", () => {
    const assigned = listOfficerAssigned().find((c) => c.status === "ASSIGNED")!;
    const result = startHandling(assigned.id);
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.complaint.status).toBe("IN_PROGRESS");
    expect(getComplaintById(assigned.id)?.status).toBe("IN_PROGRESS");
  });

  it("records progress only while IN_PROGRESS", () => {
    const assigned = listOfficerAssigned().find((c) => c.status === "ASSIGNED")!;
    expect(recordProgress(assigned.id, "too early")).toEqual({
      ok: false,
      reason: "NOT_IN_PROGRESS",
    });

    startHandling(assigned.id);
    const saved = recordProgress(assigned.id, "Called customer");
    expect(saved.ok).toBe(true);
    if (!saved.ok) return;
    expect(saved.complaint.progressNotes.at(-1)?.text).toBe("Called customer");
  });

  it("rejects empty progress notes", () => {
    const inProgress = listOfficerAssigned().find(
      (c) => c.status === "IN_PROGRESS",
    )!;
    expect(recordProgress(inProgress.id, "   ")).toEqual({
      ok: false,
      reason: "EMPTY_NOTE",
    });
  });

  it("searches customer reference cache without writing master", () => {
    const hits = searchCustomers("Hana");
    expect(hits).toHaveLength(1);
    expect(hits[0]?.ref).toBe("CUST-2099");
  });

  it("registers new intake only when complete and no active case", () => {
    const before = listUnassigned().length;
    const blocked = registerIntake({
      customerRef: "CUST-1001",
      customerName: "Ayu Pratama",
      subject: "Should block",
      description: "Active case exists",
      category: "Billing",
      channel: "Phone",
      priority: "MEDIUM",
    });
    expect(blocked).toEqual({ ok: false, reason: "ACTIVE_CASE_EXISTS" });

    const result = registerIntake({
      customerRef: "CUST-3001",
      customerName: "Joko Raharjo",
      subject: "New roaming issue",
      description: "Cannot activate roaming pack",
      category: "Service",
      channel: "Phone",
      priority: "HIGH",
    });
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.complaint.status).toBe("REGISTERED");
    expect(result.complaint.customerRef).toBe("CUST-3001");
    expect(listUnassigned().length).toBe(before + 1);
    expect(listActiveCasesByCustomerRef("CUST-3001")).toHaveLength(1);
  });

  it("holds incomplete draft without creating a complaint primary", () => {
    const beforeComplaints = listUnassigned().length;
    const result = holdIntakeDraft({
      customerRef: "CUST-2099",
      customerName: "Hana Wijaya",
      subject: "Partial subject",
      description: "",
      category: "",
      channel: "Phone",
      priority: "",
    });
    expect(result.ok).toBe(true);
    expect(listUnassigned().length).toBe(beforeComplaints);
    expect(listHeldDrafts()).toHaveLength(1);
  });

  it("saves follow-up without creating a duplicate primary record", () => {
    const active = listActiveCasesByCustomerRef("CUST-1005")[0]!;
    const beforeCount = listActiveCasesByCustomerRef("CUST-1005").length;
    const saved = saveFollowUp(active.id, "Customer asked for ETA");
    expect(saved.ok).toBe(true);
    if (!saved.ok) return;
    expect(saved.complaint.status).toBe(active.status);
    expect(saved.complaint.followUpNotes.at(-1)?.text).toBe(
      "Customer asked for ETA",
    );
    expect(listActiveCasesByCustomerRef("CUST-1005")).toHaveLength(beforeCount);
  });

  it("submits IN_PROGRESS → PENDING_REVIEW and leaves officer queue", () => {
    const inProgress = listOfficerAssigned().find(
      (c) =>
        c.status === "IN_PROGRESS" &&
        !c.escalationNew &&
        c.evidenceItems.some((e) => e.status === "ATTACHED"),
    )!;
    const beforeQueue = listOfficerAssigned().length;

    expect(
      submitForReview(inProgress.id, "   "),
    ).toEqual({ ok: false, reason: "RESOLUTION_REQUIRED" });

    const submitted = submitForReview(
      inProgress.id,
      "Root cause fixed; customer confirmed restored speed.",
    );
    expect(submitted.ok).toBe(true);
    if (!submitted.ok) return;
    expect(submitted.complaint.status).toBe("PENDING_REVIEW");
    expect(submitted.complaint.resolutionSummary).toContain("Root cause");
    expect(getComplaintById(inProgress.id)?.status).toBe("PENDING_REVIEW");
    expect(listOfficerAssigned().length).toBe(beforeQueue - 1);
    expect(
      listOfficerAssigned().some((c) => c.id === inProgress.id),
    ).toBe(false);
  });

  it("blocks submit when evidence list has no ATTACHED item", () => {
    const assigned = listOfficerAssigned().find((c) => c.status === "ASSIGNED")!;
    startHandling(assigned.id);
    expect(submitForReview(assigned.id, "Ready to submit")).toEqual({
      ok: false,
      reason: "EVIDENCE_REQUIRED",
    });

    const added = addMinimalEvidence(assigned.id, "screenshot-fix.png");
    expect(added.ok).toBe(true);
    const submitted = submitForReview(assigned.id, "Ready to submit");
    expect(submitted.ok).toBe(true);
    if (!submitted.ok) return;
    expect(submitted.complaint.status).toBe("PENDING_REVIEW");
  });

  it("lists pending review and approves PENDING_REVIEW → CLOSED", () => {
    const pending = listPendingReview();
    expect(pending.length).toBeGreaterThan(0);
    expect(pending.every((c) => c.status === "PENDING_REVIEW")).toBe(true);

    const target = pending[0]!;
    const before = listPendingReview().length;
    const approved = approveAndClose(target.id);
    expect(approved.ok).toBe(true);
    if (!approved.ok) return;
    expect(approved.complaint.status).toBe("CLOSED");
    expect(getComplaintById(target.id)?.status).toBe("CLOSED");
    expect(listPendingReview().length).toBe(before - 1);
    expect(
      listOfficerAssigned().some((c) => c.id === target.id),
    ).toBe(false);
  });

  it("rejects PENDING_REVIEW → IN_PROGRESS (status-only) with reason", () => {
    const pending = listPendingReview()[0]!;
    expect(rejectReview(pending.id, "   ")).toEqual({
      ok: false,
      reason: "REASON_REQUIRED",
    });

    const rejected = rejectReview(pending.id, "Need clearer evidence of credit");
    expect(rejected.ok).toBe(true);
    if (!rejected.ok) return;
    expect(rejected.complaint.status).toBe("IN_PROGRESS");
    expect(rejected.complaint.rejectReason).toBe(
      "Need clearer evidence of credit",
    );
    expect(
      rejected.complaint.decisionHistory.some((e) => e.type === "REJECT"),
    ).toBe(true);
    expect(listPendingReview().some((c) => c.id === pending.id)).toBe(false);
    expect(
      listOfficerAssigned().some(
        (c) => c.id === pending.id && c.status === "IN_PROGRESS",
      ),
    ).toBe(true);
  });

  it("R2-B1: seeded rejected continuity exposes history and supports resubmit", () => {
    const rejected = getComplaintById("cmp-r2b1-001");
    expect(rejected).toBeDefined();
    if (!rejected) return;
    expect(hasRejectContinuity(rejected)).toBe(true);
    expect(hasRequiredRejectHistory(rejected)).toBe(true);
    const latest = latestRejectHistory(rejected);
    expect(latest?.reason).toContain("live invoice");

    const saved = saveCorrection(
      rejected.id,
      "Updated reversal with live invoice screenshot note.",
    );
    expect(saved.ok).toBe(true);
    if (!saved.ok) return;
    expect(saved.complaint.status).toBe("IN_PROGRESS");
    expect(saved.complaint.resolutionSummary).toContain("live invoice");

    const resubmitted = submitForReview(
      rejected.id,
      "Updated reversal with live invoice screenshot note.",
    );
    expect(resubmitted.ok).toBe(true);
    if (!resubmitted.ok) return;
    expect(resubmitted.complaint.status).toBe("PENDING_REVIEW");
    expect(resubmitted.complaint.rejectReason).toBeNull();
    expect(
      resubmitted.complaint.decisionHistory.filter((e) => e.type === "REJECT")
        .length,
    ).toBeGreaterThan(0);
    expect(
      resubmitted.complaint.decisionHistory.some((e) => e.type === "SUBMIT"),
    ).toBe(true);
  });

  it("R2-B2: reopen chain route → approve → continue", () => {
    const closed = getComplaintById("cmp-r2b2-closed-001");
    expect(closed?.status).toBe("CLOSED");
    expect(listClosedCasesByCustomerRef("CUST-3001").length).toBeGreaterThan(0);
    expect(listActiveCasesByCustomerRef("CUST-3001")).toHaveLength(0);

    const routed = requestReopen(
      "cmp-r2b2-closed-001",
      "Customer reports residual billing after closure.",
    );
    expect(routed.ok).toBe(true);
    if (!routed.ok) return;
    expect(routed.complaint.reopenPending).toBe(true);
    expect(listPendingReopen().some((c) => c.id === "cmp-r2b2-closed-001")).toBe(
      true,
    );

    expect(hasRequiredClosureHistory(routed.complaint)).toBe(true);
    const approved = approveReopen("cmp-r2b2-closed-001");
    expect(approved.ok).toBe(true);
    if (!approved.ok) return;
    expect(approved.complaint.status).toBe("REOPENED");
    expect(hasReopenContinuity(approved.complaint)).toBe(true);
    expect(
      listOfficerAssigned().some((c) => c.id === "cmp-r2b2-closed-001"),
    ).toBe(true);

    const continued = continueReopened("cmp-r2b2-closed-001");
    expect(continued.ok).toBe(true);
    if (!continued.ok) return;
    expect(continued.complaint.status).toBe("IN_PROGRESS");
  });

  it("R2-B2: reject reopen keeps CLOSED and clears pending", () => {
    const pending = getComplaintById("cmp-r2b2-pending-001");
    expect(pending?.reopenPending).toBe(true);
    const rejected = rejectReopen(
      "cmp-r2b2-pending-001",
      "Outside reopen window for this mock rule.",
    );
    expect(rejected.ok).toBe(true);
    if (!rejected.ok) return;
    expect(rejected.complaint.status).toBe("CLOSED");
    expect(rejected.complaint.reopenPending).toBe(false);
    expect(
      listPendingReopen().some((c) => c.id === "cmp-r2b2-pending-001"),
    ).toBe(false);
  });

  it("lists new escalations separately from SLA and unassigned", () => {
    const escalations = listNewEscalations();
    expect(escalations.length).toBeGreaterThan(0);
    expect(escalations.every((c) => c.escalationNew)).toBe(true);

    const unassignedIds = new Set(listUnassigned().map((c) => c.id));
    const pendingIds = new Set(listPendingReview().map((c) => c.id));
    for (const item of escalations) {
      expect(unassignedIds.has(item.id)).toBe(false);
      expect(pendingIds.has(item.id)).toBe(false);
    }
  });

  it("R2-B3: handle escalation clears queue flag and keeps progress", () => {
    const esc = getComplaintById("cmp-b6-esc-001");
    expect(esc?.escalationNew).toBe(true);
    expect(hasRequiredEscalationHistory(esc!)).toBe(true);
    const notesBefore = esc!.progressNotes.length;

    const handled = handleEscalation("cmp-b6-esc-001");
    expect(handled.ok).toBe(true);
    if (!handled.ok) return;
    expect(handled.complaint.escalationNew).toBe(false);
    expect(handled.complaint.status).toBe("IN_PROGRESS");
    expect(handled.complaint.progressNotes).toHaveLength(notesBefore);
    expect(
      listNewEscalations().some((c) => c.id === "cmp-b6-esc-001"),
    ).toBe(false);
    expect(
      handled.complaint.decisionHistory.some((e) => e.type === "ESCALATION_HANDLE"),
    ).toBe(true);
  });

  it("R2-B3: context handover then forward preserves progress", () => {
    const seed = getComplaintById("cmp-r2b3-ctx-001");
    expect(seed?.escalationContextRequested).toBe(true);
    expect(hasEscalationContextRequest(seed!)).toBe(true);
    const notesBefore = seed!.progressNotes.length;

    const submitted = submitEscalationContext(
      "cmp-r2b3-ctx-001",
      "Tried refund path A; customer refuses branch resolution.",
    );
    expect(submitted.ok).toBe(true);
    if (!submitted.ok) return;
    expect(submitted.complaint.escalationContextRequested).toBe(false);
    expect(submitted.complaint.escalationContextPackage).toContain("refund");
    expect(submitted.complaint.progressNotes).toHaveLength(notesBefore);
    expect(submitted.complaint.escalationNew).toBe(true);

    const forwarded = forwardEscalation(
      "cmp-r2b3-ctx-001",
      "Forward to Head Office per Branch→HO path.",
    );
    expect(forwarded.ok).toBe(true);
    if (!forwarded.ok) return;
    expect(forwarded.complaint.escalationNew).toBe(false);
    expect(forwarded.complaint.progressNotes).toHaveLength(notesBefore);
    expect(
      forwarded.complaint.decisionHistory.some(
        (e) => e.type === "ESCALATION_FORWARD",
      ),
    ).toBe(true);
  });

  it("R2-B3: request context from open escalation", () => {
    const requested = requestEscalationContext("cmp-b6-esc-001");
    expect(requested.ok).toBe(true);
    if (!requested.ok) return;
    expect(requested.complaint.escalationContextRequested).toBe(true);
    expect(hasEscalationContextRequest(requested.complaint)).toBe(true);
    expect(
      listNewEscalations().some((c) => c.id === "cmp-b6-esc-001"),
    ).toBe(true);
  });

  it("lists SLA at-risk excluding escalations, pending, and unassigned", () => {
    const nowMs = new Date("2026-08-05T04:00:00.000Z").getTime();
    const sla = listSlaAtRisk(nowMs);
    expect(sla.length).toBeGreaterThan(0);
    expect(sla.every((c) => !c.escalationNew)).toBe(true);
    expect(sla.every((c) => c.status !== "REGISTERED")).toBe(true);
    expect(sla.every((c) => c.status !== "PENDING_REVIEW")).toBe(true);
    expect(sla.every((c) => c.slaDueAt != null)).toBe(true);
  });
});
