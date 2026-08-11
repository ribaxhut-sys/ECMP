import { cleanup, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";

const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

import { KnowledgeReferenceText } from "./KnowledgeReferenceText";

describe("KnowledgeReferenceText", () => {
  afterEach(() => {
    cleanup();
    push.mockReset();
  });

  it("renders plain text unchanged when there is no reference", () => {
    renderWithProviders(<KnowledgeReferenceText text="Penyelesaian tanpa rujukan." />);
    expect(screen.getByText("Penyelesaian tanpa rujukan.")).toBeInTheDocument();
  });

  it("renders a reference marker as a clickable element showing the snapshot title", () => {
    const text =
      "Penyelesaian sesuai @[SOP Penanganan Pengaduan v2.1](knowledge:e5555555-5555-5555-5555-555555555555).";
    renderWithProviders(<KnowledgeReferenceText text={text} />);
    expect(
      screen.getByRole("button", { name: /SOP Penanganan Pengaduan v2\.1/i }),
    ).toBeInTheDocument();
  });

  it("navigates to the Knowledge detail page when the reference is clicked", async () => {
    const user = userEvent.setup();
    const text = "Sesuai @[SOP Pengaduan](knowledge:e5555555-5555-5555-5555-555555555555).";
    renderWithProviders(<KnowledgeReferenceText text={text} />);

    await user.click(screen.getByRole("button", { name: /SOP Pengaduan/i }));

    expect(push).toHaveBeenCalledWith(
      "/knowledge/e5555555-5555-5555-5555-555555555555",
    );
  });

  it("renders multiple references with plain text preserved between them", () => {
    const text =
      "Berdasarkan @[SOP A](knowledge:e5555555-5555-5555-5555-555555555555) dan @[Peraturan B](knowledge:f6666666-6666-6666-6666-666666666666), penyelesaian dilakukan.";
    renderWithProviders(<KnowledgeReferenceText text={text} />);
    expect(screen.getByRole("button", { name: /SOP A/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Peraturan B/i })).toBeInTheDocument();
    expect(screen.getByText(/dan/)).toBeInTheDocument();
  });

  it("degrades a malformed marker to plain text without crashing", () => {
    renderWithProviders(<KnowledgeReferenceText text="Sesuai @[Rusak](knowledge:not-a-uuid)." />);
    expect(
      screen.getByText("Sesuai @[Rusak](knowledge:not-a-uuid)."),
    ).toBeInTheDocument();
  });
});
