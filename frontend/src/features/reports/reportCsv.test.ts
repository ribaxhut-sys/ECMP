import { describe, expect, it } from "vitest";
import { buildReportCsv, reportCsvFilename } from "./reportCsv";

describe("buildReportCsv", () => {
  it("quotes every cell and separates rows with CRLF", () => {
    const csv = buildReportCsv([
      ["Metrik", "Jumlah"],
      ["Total pengaduan", 16],
    ]);
    expect(csv).toBe(
      '﻿"Metrik","Jumlah"\r\n"Total pengaduan","16"\r\n',
    );
  });

  it("escapes embedded quotes so a label cannot break the column layout", () => {
    const csv = buildReportCsv([['Unit "Pusat"', 3]]);
    expect(csv).toContain('"Unit ""Pusat""","3"');
  });

  it("keeps a comma inside a cell from splitting the row", () => {
    const csv = buildReportCsv([["Terbuka, belum ditutup", 8]]);
    expect(csv.trim().split("\r\n")).toHaveLength(1);
  });
});

describe("reportCsvFilename", () => {
  it("stamps the period and the export date", () => {
    expect(
      reportCsvFilename("thisMonth", new Date("2026-08-18T10:00:00.000Z")),
    ).toBe("laporan-pengaduan-thisMonth-2026-08-18.csv");
  });
});
