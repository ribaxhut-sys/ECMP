import { describe, expect, it } from "vitest";
import {
  cmBatch1FiltersFromSearchParams,
  cmBatch1FiltersToSearchParams,
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
      new URLSearchParams("status=OPEN"),
    );
    expect(parsed.status).toBe("");
  });

  it("rejects unknown intakeDisposition", () => {
    const parsed = cmBatch1FiltersFromSearchParams(
      new URLSearchParams("intakeDisposition=UNKNOWN"),
    );
    expect(parsed.intakeDisposition).toBe("");
  });
});
