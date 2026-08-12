import { describe, expect, it } from "vitest";
import {
  buildPenangananSummarySegments,
  isHqIntakeDisposition,
  joinPenangananSummarySegments,
  partitionPenanganan,
  penangananCountsFromCases,
  penangananGroupForStatus,
  penangananSummaryCounts,
  resolvePenangananContextKind,
} from "./penangananGroups";

describe("penangananGroups", () => {
  it("maps terminal and escalated statuses", () => {
    expect(penangananGroupForStatus("IN_PROGRESS")).toBe("open");
    expect(penangananGroupForStatus("CREATED")).toBe("open");
    expect(penangananGroupForStatus("ESCALATED")).toBe("pusat");
    expect(penangananGroupForStatus("RESOLVED")).toBe("done");
    expect(penangananGroupForStatus("CLOSED")).toBe("done");
    expect(penangananGroupForStatus("CANCELLED")).toBe("cancelled");
  });

  it("moves open cases to pusat when complaint is on HQ intake path", () => {
    expect(
      penangananGroupForStatus("ASSIGNED", { complaintOnHqPath: true }),
    ).toBe("pusat");
    expect(
      penangananGroupForStatus("CLOSED", { complaintOnHqPath: true }),
    ).toBe("done");
  });

  it("detects active HQ intake dispositions only", () => {
    expect(isHqIntakeDisposition("ESCALATE_PENDING_APPROVAL")).toBe(true);
    expect(isHqIntakeDisposition("HQ_SCHEDULED")).toBe(true);
    expect(isHqIntakeDisposition("ESCALATE_REJECTED")).toBe(false);
    expect(isHqIntakeDisposition("RETURNED_TO_BRANCH")).toBe(false);
    expect(isHqIntakeDisposition(null)).toBe(false);
  });

  it("partitions and counts", () => {
    const parts = partitionPenanganan(
      [
        { status: "IN_PROGRESS", id: "a" },
        { status: "ESCALATED", id: "b" },
        { status: "CLOSED", id: "c" },
        { status: "CANCELLED", id: "d" },
      ],
      { complaintOnHqPath: false },
    );
    expect(parts.open.map((x) => x.id)).toEqual(["a"]);
    expect(parts.pusat.map((x) => x.id)).toEqual(["b"]);
    expect(parts.done.map((x) => x.id)).toEqual(["c"]);
    expect(parts.cancelled.map((x) => x.id)).toEqual(["d"]);
    expect(penangananSummaryCounts(parts)).toEqual({
      open: 1,
      pusat: 1,
      done: 1,
      cancelled: 1,
    });
  });

  it("summarizes list-column counts with HQ path", () => {
    expect(
      penangananCountsFromCases(
        [{ status: "IN_PROGRESS" }, { status: "CLOSED" }],
        null,
      ),
    ).toEqual({ open: 1, pusat: 0, done: 1, cancelled: 0 });
    expect(
      penangananCountsFromCases(
        [{ status: "ASSIGNED" }, { status: "CLOSED" }],
        "ESCALATE_PENDING_APPROVAL",
      ),
    ).toEqual({ open: 0, pusat: 1, done: 1, cancelled: 0 });
  });

  it("omits zero segments from summary", () => {
    const labels = {
      open: (n: number) => `${n} terbuka`,
      pusat: (n: number) => `${n} ke Pusat`,
      done: (n: number) => `${n} selesai`,
    };
    expect(
      joinPenangananSummarySegments(
        buildPenangananSummarySegments(
          { open: 2, pusat: 0, done: 0 },
          labels,
        ),
      ),
    ).toBe("2 terbuka");
    expect(
      joinPenangananSummarySegments(
        buildPenangananSummarySegments(
          { open: 1, pusat: 1, done: 0 },
          labels,
        ),
      ),
    ).toBe("1 terbuka · 1 ke Pusat");
    expect(
      joinPenangananSummarySegments(
        buildPenangananSummarySegments(
          { open: 0, pusat: 0, done: 0 },
          labels,
        ),
      ),
    ).toBeNull();
  });

  it("resolves context kind with priority closed > hq > counts > none", () => {
    expect(
      resolvePenangananContextKind({
        complaintStatus: "CLOSED",
        counts: { open: 0, pusat: 0, done: 0 },
      }),
    ).toBe("closed");
    expect(
      resolvePenangananContextKind({
        intakeDisposition: "BRANCH_CLOSED",
        counts: { open: 0, pusat: 0, done: 0 },
      }),
    ).toBe("closed");
    expect(
      resolvePenangananContextKind({
        complaintStatus: "REGISTERED",
        intakeDisposition: "ESCALATE_PENDING_APPROVAL",
        counts: { open: 0, pusat: 0, done: 0 },
      }),
    ).toBe("hq_waiting");
    expect(
      resolvePenangananContextKind({
        complaintStatus: "REGISTERED",
        intakeDisposition: null,
        counts: { open: 2, pusat: 0, done: 0 },
      }),
    ).toBe("has_counts");
    expect(
      resolvePenangananContextKind({
        complaintStatus: "REGISTERED",
        intakeDisposition: null,
        counts: { open: 0, pusat: 0, done: 0 },
      }),
    ).toBe("none");
  });
});
