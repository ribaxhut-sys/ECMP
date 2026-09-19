import { afterEach, describe, expect, it } from "vitest";
import {
  clearEscalateIntakeDraft,
  consumeIntakeFormResume,
  markIntakeFormResume,
  peekEscalateIntakeDraft,
  stashEscalateIntakeDraft,
  type EscalateIntakeDraft,
} from "./escalateIntakeDraft";
import { createEmptyComplaintForm } from "./createComplaintForm";

function sampleDraft(
  overrides?: Partial<EscalateIntakeDraft>,
): EscalateIntakeDraft {
  return {
    values: {
      ...createEmptyComplaintForm({ channel: "BRANCH" }),
      customerId: "cust-1",
      customerName: "Ada",
      subject: "Mesin error",
      description: "Detail",
    },
    stagingToken: "stg-token-1",
    hasStagedAttachments: true,
    overrideJustification: null,
    recordingUnitCode: "UPPPD-X",
    intent: "register",
    ...overrides,
  };
}

afterEach(() => {
  clearEscalateIntakeDraft();
  sessionStorage.removeItem("ecmp.cm.intakeFormResume.v1");
});

describe("escalateIntakeDraft", () => {
  it("keeps draft available after Lanjut so create form can restore without resume flag", () => {
    stashEscalateIntakeDraft(sampleDraft());
    const peeked = peekEscalateIntakeDraft();
    expect(peeked?.values.customerId).toBe("cust-1");
    expect(peeked?.values.subject).toBe("Mesin error");
    expect(peeked?.stagingToken).toBe("stg-token-1");
    expect(peeked?.hasStagedAttachments).toBe(true);
  });

  it("restores extra Case drafts", () => {
    stashEscalateIntakeDraft(
      sampleDraft({
        extraCaseDrafts: [{ id: "e1", description: "Case 2 uraian" }],
      }),
    );
    expect(peekEscalateIntakeDraft()?.extraCaseDrafts).toEqual([
      {
        id: "e1",
        // Extra Case cards carry their own title now — sanitize normalizes the
        // missing field to "" rather than dropping it.
        subject: "",
        description: "Case 2 uraian",
        priority: "",
        note: "",
        action: "register",
        locked: false,
      },
    ]);
  });

  it("peek does not clear the draft (safe under Strict remount / breadcrumb)", () => {
    stashEscalateIntakeDraft(sampleDraft());
    expect(peekEscalateIntakeDraft()?.values.subject).toBe("Mesin error");
    expect(peekEscalateIntakeDraft()?.values.subject).toBe("Mesin error");
  });

  it("keeps draft without locked intent after Lanjut", () => {
    stashEscalateIntakeDraft(sampleDraft({ intent: undefined }));
    const peeked = peekEscalateIntakeDraft();
    expect(peeked?.values.customerId).toBe("cust-1");
    expect(peeked?.intent).toBeUndefined();
  });

  it("clears invalid legacy intent instead of defaulting to escalate", () => {
    sessionStorage.setItem(
      "ecmp.cm.escalateIntakeDraft.v1",
      JSON.stringify({
        ...sampleDraft(),
        intent: "legacy-unknown",
      }),
    );
    const peeked = peekEscalateIntakeDraft();
    expect(peeked?.intent).toBeUndefined();
  });

  it("clearEscalateIntakeDraft also clears legacy resume flag", () => {
    stashEscalateIntakeDraft(sampleDraft());
    markIntakeFormResume();
    clearEscalateIntakeDraft();
    expect(peekEscalateIntakeDraft()).toBeNull();
    expect(consumeIntakeFormResume()).toBe(false);
  });
});
