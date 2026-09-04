/**
 * KnowledgeDetailView — Edit modal embeds Documents so a knowledge:manage
 * holder can replace files without leaving the modal (DRAFT only, KM §17/§23).
 * ACTIVE/ARCHIVED records stay identity-locked; correction goes through
 * "Create replacement version" (new DRAFT with supersedesKnowledgeId).
 */
import { cleanup, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import type { Knowledge } from "@/lib/api/types";

const fetchKnowledge = vi.fn();
const fetchKnowledgeHistory = vi.fn();
const createKnowledge = vi.fn();
const uploadKnowledgeFile = vi.fn();
const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push, replace: vi.fn(), back: vi.fn() }),
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
    createKnowledge: (...args: unknown[]) => createKnowledge(...args),
    uploadKnowledgeFile: (...args: unknown[]) => uploadKnowledgeFile(...args),
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
    editable: true,
    editableUntil: null,
    files: [],
    pinned: false,
    ...overrides,
  };
}

describe("KnowledgeDetailView — Edit modal Documents section", () => {
  beforeEach(() => {
    fetchKnowledge.mockReset();
    fetchKnowledgeHistory.mockReset();
    createKnowledge.mockReset();
    uploadKnowledgeFile.mockReset();
    push.mockReset();
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
      within(dialog).getByRole("button", { name: /upload file/i }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /create replacement version/i }),
    ).not.toBeInTheDocument();
  });

  it("lets a manager keep uploading files on an ACTIVE record inside the edit window (DEC-030)", async () => {
    const user = userEvent.setup();
    fetchKnowledge.mockResolvedValue({
      data: knowledge({
        status: "ACTIVE",
        editable: true,
        editableUntil: "2026-08-01T00:00:00Z",
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
    expect(within(dialog).getByRole("button", { name: /^add file$/i })).toBeInTheDocument();
  });

  it("shows the Documents list read-only once the ACTIVE record's edit window has closed", async () => {
    fetchKnowledge.mockResolvedValue({
      data: knowledge({
        status: "ACTIVE",
        editable: false,
        editableUntil: "2026-07-30T00:00:00Z",
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

    // Edit is disabled outright once locked — no point opening a dead form.
    expect(await screen.findByRole("button", { name: /^edit$/i })).toBeDisabled();

    expect(screen.getAllByText("sop-utama.pdf").length).toBeGreaterThan(0);
    expect(screen.queryByRole("button", { name: /upload file/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^add file$/i })).not.toBeInTheDocument();
    expect(screen.getAllByText(/edit window has closed/i).length).toBeGreaterThan(0);
    expect(
      screen.getByRole("button", { name: /create replacement version/i }),
    ).toBeInTheDocument();
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

describe("KnowledgeDetailView — replacement version", () => {
  beforeEach(() => {
    fetchKnowledge.mockReset();
    fetchKnowledgeHistory.mockReset();
    createKnowledge.mockReset();
    uploadKnowledgeFile.mockReset();
    push.mockReset();
    fetchKnowledgeHistory.mockResolvedValue({ data: [] });
  });

  afterEach(() => {
    cleanup();
  });

  it("opens a replacement form prefilled from the ACTIVE record with unlocked identity fields", async () => {
    const user = userEvent.setup();
    fetchKnowledge.mockResolvedValue({ data: knowledge({ status: "ACTIVE" }) });

    renderWithProviders(<KnowledgeDetailView id="f6666666-6666-6666-6666-666666666666" />);

    await user.click(
      await screen.findByRole("button", { name: /create replacement version/i }),
    );
    const dialog = await screen.findByRole("dialog");

    expect(within(dialog).getByText(/the new draft will supersede/i)).toBeInTheDocument();
    const title = within(dialog).getByDisplayValue("SOP Penanganan Pengaduan");
    expect(title).not.toBeDisabled();
    expect(within(dialog).getByRole("button", { name: /upload file/i })).toBeInTheDocument();
  });

  it("creates a draft that supersedes the current record", async () => {
    const user = userEvent.setup();
    fetchKnowledge.mockResolvedValue({ data: knowledge({ status: "ACTIVE" }) });
    createKnowledge.mockResolvedValue({
      data: knowledge({
        id: "a1111111-1111-1111-1111-111111111111",
        status: "DRAFT",
        title: "SOP judul benar",
        supersedesKnowledgeId: "f6666666-6666-6666-6666-666666666666",
        supersedesTitle: "SOP Penanganan Pengaduan",
      }),
    });

    renderWithProviders(<KnowledgeDetailView id="f6666666-6666-6666-6666-666666666666" />);

    await user.click(
      await screen.findByRole("button", { name: /create replacement version/i }),
    );
    const dialog = await screen.findByRole("dialog");
    const title = within(dialog).getByDisplayValue("SOP Penanganan Pengaduan");
    await user.clear(title);
    await user.type(title, "SOP judul benar");
    await user.click(within(dialog).getByRole("button", { name: /^save$/i }));

    await waitFor(() => {
      expect(createKnowledge).toHaveBeenCalledWith(
        expect.objectContaining({
          title: "SOP judul benar",
          knowledgeType: "SOP",
          supersedesKnowledgeId: "f6666666-6666-6666-6666-666666666666",
        }),
      );
    });
    expect(push).toHaveBeenCalledWith(
      "/knowledge/a1111111-1111-1111-1111-111111111111",
    );
  });

  it("shows a reminder banner on a replacement draft", async () => {
    fetchKnowledge.mockResolvedValue({
      data: knowledge({
        status: "DRAFT",
        supersedesKnowledgeId: "f6666666-6666-6666-6666-666666666666",
        supersedesTitle: "SOP lama",
      }),
    });

    renderWithProviders(<KnowledgeDetailView id="a1111111-1111-1111-1111-111111111111" />);

    expect(await screen.findByText("Replacement version")).toBeInTheDocument();
    expect(screen.getByText(/this draft supersedes "SOP lama"/i)).toBeInTheDocument();
  });
});
