/**
 * KnowledgeListView — single shared list: every knowledge:read holder can
 * search/read; "+ Add" only renders for knowledge:manage (Pusat-proven).
 */
import { cleanup, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";

const searchKnowledge = vi.fn();
const createKnowledge = vi.fn();
const uploadKnowledgeFile = vi.fn();
const push = vi.fn();
const hasPermission = vi.fn<(permission: string) => boolean>(() => false);
let mockRoles: string[] = [];
let mockOrgUnitCode: string | null = null;

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: vi.fn(), push, back: vi.fn() }),
}));

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({
    hasPermission,
    user: null,
    roles: mockRoles,
    status: "authenticated",
  }),
}));

vi.mock("@/features/announcements/useOrgUnitCode", () => ({
  useOrgUnitCode: () => mockOrgUnitCode,
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    searchKnowledge: (...args: unknown[]) => searchKnowledge(...args),
    createKnowledge: (...args: unknown[]) => createKnowledge(...args),
    uploadKnowledgeFile: (...args: unknown[]) => uploadKnowledgeFile(...args),
  };
});

import { KnowledgeListView } from "./KnowledgeListView";

function knowledge(overrides: Record<string, unknown> = {}) {
  return {
    id: "d4444444-4444-4444-4444-444444444444",
    title: "SOP Penanganan Pengaduan",
    knowledgeType: "SOP",
    status: "ACTIVE",
    documentNumber: "SOP-001",
    summary: "Ringkasan prosedur.",
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

describe("KnowledgeListView", () => {
  beforeEach(() => {
    searchKnowledge.mockReset();
    createKnowledge.mockReset();
    uploadKnowledgeFile.mockReset();
    push.mockReset();
    hasPermission.mockReset().mockReturnValue(false);
    mockRoles = [];
    mockOrgUnitCode = null;
  });

  afterEach(() => {
    cleanup();
  });

  it("renders ACTIVE Knowledge for a read-only holder without the Add button", async () => {
    searchKnowledge.mockResolvedValue({ data: [knowledge()] });

    renderWithProviders(<KnowledgeListView />);

    await waitFor(() => {
      const list = screen.getByRole("list", { name: /knowledge list/i });
      expect(within(list).getByText("SOP Penanganan Pengaduan")).toBeInTheDocument();
    });
    expect(screen.getByText(/effective/i)).toBeInTheDocument();
    expect(screen.getByText(/uploaded/i)).toBeInTheDocument();
    expect(searchKnowledge).toHaveBeenCalledWith(
      expect.objectContaining({ status: "ACTIVE" }),
    );
    expect(
      screen.queryByRole("button", { name: /\+ Add/i }),
    ).not.toBeInTheDocument();
  });

  it("shows inactive date for archived Knowledge", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [] });

    renderWithProviders(<KnowledgeListView />);
    await waitFor(() => {
      expect(searchKnowledge).toHaveBeenCalled();
    });

    searchKnowledge.mockResolvedValue({
      data: [
        knowledge({
          status: "ARCHIVED",
          effectiveFrom: "2026-01-01T00:00:00Z",
          effectiveTo: "2026-08-10T00:00:00Z",
        }),
      ],
    });
    await user.selectOptions(screen.getByLabelText(/^status$/i), "ARCHIVED");

    await waitFor(() => {
      expect(screen.getByText(/inactive/i)).toBeInTheDocument();
    });
  });

  it("orders rows by newest uploadedAt first even if the API is unsorted", async () => {
    searchKnowledge.mockResolvedValue({
      data: [
        knowledge({
          id: "old",
          title: "Older Knowledge",
          createdAt: "2026-07-01T00:00:00Z",
        }),
        knowledge({
          id: "new",
          title: "Newer Knowledge",
          createdAt: "2026-08-11T00:00:00Z",
        }),
      ],
    });

    renderWithProviders(<KnowledgeListView />);
    const list = await screen.findByRole("list", { name: /knowledge list/i });
    await waitFor(() => {
      expect(within(list).getByText("Newer Knowledge")).toBeInTheDocument();
    });
    const titles = within(list)
      .getAllByRole("listitem")
      .map((item) => item.textContent ?? "");
    const newerIdx = titles.findIndex((text) => text.includes("Newer Knowledge"));
    const olderIdx = titles.findIndex((text) => text.includes("Older Knowledge"));
    expect(newerIdx).toBeGreaterThanOrEqual(0);
    expect(olderIdx).toBeGreaterThanOrEqual(0);
    expect(newerIdx).toBeLessThan(olderIdx);
  });

  it("shows the Add button for a knowledge:manage Pusat Admin", async () => {
    hasPermission.mockImplementation((perm: string) => perm === "knowledge:manage");
    mockRoles = ["ADMIN"];
    mockOrgUnitCode = null;
    searchKnowledge.mockResolvedValue({ data: [] });

    renderWithProviders(<KnowledgeListView />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /\+ Add/i })).toBeInTheDocument();
    });
  });

  it("uploads staged primary and supporting files right after create succeeds", async () => {
    const user = userEvent.setup();
    hasPermission.mockImplementation((perm: string) => perm === "knowledge:manage");
    mockRoles = ["ADMIN"];
    searchKnowledge.mockResolvedValue({ data: [] });
    createKnowledge.mockResolvedValue({
      data: knowledge({ id: "new-knowledge-id", status: "DRAFT" }),
    });
    uploadKnowledgeFile.mockResolvedValue({ data: knowledge({ id: "new-knowledge-id" }) });

    renderWithProviders(<KnowledgeListView />);
    await user.click(await screen.findByRole("button", { name: /\+ Add/i }));
    const dialog = await screen.findByRole("dialog");

    // Title Input has no distinct id/name, so it shares the generic default
    // id with the page's own Search field once both are mounted at once —
    // querying by role avoids the resulting id collision.
    await user.type(within(dialog).getAllByRole("textbox")[0], "SOP Baru");

    const primaryFile = new File(["a"], "sop-utama.pdf", { type: "application/pdf" });
    const supportingFile = new File(["b"], "lampiran.pdf", { type: "application/pdf" });
    const fileInput = within(dialog).getByLabelText(/upload file/i);
    await user.upload(fileInput, [primaryFile, supportingFile]);

    expect(within(dialog).getByText("sop-utama.pdf")).toBeInTheDocument();
    expect(within(dialog).getByText("lampiran.pdf")).toBeInTheDocument();

    await user.click(within(dialog).getByRole("button", { name: /^save$/i }));

    await waitFor(() => {
      expect(createKnowledge).toHaveBeenCalledWith(
        expect.objectContaining({ title: "SOP Baru" }),
      );
    });
    await waitFor(() => {
      expect(uploadKnowledgeFile).toHaveBeenCalledWith(
        "new-knowledge-id",
        primaryFile,
        "PRIMARY",
      );
      expect(uploadKnowledgeFile).toHaveBeenCalledWith(
        "new-knowledge-id",
        supportingFile,
        "SUPPORTING",
      );
    });
    await waitFor(() => {
      expect(push).toHaveBeenCalledWith("/knowledge/new-knowledge-id");
    });
  });

  it("shows one row per file for a record with two files, repeating the title", async () => {
    searchKnowledge.mockResolvedValue({
      data: [
        knowledge({
          files: [
            {
              id: "f-primary",
              fileName: "Panduan_Membuat_Pengaduan.docx",
              mimeType:
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
              sizeBytes: 37984,
              role: "PRIMARY",
              createdAt: "2026-08-01T00:00:00Z",
            },
            {
              id: "f-supporting",
              fileName: "Panduan_Peran_Pengguna.docx",
              mimeType:
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
              sizeBytes: 36662,
              role: "SUPPORTING",
              createdAt: "2026-08-01T00:00:00Z",
            },
          ],
        }),
      ],
    });

    renderWithProviders(<KnowledgeListView />);
    // Desktop table and the mobile stacked-card fallback both render at
    // once in jsdom (only CSS breakpoints tell them apart) — scope to one
    // tree, the same way the "orders rows" test above does, so counts stay
    // exact instead of doubled.
    const list = await screen.findByRole("list", { name: /knowledge list/i });

    await waitFor(() => {
      expect(within(list).getByText("Panduan_Membuat_Pengaduan.docx")).toBeInTheDocument();
    });
    expect(within(list).getByText("Panduan_Peran_Pengguna.docx")).toBeInTheDocument();
    // Same record, same title — repeated once per file row.
    expect(within(list).getAllByText("SOP Penanganan Pengaduan")).toHaveLength(2);
  });

  it("opens the file in a new tab from the Buka column without navigating to the detail page", async () => {
    const user = userEvent.setup();
    const openSpy = vi.spyOn(window, "open").mockReturnValue({} as Window);
    searchKnowledge.mockResolvedValue({
      data: [
        knowledge({
          files: [
            {
              id: "f-primary",
              fileName: "sop.pdf",
              mimeType: "application/pdf",
              sizeBytes: 1024,
              role: "PRIMARY",
              createdAt: "2026-08-01T00:00:00Z",
            },
          ],
        }),
      ],
    });

    renderWithProviders(<KnowledgeListView />);
    const list = await screen.findByRole("list", { name: /knowledge list/i });
    await waitFor(() => {
      expect(within(list).getByText("sop.pdf")).toBeInTheDocument();
    });

    await user.click(within(list).getByRole("button", { name: /open in new tab/i }));

    expect(openSpy).toHaveBeenCalledWith(
      "/attachments/f-primary/preview",
      "_blank",
      "noopener,noreferrer",
    );
    // The row itself is also clickable (goes to the detail page) — clicking
    // the Buka button must not also trigger that navigation.
    expect(push).not.toHaveBeenCalled();

    openSpy.mockRestore();
  });

  it("shows an empty state when there are no results", async () => {
    searchKnowledge.mockResolvedValue({ data: [] });

    renderWithProviders(<KnowledgeListView />);

    await waitFor(() => {
      expect(screen.getByText("No Knowledge yet")).toBeInTheDocument();
    });
  });

  describe("pagination", () => {
    function manyKnowledge(count: number) {
      return Array.from({ length: count }, (_, i) =>
        knowledge({
          id: `k-${String(i + 1).padStart(3, "0")}`,
          title: `Knowledge ${String(i + 1).padStart(3, "0")}`,
          // Newest first after catalog sort: item 001 uploaded last.
          createdAt: new Date(Date.UTC(2026, 7, 11, 12, 0, 0) - i * 60_000).toISOString(),
        }),
      );
    }

    it("shows only the first page (10 rows) and reports the total", async () => {
      searchKnowledge.mockResolvedValue({ data: manyKnowledge(25) });

      renderWithProviders(<KnowledgeListView />);

      const list = await screen.findByRole("list", { name: /knowledge list/i });
      await waitFor(() => {
        expect(within(list).getByText("Knowledge 001")).toBeInTheDocument();
      });
      expect(within(list).getByText("Knowledge 010")).toBeInTheDocument();
      expect(within(list).queryByText("Knowledge 011")).not.toBeInTheDocument();
      expect(screen.getByText("Showing 1–10 of 25")).toBeInTheDocument();
    });

    it("moves to the next page and back", async () => {
      const user = userEvent.setup();
      searchKnowledge.mockResolvedValue({ data: manyKnowledge(25) });

      renderWithProviders(<KnowledgeListView />);
      const list = await screen.findByRole("list", { name: /knowledge list/i });
      await waitFor(() => {
        expect(within(list).getByText("Knowledge 001")).toBeInTheDocument();
      });

      await user.click(screen.getByRole("button", { name: /next/i }));

      await waitFor(() => {
        expect(within(list).getByText("Knowledge 011")).toBeInTheDocument();
      });
      expect(within(list).queryByText("Knowledge 001")).not.toBeInTheDocument();
      expect(screen.getByText("Showing 11–20 of 25")).toBeInTheDocument();

      await user.click(screen.getByRole("button", { name: /previous/i }));

      await waitFor(() => {
        expect(within(list).getByText("Knowledge 001")).toBeInTheDocument();
      });
    });

    it("disables Previous on the first page and Next on the last page", async () => {
      const user = userEvent.setup();
      searchKnowledge.mockResolvedValue({ data: manyKnowledge(15) });

      renderWithProviders(<KnowledgeListView />);
      await screen.findByRole("list", { name: /knowledge list/i });

      expect(screen.getByRole("button", { name: /previous/i })).toBeDisabled();
      expect(screen.getByRole("button", { name: /next/i })).toBeEnabled();

      await user.click(screen.getByRole("button", { name: /next/i }));

      await waitFor(() => {
        expect(screen.getByRole("button", { name: /next/i })).toBeDisabled();
      });
      expect(screen.getByRole("button", { name: /previous/i })).toBeEnabled();
    });

    it("changing page size re-pages from page 1", async () => {
      const user = userEvent.setup();
      searchKnowledge.mockResolvedValue({ data: manyKnowledge(30) });

      renderWithProviders(<KnowledgeListView />);
      const list = await screen.findByRole("list", { name: /knowledge list/i });
      await waitFor(() => {
        expect(within(list).getByText("Knowledge 001")).toBeInTheDocument();
      });

      await user.click(screen.getByRole("button", { name: /next/i }));
      await waitFor(() => {
        expect(screen.getByText("Showing 11–20 of 30")).toBeInTheDocument();
      });

      await user.selectOptions(screen.getByLabelText(/per page/i), "25");

      await waitFor(() => {
        expect(screen.getByText("Showing 1–25 of 30")).toBeInTheDocument();
      });
      expect(within(list).getByText("Knowledge 001")).toBeInTheDocument();
    });

    it("hides pagination chrome when a single page covers every row", async () => {
      searchKnowledge.mockResolvedValue({ data: manyKnowledge(3) });

      renderWithProviders(<KnowledgeListView />);
      await screen.findByRole("list", { name: /knowledge list/i });

      expect(screen.getByText("Showing 1–3 of 3")).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /previous/i })).toBeDisabled();
      expect(screen.getByRole("button", { name: /next/i })).toBeDisabled();
    });
  });
});
