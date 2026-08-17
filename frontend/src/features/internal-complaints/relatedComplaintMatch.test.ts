import { describe, expect, it } from "vitest";
import {
  looksLikeRelatedComplaintQuery,
  matchRelatedComplaint,
  mergeRelatedComplaintRefs,
  relatedComplaintFromListRow,
  resolveRelatedComplaintPayload,
} from "./relatedComplaintMatch";

const ROW = {
  id: "11111111-1111-1111-1111-111111111111",
  number: "CM-2026-0001",
  subject: "Antrian panjang",
  createdAt: "2026-08-17T01:00:00Z",
  createdByName: "Ani",
};

describe("relatedComplaintMatch", () => {
  it("maps a list row and skips incomplete rows", () => {
    expect(
      relatedComplaintFromListRow({
        complaintId: ROW.id,
        complaintNumber: ROW.number,
        subject: "  Antrian panjang  ",
        createdAt: ROW.createdAt,
        createdByName: "Ani",
      }),
    ).toEqual(ROW);
    expect(
      relatedComplaintFromListRow({
        complaintId: "",
        complaintNumber: "CM-1",
      }),
    ).toBeNull();
  });

  it("matches on number or id, case-insensitive for number", () => {
    expect(matchRelatedComplaint("cm-2026-0001", [ROW])?.id).toBe(ROW.id);
    expect(matchRelatedComplaint(ROW.id, [ROW])?.id).toBe(ROW.id);
    expect(matchRelatedComplaint("CM-9999", [ROW])).toBeNull();
    expect(matchRelatedComplaint("  ", [ROW])).toBeNull();
  });

  it("matches a unique subject or reporter name", () => {
    expect(matchRelatedComplaint("Antrian panjang", [ROW])?.id).toBe(ROW.id);
    expect(matchRelatedComplaint("Ani", [ROW])?.id).toBe(ROW.id);
    const twin = { ...ROW, id: "222", number: "CM-2", subject: "Antrian panjang" };
    expect(matchRelatedComplaint("Antrian panjang", [ROW, twin])).toBeNull();
  });

  it("detects complete-looking related queries", () => {
    expect(looksLikeRelatedComplaintQuery("CM-1")).toBe(true);
    expect(looksLikeRelatedComplaintQuery(ROW.id)).toBe(true);
    expect(looksLikeRelatedComplaintQuery("Ani")).toBe(true);
    expect(looksLikeRelatedComplaintQuery("a")).toBe(false);
    expect(looksLikeRelatedComplaintQuery("")).toBe(false);
  });

  it("merges refs by id", () => {
    const extra = { ...ROW, id: "222", number: "CM-2", subject: "Lain" };
    expect(mergeRelatedComplaintRefs([ROW], [ROW, extra]).map((r) => r.id)).toEqual(
      [ROW.id, "222"],
    );
  });

  it("resolves payload: empty, matched, CM- literal, or unresolved keyword", () => {
    expect(resolveRelatedComplaintPayload("", [ROW])).toEqual({
      status: "empty",
      id: null,
    });
    expect(resolveRelatedComplaintPayload("Antrian panjang", [ROW])).toEqual({
      status: "matched",
      id: ROW.id,
    });
    expect(resolveRelatedComplaintPayload("CM-2026-9999", [ROW])).toEqual({
      status: "literal",
      id: "CM-2026-9999",
    });
    expect(resolveRelatedComplaintPayload("bukan nomor", [ROW])).toEqual({
      status: "unresolved",
    });
  });
});
