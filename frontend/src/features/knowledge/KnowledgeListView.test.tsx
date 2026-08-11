/**
 * KnowledgeListView — single shared list: every knowledge:read holder can
 * search/read; "+ Add" only renders for knowledge:manage (Pusat-proven).
 */
import { cleanup, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";

const searchKnowledge = vi.fn();
const hasPermission = vi.fn<(permission: string) => boolean>(() => false);
let mockRoles: string[] = [];
let mockOrgUnitCode: string | null = null;

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: vi.fn(), push: vi.fn(), back: vi.fn() }),
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
      const table = screen.getByRole("table", { name: /knowledge list/i });
      expect(within(table).getByText("SOP Penanganan Pengaduan")).toBeInTheDocument();
    });
    expect(searchKnowledge).toHaveBeenCalledWith(
      expect.objectContaining({ status: "ACTIVE" }),
    );
    expect(
      screen.queryByRole("button", { name: /\+ Add/i }),
    ).not.toBeInTheDocument();
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

  it("shows an empty state when there are no results", async () => {
    searchKnowledge.mockResolvedValue({ data: [] });

    renderWithProviders(<KnowledgeListView />);

    await waitFor(() => {
      expect(screen.getByText("No Knowledge yet")).toBeInTheDocument();
    });
  });
});
