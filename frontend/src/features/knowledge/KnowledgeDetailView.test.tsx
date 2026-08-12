/**
 * KnowledgeDetailView — Edit modal now embeds the Documents section so a
 * knowledge:manage holder can replace files without leaving the modal
 * (mirrors the Create modal's staged upload). Files stay DRAFT-only per
 * backend gate (KM §17/§23) — ACTIVE/ARCHIVED records show the list
 * read-only, same as the page-level Documents section.
 */
import { cleanup, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import type { Knowledge } from "@/lib/api/types";

const fetchKnowledge = vi.fn();
const fetchKnowledgeHistory = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn() }),
}));

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({
    hasPermission: (perm: string) => perm === "knowledge:manage",
    user: null,
    roles: ["ADMIN"],
    status: "authenticated",
  }),
}));

vi.mock("@/features/announcements/useOrgUnitCode", () => ({
  useOrgUnitCode: () => null,
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchKnowledge: (...args: unknown[]) => fetchKnowledge(...args),
    fetchKnowledgeHistory: (...args: unknown[]) => fetchKnowledgeHistory(...args),
  };
});

import { KnowledgeDetailView } from "./KnowledgeDetailView";

function knowledge(overrides: Partial<Knowledge> = {}): Knowledge {
  return {
    id: "f6666666-6666-6666-6666-666666666666",
    title: "SOP Penanganan Pengaduan",
    knowledgeType: "SOP",
    status: "DRAFT",
    documentNumber: "SOP-001",
    summary: "Ringkasan.",
    versionLabel: "2.1",
    effectiveFrom: null,
    effectiveTo: null,
    ownerOrgUnitId: "PUSAT",
    publishedAt: null,
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

describe("KnowledgeDetailView — Edit modal Documents section", () => {
  beforeEach(() => {
    fetchKnowledge.mockReset();
    fetchKnowledgeHistory.mockReset();
    fetchKnowledgeHistory.mockResolvedValue({ data: [] });
  });

  afterEach(() => {
    cleanup();
  });

  it("lets a manager upload files from inside the Edit modal for a DRAFT record", async () => {
    const user = userEvent.setup();
    fetchKnowledge.mockResolvedValue({ data: knowledge({ status: "DRAFT" }) });

    renderWithProviders(<KnowledgeDetailView id="f6666666-6666-6666-6666-666666666666" />);

    await user.click(await screen.findByRole("button", { name: /^edit$/i }));
    const dialog = await screen.findByRole("dialog");

    expect(within(dialog).getByText("Documents")).toBeInTheDocument();
    expect(
      within(dialog).getByRole("button", { name: /upload primary file/i }),
    ).toBeInTheDocument();
    expect(
      within(dialog).getByRole("button", { name: /add supporting file/i }),
    ).toBeInTheDocument();
  });

  it("shows the Documents list read-only in the Edit modal once the record is ACTIVE", async () => {
    const user = userEvent.setup();
    fetchKnowledge.mockResolvedValue({
      data: knowledge({
        status: "ACTIVE",
        files: [
          {
            id: "g7777777-7777-7777-7777-777777777777",
            fileName: "sop-utama.pdf",
            mimeType: "application/pdf",
            sizeBytes: 1024,
            role: "PRIMARY",
            createdAt: "2026-07-30T00:00:00Z",
          },
        ],
      }),
    });

    renderWithProviders(<KnowledgeDetailView id="f6666666-6666-6666-6666-666666666666" />);

    await waitFor(() => {
      expect(fetchKnowledge).toHaveBeenCalled();
    });
    await user.click(await screen.findByRole("button", { name: /^edit$/i }));
    const dialog = await screen.findByRole("dialog");

    expect(within(dialog).getByText("sop-utama.pdf")).toBeInTheDocument();
    expect(
      within(dialog).queryByRole("button", { name: /upload primary file/i }),
    ).not.toBeInTheDocument();
    expect(
      within(dialog).queryByRole("button", { name: /add supporting file/i }),
    ).not.toBeInTheDocument();
  });

  it("shows the History section on the detail page", async () => {
    fetchKnowledge.mockResolvedValue({ data: knowledge({ status: "ACTIVE" }) });
    fetchKnowledgeHistory.mockResolvedValue({
      data: [
        {
          id: "h1",
          eventType: "KnowledgeCreated",
          action: "CREATE",
          actorId: "u1",
          actorName: "Admin Pusat",
          oldValues: null,
          newValues: { title: "SOP Penanganan Pengaduan" },
          createdAt: "2026-07-30T00:00:00Z",
        },
      ],
    });

    renderWithProviders(<KnowledgeDetailView id="f6666666-6666-6666-6666-666666666666" />);

    await screen.findByText("History");
    await waitFor(() => {
      expect(fetchKnowledgeHistory).toHaveBeenCalledWith(
        "f6666666-6666-6666-6666-666666666666",
      );
    });
    expect(await screen.findByText("Created")).toBeInTheDocument();
    expect(screen.getByText(/Admin Pusat/)).toBeInTheDocument();
  });
});
