import { describe, expect, it } from "vitest";
import {
  TAXPAYER_PROFILE_CLIPBOARD_MARKER,
  formatTaxpayerProfileClipboard,
  parseTaxpayerProfileClipboard,
  taxpayerIdForClipboard,
} from "./taxpayerProfileClipboard";

describe("taxpayerIdForClipboard", () => {
  it("strips grouping spaces from numeric WP ids", () => {
    expect(taxpayerIdForClipboard("3200 0000 0000 0034")).toBe(
      "3200000000000034",
    );
  });

  it("keeps alphanumeric customer numbers without inventing digits-only", () => {
    expect(taxpayerIdForClipboard("CN-10000001")).toBe("CN-10000001");
  });
});

describe("formatTaxpayerProfileClipboard", () => {
  it("emits the ECMP-WP-1 labeled block without internal UUID", () => {
    const text = formatTaxpayerProfileClipboard({
      nama: "Ayu Santoso",
      idWp: "3200 0000 0000 0034",
      telepon: "081212345678",
      email: "ayu@example.com",
    });
    expect(text).toBe(
      [
        TAXPAYER_PROFILE_CLIPBOARD_MARKER,
        "Nama: Ayu Santoso",
        "ID WP: 3200000000000034",
        "Telepon: 081212345678",
        "Email: ayu@example.com",
      ].join("\n"),
    );
    expect(text).not.toMatch(/[0-9a-f]{8}-[0-9a-f]{4}/i);
  });
});

describe("parseTaxpayerProfileClipboard", () => {
  it("round-trips a profile block including empty contact fields", () => {
    const payload = formatTaxpayerProfileClipboard({
      nama: "Ayu Santoso",
      idWp: "3200000000000034",
      telepon: "",
      email: "",
    });
    expect(parseTaxpayerProfileClipboard(payload)).toEqual({
      kind: "profile",
      fields: {
        nama: "Ayu Santoso",
        idWp: "3200000000000034",
        telepon: "",
        email: "",
      },
    });
  });

  it("accepts Windows newlines and a BOM", () => {
    const raw =
      "\uFEFFECMP-WP-1\r\nNama: Ayu\r\nID WP: 3200000000000034\r\nTelepon: 0812\r\nEmail: a@b.c";
    expect(parseTaxpayerProfileClipboard(raw)).toEqual({
      kind: "profile",
      fields: {
        nama: "Ayu",
        idWp: "3200000000000034",
        telepon: "0812",
        email: "a@b.c",
      },
    });
  });

  it("treats a numeric-only clipboard as ID WP paste", () => {
    expect(parseTaxpayerProfileClipboard("3200 0000 0000 0034")).toEqual({
      kind: "idWp",
      idWp: "3200000000000034",
    });
  });

  it("rejects free text so a name is not treated as No. Pelanggan", () => {
    expect(parseTaxpayerProfileClipboard("Ayu Santoso")).toEqual({
      kind: "invalid",
    });
  });
});
