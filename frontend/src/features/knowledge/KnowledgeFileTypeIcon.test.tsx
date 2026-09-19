import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { KnowledgeFileTypeIcon } from "./KnowledgeFileTypeIcon";

describe("KnowledgeFileTypeIcon", () => {
  it("shows a colored PDF badge for a PDF file", () => {
    render(
      <KnowledgeFileTypeIcon
        file={{ mimeType: "application/pdf", fileName: "sop.pdf" }}
      />,
    );
    const badge = screen.getByText("PDF");
    expect(badge.className).toContain("danger");
  });

  it("shows a colored XLSX badge for a spreadsheet file", () => {
    render(
      <KnowledgeFileTypeIcon
        file={{
          mimeType:
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          fileName: "data.xlsx",
        }}
      />,
    );
    const badge = screen.getByText("XLSX");
    expect(badge.className).toContain("success");
  });

  it("shows a colored ZIP badge for an archive file", () => {
    render(
      <KnowledgeFileTypeIcon
        file={{ mimeType: "application/zip", fileName: "bundle.zip" }}
      />,
    );
    const badge = screen.getByText("ZIP");
    expect(badge.className).toContain("warning");
  });

  it("falls back to a neutral badge with the raw extension for an unmapped type", () => {
    render(
      <KnowledgeFileTypeIcon
        file={{ mimeType: "application/rtf", fileName: "notes.rtf" }}
      />,
    );
    const badge = screen.getByText("RTF");
    // Neutral tone's classes don't literally say "neutral" (they're the
    // plain secondary/gray palette) — assert the absence of every colored
    // tone instead of a single substring.
    expect(badge.className).not.toMatch(/danger|success|warning|info/);
  });

  it("renders a picture glyph instead of a text badge for image files", () => {
    render(
      <KnowledgeFileTypeIcon
        file={{ mimeType: "image/png", fileName: "photo.png" }}
      />,
    );
    expect(screen.queryByText("PNG")).not.toBeInTheDocument();
  });
});
