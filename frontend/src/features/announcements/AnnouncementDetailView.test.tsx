/**
 * AnnouncementDetailView — mark-read wiring (post-login unread-redirect
 * milestone, §4/§8, LOCKED). Read state is set when the reader opens the
 * *detail*, never from the list — verified elsewhere (AnnouncementHistoryView
 * has no mark-read call at all). This only proves the detail view fires it
 * exactly once per successful load, best-effort (a failure never blocks the
 * page or surfaces to the user).
 */
import { cleanup, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";

const fetchAnnouncement = vi.fn();
const markAnnouncementRead = vi.fn();
const hasPermission = vi.fn(() => false);
let mockSearchParams = new URLSearchParams();
let mockRoles: string[] = [];
let mockOrgUnitCode: string | null = null;

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: vi.fn(), push: vi.fn(), back: vi.fn() }),
  useSearchParams: () => mockSearchParams,
}));

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({
    hasPermission,
    user: null,
    roles: mockRoles,
    status: "authenticated",
  }),
}));

vi.mock("./useOrgUnitCode", () => ({
  useOrgUnitCode: () => mockOrgUnitCode,
}));

vi.mock("@/shared/i18n", async () => {
  const actual = await vi.importActual<typeof import("@/shared/i18n")>("@/shared/i18n");
  return {
    ...actual,
    useLocaleContext: () => ({ locale: "en", setLocale: vi.fn(), ready: true }),
  };
});

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchAnnouncement: (...args: unknown[]) => fetchAnnouncement(...args),
    markAnnouncementRead: (...args: unknown[]) => markAnnouncementRead(...args),
  };
});

import { AnnouncementDetailView } from "./AnnouncementDetailView";

const ANNOUNCEMENT_ID = "c3333333-3333-3333-3333-333333333333";

function announcement(overrides: Record<string, unknown> = {}) {
  return {
    id: ANNOUNCEMENT_ID,
    referenceNumber: "PGM-2608-0001",
    title: "Pemeliharaan Sistem",
    body: "Sistem akan pemeliharaan pukul 22:00.",
    priority: "NORMAL",
    status: "PUBLISHED",
    effectiveStatus: "PUBLISHED",
    startAt: null,
    endAt: null,
    publishedAt: "2026-08-01T00:00:00Z",
    createdAt: "2026-07-30T00:00:00Z",
    createdBy: null,
    attachmentCount: 0,
    attachments: [],
    ...overrides,
  };
}

describe("AnnouncementDetailView — mark-read", () => {
  beforeEach(() => {
    fetchAnnouncement.mockReset();
    markAnnouncementRead.mockReset().mockResolvedValue(undefined);
    hasPermission.mockReset().mockReturnValue(false);
    mockSearchParams = new URLSearchParams();
    mockRoles = [];
    mockOrgUnitCode = null;
  });

  afterEach(() => {
    cleanup();
  });

  it("marks the announcement read once the detail finishes loading", async () => {
    fetchAnnouncement.mockResolvedValue({ data: announcement() });

    renderWithProviders(<AnnouncementDetailView id={ANNOUNCEMENT_ID} />);

    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Pemeliharaan Sistem" })).toBeInTheDocument(),
    );
    await waitFor(() => expect(markAnnouncementRead).toHaveBeenCalledWith(ANNOUNCEMENT_ID));
  });

  it("does not call mark-read when the detail fails to load", async () => {
    fetchAnnouncement.mockRejectedValue(new Error("not found"));

    renderWithProviders(<AnnouncementDetailView id={ANNOUNCEMENT_ID} />);

    await waitFor(() => expect(fetchAnnouncement).toHaveBeenCalled());
    expect(markAnnouncementRead).not.toHaveBeenCalled();
  });

  it("shows manage actions when opened from pengelolaan with manage gate", async () => {
    mockSearchParams = new URLSearchParams("from=manage");
    mockRoles = ["ADMIN"];
    mockOrgUnitCode = null;
    hasPermission.mockImplementation((...args: unknown[]) => {
      return args[0] === "announcement:manage";
    });
    fetchAnnouncement.mockResolvedValue({ data: announcement() });

    renderWithProviders(<AnnouncementDetailView id={ANNOUNCEMENT_ID} />);

    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Pemeliharaan Sistem" })).toBeInTheDocument(),
    );
    expect(screen.getByRole("button", { name: /^edit$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^unpublish$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^delete$/i })).toBeInTheDocument();
  });

  it("hides manage actions for history readers", async () => {
    fetchAnnouncement.mockResolvedValue({ data: announcement() });

    renderWithProviders(<AnnouncementDetailView id={ANNOUNCEMENT_ID} />);

    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Pemeliharaan Sistem" })).toBeInTheDocument(),
    );
    expect(screen.queryByRole("button", { name: /^edit$/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /^unpublish$/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /^delete$/i })).toBeNull();
  });
});
