import { describe, expect, it } from "vitest";
import {
  filterTransferDestinations,
  formatRelatedComplaintOptionLabel,
  formatUnitOptionLabel,
  isPusatUnitCode,
} from "./transferDirection";

describe("transferDirection", () => {
  it("detects pusat codes", () => {
    expect(isPusatUnitCode("PUSAT")).toBe(true);
    expect(isPusatUnitCode("ho")).toBe(true);
    expect(isPusatUnitCode("UPPPD-GAMBIR")).toBe(false);
  });

  it("from cabang only allows pusat destinations", () => {
    const branches = [
      { code: "PUSAT", name: "Kantor Pusat" },
      { code: "UPPPD-GAMBIR", name: "Gambir" },
      { code: "UPPPD-MENTENG", name: "Menteng" },
    ];
    expect(
      filterTransferDestinations(branches, "UPPPD-GAMBIR").map((b) => b.code),
    ).toEqual(["PUSAT"]);
  });

  it("from pusat only allows cabang destinations", () => {
    const branches = [
      { code: "PUSAT", name: "Kantor Pusat" },
      { code: "UPPPD-GAMBIR", name: "Gambir" },
      { code: "UPPPD-MENTENG", name: "Menteng" },
    ];
    expect(
      filterTransferDestinations(branches, "PUSAT").map((b) => b.code),
    ).toEqual(["UPPPD-GAMBIR", "UPPPD-MENTENG"]);
  });

  it("formats unit labels for compact native selects", () => {
    expect(formatUnitOptionLabel("PUSAT", "Pusat")).toBe("Pusat");
    expect(formatUnitOptionLabel("PUSAT", "Kantor Pusat")).toBe("Kantor Pusat");
    expect(formatUnitOptionLabel("UPPPD-GAMBIR", "Gambir")).toBe("Gambir");
    expect(formatUnitOptionLabel("UPPPD-GAMBIR", "")).toBe("UPPPD-GAMBIR");
  });

  it("uses complaint number only for related suggestions", () => {
    expect(formatRelatedComplaintOptionLabel("CM-1")).toBe("CM-1");
    expect(formatRelatedComplaintOptionLabel("CM-2")).toBe("CM-2");
  });
});
