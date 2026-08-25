import { describe, expect, it } from "vitest";
import {
  cmBatch1FiltersFromSearchParams,
  cmBatch1FiltersToSearchParams,
  defaultCmBatch1ListFilters,
} from "./cmBatch1ListFilters";

describe("cmBatch1ListFilters", () => {
  it("parses and serializes keyword/status/intakeDisposition", () => {
    const parsed = cmBatch1FiltersFromSearchParams(
      new URLSearchParams(
        "keyword=CM-1&status=closed&intakeDisposition=escalate_pending_approval&page=2",
      ),
    );
    expect(parsed.keyword).toBe("CM-1");
    expect(parsed.status).toBe("CLOSED");
    expect(parsed.intakeDisposition).toBe("ESCALATE_PENDING_APPROVAL");
    expect(parsed.page).toBe(2);

    const qs = cmBatch1FiltersToSearchParams(parsed).toString();
    expect(qs).toContain("keyword=CM-1");
    expect(qs).toContain("status=CLOSED");
    expect(qs).toContain("intakeDisposition=ESCALATE_PENDING_APPROVAL");
    expect(qs).toContain("page=2");
  });

  it("rejects unknown status", () => {
    const parsed = cmBatch1FiltersFromSearchParams(
      new URLSearchParams("status=FOO"),
    );
    expect(parsed.status).toBe("");
  });

  it("rejects unknown intakeDisposition", () => {
    const parsed = cmBatch1FiltersFromSearchParams(
      new URLSearchParams("intakeDisposition=UNKNOWN"),
    );
    expect(parsed.intakeDisposition).toBe("");
  });

  it("parses IN_PROGRESS and OPEN (DEC-025)", () => {
    expect(
      cmBatch1FiltersFromSearchParams(new URLSearchParams("status=IN_PROGRESS"))
        .status,
    ).toBe("IN_PROGRESS");
    expect(
      cmBatch1FiltersFromSearchParams(new URLSearchParams("status=OPEN")).status,
    ).toBe("OPEN");
  });

  it("parses dashboard open and waiting-assignment drill-down queries", () => {
    const open = cmBatch1FiltersFromSearchParams(
      new URLSearchParams("status=OPEN"),
    );
    expect(open.status).toBe("OPEN");
    expect(open.intakeDisposition).toBe("");

    const waiting = cmBatch1FiltersFromSearchParams(
      new URLSearchParams("status=REGISTERED&intakeDisposition=UNESCALATED"),
    );
    expect(waiting.status).toBe("REGISTERED");
    expect(waiting.intakeDisposition).toBe("UNESCALATED");
  });

  it("parses and serializes needsPusatHandling", () => {
    const parsed = cmBatch1FiltersFromSearchParams(
      new URLSearchParams("needsPusatHandling=1"),
    );
    expect(parsed.needsPusatHandling).toBe(true);
    expect(cmBatch1FiltersToSearchParams(parsed).get("needsPusatHandling")).toBe(
      "1",
    );
  });

  it("defaults Pusat Pengaduan to the unhandled queue", () => {
    expect(defaultCmBatch1ListFilters().needsPusatHandling).toBe(false);
    expect(
      defaultCmBatch1ListFilters({ pusatUnhandledQueue: true })
        .needsPusatHandling,
    ).toBe(true);
  });

  it("defaults Cabang work list to OPEN and Ditutup to CLOSED", () => {
    expect(defaultCmBatch1ListFilters({ openOnly: true }).status).toBe("OPEN");
    expect(defaultCmBatch1ListFilters({ closedArchive: true }).status).toBe(
      "CLOSED",
    );
    expect(
      defaultCmBatch1ListFilters({ closedArchive: true }).needsPusatHandling,
    ).toBe(false);
  });
});
