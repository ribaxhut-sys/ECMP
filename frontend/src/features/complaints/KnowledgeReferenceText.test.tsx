import { cleanup, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import type { Knowledge } from "@/lib/api/types";

const push = vi.fn();
const fetchKnowledge = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchKnowledge: (...args: unknown[]) => fetchKnowledge(...args),
  };
});

import { KnowledgeReferenceText } from "./KnowledgeReferenceText";

function knowledge(overrides: Partial<Knowledge> = {}): Knowledge {
  return {
    id: "e5555555-5555-5555-5555-555555555555",
    title: "SOP Pengaduan",
    knowledgeType: "SOP",
    status: "ACTIVE",
    documentNumber: null,
    summary: null,
    versionLabel: "2.1",
    effectiveFrom: null,
    effectiveTo: null,
    ownerOrgUnitId: "PUSAT",
    publishedAt: "2026-08-01T00:00:00Z",
    publishedBy: null,
    supersedesKnowledgeId: null,
    supersedesTitle: null,
    createdBy: null,
    createdAt: "2026-07-30T00:00:00Z",
    updatedBy: null,
    updatedAt: "2026-07-30T00:00:00Z",
    files: [],
    ...overrides,
  };
}

describe("KnowledgeReferenceText", () => {
  afterEach(() => {
    cleanup();
    push.mockReset();
    fetchKnowledge.mockReset();
  });

  it("renders plain text unchanged when there is no reference", () => {
    renderWithProviders(<KnowledgeReferenceText text="Penyelesaian tanpa rujukan." />);
    expect(screen.getByText("Penyelesaian tanpa rujukan.")).toBeInTheDocument();
  });

  it("renders a reference marker as a clickable element showing the snapshot title", () => {
    fetchKnowledge.mockResolvedValue({ data: knowledge() });
    const text =
      "Penyelesaian sesuai @[SOP Penanganan Pengaduan v2.1](knowledge:e5555555-5555-5555-5555-555555555555).";
    renderWithProviders(<KnowledgeReferenceText text={text} />);
    expect(
      screen.getByRole("button", { name: /SOP Penanganan Pengaduan v2\.1/i }),
    ).toBeInTheDocument();
  });

  it("navigates to the Knowledge detail page when the reference is clicked", async () => {
    const user = userEvent.setup();
    fetchKnowledge.mockResolvedValue({ data: knowledge() });
    const text = "Sesuai @[SOP Pengaduan](knowledge:e5555555-5555-5555-5555-555555555555).";
    renderWithProviders(<KnowledgeReferenceText text={text} />);

    await user.click(screen.getByRole("button", { name: /SOP Pengaduan/i }));

    expect(push).toHaveBeenCalledWith(
      "/knowledge/e5555555-5555-5555-5555-555555555555",
    );
  });

  it("renders the reference title in italic blue when Knowledge is active", async () => {
    fetchKnowledge.mockResolvedValue({ data: knowledge({ status: "ACTIVE" }) });
    const text = "Sesuai @[SOP Pengaduan](knowledge:e5555555-5555-5555-5555-555555555555).";
    renderWithProviders(<KnowledgeReferenceText text={text} />);
    const button = screen.getByRole("button", { name: /SOP Pengaduan/i });
    expect(button.className).toContain("italic");
    expect(button.className).toContain("text-ecmp-primary");
    await waitFor(() => {
      expect(screen.getByText("SOP")).toBeInTheDocument();
    });
  });

  it("renders inactive Knowledge references in red", async () => {
    fetchKnowledge.mockResolvedValue({
      data: knowledge({ status: "ARCHIVED" }),
    });
    const text = "Sesuai @[SOP Pengaduan](knowledge:e5555555-5555-5555-5555-555555555555).";
    renderWithProviders(<KnowledgeReferenceText text={text} />);

    await waitFor(() => {
      const button = screen.getByRole("button", { name: /SOP Pengaduan/i });
      expect(button.className).toContain("text-ecmp-danger");
      expect(button.className).not.toContain("text-ecmp-primary");
    });
  });

  it("renders multiple references with plain text preserved between them", () => {
    fetchKnowledge.mockResolvedValue({ data: knowledge() });
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
