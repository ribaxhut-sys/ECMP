import { describe, expect, it } from "vitest";
import {
  actorMatchesInternalHandlingUnit,
  displayInternalUnitCode,
  filterInternalTransferDestinations,
  filterTransferDestinations,
  formatRelatedComplaintOptionLabel,
  formatUnitOptionLabel,
  isPusatUnitCode,
  resolveCreateSourceUnitCode,
} from "./transferDirection";

describe("transferDirection", () => {
  it("detects pusat codes", () => {
    expect(isPusatUnitCode("PUSAT")).toBe(true);
    expect(isPusatUnitCode("ho")).toBe(true);
    expect(isPusatUnitCode("UPPPD-GAMBIR")).toBe(false);
  });

  it("from cabang only allows the canonical Pusat root, not CRO sub-units", () => {
    const branches = [
      { code: "PUSAT", name: "Kantor Pusat" },
      { code: "PUSAT-CRO", name: "CRO" },
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

  it("cabang actor at pusat handling cannot pick another cabang", () => {
    const branches = [
      { code: "PUSAT", name: "Kantor Pusat" },
      { code: "UPPPD-GAMBIR", name: "Gambir" },
      { code: "UPPPD-MENTENG", name: "Menteng" },
    ];
    expect(
      filterInternalTransferDestinations(branches, {
        actorUnitId: "UPPPD-GAMBIR",
        handlingUnitId: "PUSAT",
      }).map((b) => b.code),
    ).toEqual([]);
  });

  it("cabang actor with local handling may only pick pusat", () => {
    const branches = [
      { code: "PUSAT", name: "Kantor Pusat" },
      { code: "UPPPD-GAMBIR", name: "Gambir" },
      { code: "UPPPD-MENTENG", name: "Menteng" },
    ];
    expect(
      filterInternalTransferDestinations(branches, {
        actorUnitId: "UPPPD-GAMBIR",
        handlingUnitId: "UPPPD-GAMBIR",
      }).map((b) => b.code),
    ).toEqual(["PUSAT"]);
  });

  it("pusat actor at pusat handling may pick cabang", () => {
    const branches = [
      { code: "PUSAT", name: "Kantor Pusat" },
      { code: "UPPPD-GAMBIR", name: "Gambir" },
      { code: "UPPPD-MENTENG", name: "Menteng" },
    ];
    expect(
      filterInternalTransferDestinations(branches, {
        actorUnitId: "PUSAT",
        handlingUnitId: "PUSAT",
      }).map((b) => b.code),
    ).toEqual(["UPPPD-GAMBIR", "UPPPD-MENTENG"]);
  });

  it("missing actor unit is treated as cabang, not pusat", () => {
    const branches = [
      { code: "PUSAT", name: "Kantor Pusat" },
      { code: "UPPPD-GAMBIR", name: "Gambir" },
    ];
    expect(
      filterInternalTransferDestinations(branches, {
        actorUnitId: null,
        handlingUnitId: "UPPPD-GAMBIR",
        actorIsAdmin: false,
      }).map((b) => b.code),
    ).toEqual(["PUSAT"]);
    expect(
      filterInternalTransferDestinations(branches, {
        actorUnitId: null,
        handlingUnitId: "PUSAT",
        actorIsAdmin: true,
      }).map((b) => b.code),
    ).toEqual(["UPPPD-GAMBIR"]);
  });

  it("treats missing create-form membership as Pusat", () => {
    expect(resolveCreateSourceUnitCode(null)).toBe("PUSAT");
    expect(resolveCreateSourceUnitCode("")).toBe("PUSAT");
    expect(resolveCreateSourceUnitCode("ho")).toBe("PUSAT");
    expect(resolveCreateSourceUnitCode("UPPPD-GAMBIR")).toBe("UPPPD-GAMBIR");
    expect(
      resolveCreateSourceUnitCode(null, { treatMissingAsPusat: false }),
    ).toBeNull();
  });

  it("matches any Pusat login to Pusat handling, not Cabang", () => {
    expect(
      actorMatchesInternalHandlingUnit("PUSAT", "PUSAT-CRO", ["AGENT"]),
    ).toBe(true);
    expect(
      actorMatchesInternalHandlingUnit(null, "PUSAT", ["ADMIN"]),
    ).toBe(true);
    expect(
      actorMatchesInternalHandlingUnit(null, "PUSAT", ["AGENT"]),
    ).toBe(false);
    expect(
      actorMatchesInternalHandlingUnit("UPPPD-GAMBIR", "PUSAT", ["AGENT"]),
    ).toBe(false);
    expect(
      actorMatchesInternalHandlingUnit("UPPPD-GAMBIR", "UPPPD-GAMBIR", [
        "AGENT",
      ]),
    ).toBe(true);
  });

  it("displays Pusat sub-units as canonical PUSAT", () => {
    expect(displayInternalUnitCode("PUSAT-CRO")).toBe("PUSAT");
    expect(displayInternalUnitCode("HO-CRO")).toBe("PUSAT");
    expect(displayInternalUnitCode("UPPPD-GAMBIR")).toBe("UPPPD-GAMBIR");
    expect(displayInternalUnitCode("")).toBe("");
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
