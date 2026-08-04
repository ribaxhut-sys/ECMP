import { describe, expect, it } from "vitest";
import {
  deriveContextBadges,
  deriveNextActionKey,
  deriveOperationalContext,
  deriveRelevantDueAt,
} from "./deriveOperationalContext";

describe("deriveContextBadges", () => {
  it("derives allowed badges from existing fields only", () => {
    expect(
      deriveContextBadges({
        status: "PENDING",
        priority: "HIGH",
        overallSlaStatus: "BREACHED",
      }).map((b) => b.kind),
    ).toEqual([
      "high_priority",
      "critical_sla",
      "waiting_customer",
    ]);
  });

  it("adds escalated from status", () => {
    expect(
      deriveContextBadges({
        status: "ESCALATED",
        priority: "MEDIUM",
      }).map((b) => b.kind),
    ).toEqual(["escalated"]);
  });

  it("never invents repeat complaint", () => {
    expect(
      deriveContextBadges({
        status: "IN_PROGRESS",
        priority: "LOW",
      }).map((b) => b.kind),
    ).toEqual([]);
  });
});

describe("deriveNextActionKey", () => {
  it("maps foundation statuses", () => {
    expect(deriveNextActionKey("NEW")).toBe("assign");
    expect(deriveNextActionKey("ASSIGNED")).toBe("start_progress");
    expect(deriveNextActionKey("IN_PROGRESS")).toBe("mark_pending");
    expect(deriveNextActionKey("PENDING")).toBe("resume");
    expect(deriveNextActionKey("ESCALATED")).toBe("review_escalation");
    expect(deriveNextActionKey("RESOLVED")).toBe("close");
    expect(deriveNextActionKey("CLOSED")).toBe("none");
  });

  it("maps aggregate in-progress to resolve", () => {
    expect(deriveNextActionKey("IN_PROGRESS", "aggregate")).toBe("resolve");
    expect(deriveNextActionKey("CREATED", "aggregate")).toBe("assign");
    expect(deriveNextActionKey("CANCELLED", "aggregate")).toBe("none");
  });
});

describe("deriveRelevantDueAt", () => {
  it("prefers assignment due for early statuses", () => {
    expect(
      deriveRelevantDueAt({
        status: "ASSIGNED",
        assignmentDueAt: "2026-08-01T10:00:00Z",
        resolutionDueAt: "2026-08-02T10:00:00Z",
      }),
    ).toBe("2026-08-01T10:00:00Z");
  });

  it("omits when no due exists", () => {
    expect(deriveRelevantDueAt({ status: "IN_PROGRESS" })).toBeUndefined();
  });
});

describe("deriveOperationalContext", () => {
  it("omits header-canonical fields from operational panel", () => {
    const derived = deriveOperationalContext({
      status: "IN_PROGRESS",
      priority: "HIGH",
      overallSlaStatus: "ON_TIME",
      assignedToLabel: "Alex",
      branchLabel: "Branch A",
      lastUpdated: "2026-08-03T01:00:00Z",
    });

    expect(derived.operational).toEqual({
      status: "IN_PROGRESS",
      assignedTo: "Alex",
      branch: "Branch A",
      lastUpdated: "2026-08-03T01:00:00Z",
    });
    expect(derived.operational).not.toHaveProperty("priority");
    expect(derived.operational).not.toHaveProperty("owner");
    expect(derived.operational).not.toHaveProperty("sla");
    expect(derived.operational).not.toHaveProperty("currentWork");
  });

  it("hides current work when closed", () => {
    const derived = deriveOperationalContext({
      status: "CLOSED",
      priority: "MEDIUM",
      assignedToLabel: "Alex",
    });
    expect(derived.currentWork.show).toBe(false);
    expect(derived.currentWork.nextActionKey).toBe("none");
  });

  it("sets waiting blocking only for PENDING", () => {
    const pending = deriveOperationalContext({
      status: "PENDING",
      priority: "MEDIUM",
    });
    expect(pending.currentWork.blockingReasonKey).toBe("waiting_customer");

    const open = deriveOperationalContext({
      status: "IN_PROGRESS",
      priority: "MEDIUM",
    });
    expect(open.currentWork.blockingReasonKey).toBeUndefined();
  });

  it("omits customer type and count when absent", () => {
    const derived = deriveOperationalContext({
      status: "ASSIGNED",
      priority: "LOW",
      customerName: "Pat",
    });
    expect(derived.customerSummary).toEqual({ name: "Pat" });
  });

  it("includes complaint count only when provided", () => {
    const derived = deriveOperationalContext({
      status: "ASSIGNED",
      priority: "LOW",
      customerName: "Pat",
      complaintCount: 3,
    });
    expect(derived.customerSummary.complaintCount).toBe(3);
  });

  it("does not invent severity or channel", () => {
    const derived = deriveOperationalContext({
      status: "ASSIGNED",
      priority: "CRITICAL",
      category: "Billing",
      createdAt: "2026-08-01T00:00:00Z",
    });
    expect(derived.caseSummary).toEqual({
      currentStage: "ASSIGNED",
      category: "Billing",
      createdAt: "2026-08-01T00:00:00Z",
    });
  });
});
