/**
 * Root "/" entry-point gate (post-login unread-announcement redirect
 * milestone, §9/§10/§18/§20, LOCKED). Dashboard stays the app's default
 * home — this route only decides, once, whether to detour through
 * /announcements first when the caller has at least one unread active
 * announcement.
 */
import { cleanup, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";

const replace = vi.fn();
const fetchHasUnreadAnnouncements = vi.fn();
const hasPermission = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace, push: vi.fn(), back: vi.fn() }),
}));

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({ hasPermission, user: null }),
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchHasUnreadAnnouncements: (...args: unknown[]) =>
      fetchHasUnreadAnnouncements(...args),
  };
});

import EntryPointPage from "./page";

const READER_PERMS = ["announcement:read", "complaints:read"];

describe("EntryPointPage ('/', post-login unread gate)", () => {
  beforeEach(() => {
    replace.mockReset();
    fetchHasUnreadAnnouncements.mockReset();
    hasPermission.mockReset();
  });

  afterEach(() => {
    cleanup();
  });

  it("redirects to /dashboard when there is no unread active announcement", async () => {
    hasPermission.mockImplementation((code: string) => READER_PERMS.includes(code));
    fetchHasUnreadAnnouncements.mockResolvedValue({ data: false });

    renderWithProviders(<EntryPointPage />);

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/dashboard"));
    expect(fetchHasUnreadAnnouncements).toHaveBeenCalledWith();
    expect(replace).toHaveBeenCalledTimes(1);
  });

  it("redirects to /announcements when there is an unread active announcement", async () => {
    hasPermission.mockImplementation((code: string) => READER_PERMS.includes(code));
    fetchHasUnreadAnnouncements.mockResolvedValue({ data: true });

    renderWithProviders(<EntryPointPage />);

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/announcements"));
    expect(replace).toHaveBeenCalledTimes(1);
  });

  it("issues exactly one redirect for multiple unread announcements — no per-item bouncing", async () => {
    hasPermission.mockImplementation((code: string) => READER_PERMS.includes(code));
    // The endpoint is a single boolean regardless of how many are unread —
    // this test guards the frontend side: one fetch, one decision, one replace.
    fetchHasUnreadAnnouncements.mockResolvedValue({ data: true });

    renderWithProviders(<EntryPointPage />);

    await waitFor(() => expect(replace).toHaveBeenCalled());
    expect(fetchHasUnreadAnnouncements).toHaveBeenCalledTimes(1);
    expect(replace).toHaveBeenCalledTimes(1);
    expect(replace).toHaveBeenCalledWith("/announcements");
  });

  it("goes straight to /dashboard without an unread check for a caller without announcement:read", async () => {
    hasPermission.mockImplementation((code: string) => code === "complaints:read");

    renderWithProviders(<EntryPointPage />);

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/dashboard"));
    expect(fetchHasUnreadAnnouncements).not.toHaveBeenCalled();
  });

  it("fails open to /dashboard when the unread check errors", async () => {
    hasPermission.mockImplementation((code: string) => READER_PERMS.includes(code));
    fetchHasUnreadAnnouncements.mockRejectedValue(new Error("network"));

    renderWithProviders(<EntryPointPage />);

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/dashboard"));
  });
});
