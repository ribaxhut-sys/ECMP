import { describe, expect, it } from "vitest";
import {
  findMockAccount,
  mockEntryHref,
  MOCK_ACCOUNTS,
} from "@/auth/mockAuth";

describe("mockAuth", () => {
  it("exposes four personas", () => {
    expect(MOCK_ACCOUNTS.map((a) => a.persona).sort()).toEqual([
      "administrator",
      "complaint_officer",
      "manager",
      "supervisor",
    ].sort());
  });

  it("maps entry points per NAV-001 / B0", () => {
    const officer = findMockAccount("officer")!;
    expect(
      mockEntryHref({
        user: officer.user,
        persona: "complaint_officer",
        officerWorkMode: "intake",
      }),
    ).toBe("/workspace");
    expect(
      mockEntryHref({
        user: officer.user,
        persona: "complaint_officer",
        officerWorkMode: "handling",
      }),
    ).toBe("/queue");
    expect(
      mockEntryHref({
        user: findMockAccount("supervisor")!.user,
        persona: "supervisor",
        officerWorkMode: "handling",
      }),
    ).toBe("/queue");
  });
});
