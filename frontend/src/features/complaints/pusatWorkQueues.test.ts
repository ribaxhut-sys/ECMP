import { describe, expect, it } from "vitest";
import type { CmBatch1ComplaintResponse } from "@/lib/api";
import type { CmCaseSummary } from "@/lib/api/cmCase";
import {
  complaintWorkListIsUnread,
  isPusatFollowUpCase,
  isPusatUnhandledCase,
  isPusatUnhandledComplaint,
  keepPusatPengaduanListRow,
} from "./pusatWorkQueues";

function complaint(
  overrides: Partial<CmBatch1ComplaintResponse> = {},
): CmBatch1ComplaintResponse {
  return {
    complaintId: "cx-1",
    complaintNumber: "TAB-0001",
    status: "IN_PROGRESS",
    customerId: "cust-1",
    caseCreated: true,
    replayed: false,
    createdAt: "2026-08-01T00:00:00Z",
    ...overrides,
  } as CmBatch1ComplaintResponse;
}

function caseSummary(
  overrides: Partial<CmCaseSummary> = {},
): CmCaseSummary {
  return {
    caseId: "case-1",
    caseNumber: "CASE-1",
    complaintId: "cx-1",
    status: "IN_PROGRESS",
    ...overrides,
  } as CmCaseSummary;
}

describe("Pengaduan Pusat — never handled", () => {
  it("includes an unclaimed Case escalated from the branch", () => {
    expect(
      isPusatUnhandledCase(
        caseSummary({ escalatedToPusat: true }),
        complaint({ intakeDisposition: "ESCALATE_APPROVED" }),
      ),
    ).toBe(true);
  });

  it("includes a parent still waiting for Pusat to accept", () => {
    expect(
      isPusatUnhandledComplaint(
        complaint({
          intakeDisposition: "ESCALATE_APPROVED",
          needsPusatHandling: true,
        }),
      ),
    ).toBe(true);
  });

  it("excludes a Case after Pusat accepted", () => {
    expect(
      isPusatUnhandledCase(
        caseSummary({ escalatedToPusat: true }),
        complaint({
          intakeDisposition: "ESCALATE_APPROVED",
          hqAcceptedAt: "2026-08-17T10:00:00Z",
        }),
      ),
    ).toBe(false);
  });

  it("excludes a claimed Case", () => {
    expect(
      isPusatUnhandledCase(
        caseSummary({
          escalatedToPusat: true,
          handlingClaimedBy: "user-hq",
        }),
        complaint({ intakeDisposition: "ESCALATE_APPROVED" }),
      ),
    ).toBe(false);
  });

  it("excludes HQ scheduled work (already handled — Tindak lanjut)", () => {
    expect(
      isPusatUnhandledCase(
        caseSummary({ escalatedToPusat: true }),
        complaint({ intakeDisposition: "HQ_SCHEDULED" }),
      ),
    ).toBe(false);
    expect(
      isPusatUnhandledComplaint(
        complaint({
          intakeDisposition: "HQ_SCHEDULED",
          needsPusatHandling: true,
        }),
      ),
    ).toBe(false);
  });

  it("keeps a later unclaimed Case after the parent was returned to branch", () => {
    expect(
      isPusatUnhandledCase(
        caseSummary({ escalatedToPusat: true }),
        complaint({ intakeDisposition: "RETURNED_TO_BRANCH" }),
      ),
    ).toBe(true);
  });

  it("excludes a closed parent", () => {
    expect(
      isPusatUnhandledCase(
        caseSummary({ escalatedToPusat: true }),
        complaint({ status: "CLOSED", intakeDisposition: "ESCALATE_APPROVED" }),
      ),
    ).toBe(false);
  });

  it("drops a claimed sibling from the Pengaduan list", () => {
    const parent = complaint({ intakeDisposition: "ESCALATE_APPROVED" });
    expect(
      keepPusatPengaduanListRow({
        key: "claimed",
        complaint: parent,
        caseItem: caseSummary({
          caseId: "claimed",
          escalatedToPusat: true,
          handlingClaimedBy: "user-hq",
        }),
        casesState: "ready",
      }),
    ).toBe(false);
    expect(
      keepPusatPengaduanListRow({
        key: "new",
        complaint: parent,
        caseItem: caseSummary({ caseId: "new", escalatedToPusat: true }),
        casesState: "ready",
      }),
    ).toBe(true);
  });
});

describe("Tindak lanjut Pusat — already handled, still open", () => {
  it("includes accepted but unscheduled work", () => {
    expect(
      isPusatFollowUpCase(
        caseSummary({ escalatedToPusat: true }),
        complaint({
          intakeDisposition: "ESCALATE_APPROVED",
          hqAcceptedAt: "2026-08-17T10:00:00Z",
        }),
      ),
    ).toBe(true);
  });

  it("includes a scheduled HQ visit", () => {
    expect(
      isPusatFollowUpCase(
        caseSummary({ escalatedToPusat: true }),
        complaint({
          intakeDisposition: "HQ_SCHEDULED",
          hqAcceptedAt: "2026-08-17T10:00:00Z",
        }),
      ),
    ).toBe(true);
  });

  it("includes a claimed escalated Case", () => {
    expect(
      isPusatFollowUpCase(
        caseSummary({
          escalatedToPusat: true,
          handlingClaimedBy: "user-hq",
        }),
        complaint({
          intakeDisposition: "ESCALATE_APPROVED",
          hqAcceptedAt: "2026-08-17T10:00:00Z",
        }),
      ),
    ).toBe(true);
  });

  it("excludes never-handled intake (belongs on Pengaduan)", () => {
    expect(
      isPusatFollowUpCase(
        caseSummary({ escalatedToPusat: true }),
        complaint({ intakeDisposition: "ESCALATE_APPROVED" }),
      ),
    ).toBe(false);
  });

  it("excludes claimed returned work and pending cabang approval", () => {
    expect(
      isPusatFollowUpCase(
        caseSummary({ escalatedToPusat: true, handlingClaimedBy: "user-hq" }),
        complaint({ intakeDisposition: "RETURNED_TO_BRANCH" }),
      ),
    ).toBe(false);
    expect(
      isPusatFollowUpCase(
        caseSummary({ status: "IN_PROGRESS" }),
        complaint({ intakeDisposition: "ESCALATE_PENDING_APPROVAL" }),
      ),
    ).toBe(false);
  });

  it("excludes a branch-only Case that never reached Pusat", () => {
    expect(
      isPusatFollowUpCase(
        caseSummary({ status: "IN_PROGRESS" }),
        complaint(),
      ),
    ).toBe(false);
  });
});

describe("complaintWorkListIsUnread", () => {
  it("Pusat bolds only the badge receipt, not queue membership", () => {
    expect(
      complaintWorkListIsUnread(
        complaint({ needsPusatHandling: true, pusatUnread: false }),
        true,
      ),
    ).toBe(false);
    expect(
      complaintWorkListIsUnread(
        complaint({ needsPusatHandling: true, pusatUnread: true }),
        true,
      ),
    ).toBe(true);
  });

  it("Cabang bolds from Case inbox isRead, not needsPusatHandling", () => {
    expect(
      complaintWorkListIsUnread(
        complaint({ needsPusatHandling: true }),
        false,
        caseSummary({ isRead: true }),
      ),
    ).toBe(false);
    expect(
      complaintWorkListIsUnread(
        complaint({ needsPusatHandling: false }),
        false,
        caseSummary({ isRead: false }),
      ),
    ).toBe(true);
  });
});
