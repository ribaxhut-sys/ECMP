import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { cleanup, render, screen, waitFor, act } from "@testing-library/react";
import {
  INTERNAL_INBOX_BADGE_POLL_MS,
  usePendingInboxCount,
} from "./usePendingInboxCount";
import { refreshInternalInboxBadges } from "./inboxBadgesSignal";

const fetchPendingInboxCount = vi.fn();

vi.mock("@/lib/api/internalComplaints", () => ({
  fetchPendingInboxCount: (...args: unknown[]) => fetchPendingInboxCount(...args),
}));

vi.mock("next/navigation", () => ({
  usePathname: () => "/internal",
}));

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({ hasPermission: () => true }),
}));

vi.mock("@/shared/config/internalComplaintsUi", () => ({
  isInternalComplaintsUiEnabled: () => true,
}));

function Probe() {
  const count = usePendingInboxCount();
  return <span data-testid="count">{count}</span>;
}

describe("usePendingInboxCount", () => {
  beforeEach(() => {
    cleanup();
    fetchPendingInboxCount.mockReset();
  });

  afterEach(() => {
    cleanup();
  });

  it("refetches when the same tab signals receive / return / resend", async () => {
    fetchPendingInboxCount
      .mockResolvedValueOnce({ data: 1 })
      .mockResolvedValueOnce({ data: 0 });

    render(<Probe />);
    await waitFor(() => expect(screen.getByTestId("count").textContent).toBe("1"));

    await act(async () => {
      refreshInternalInboxBadges();
    });

    await waitFor(() => expect(screen.getByTestId("count").textContent).toBe("0"));
    expect(fetchPendingInboxCount).toHaveBeenCalledTimes(2);
  });

  it("refetches when the receiving tab becomes visible again", async () => {
    fetchPendingInboxCount
      .mockResolvedValueOnce({ data: 0 })
      .mockResolvedValueOnce({ data: 2 });

    render(<Probe />);
    await waitFor(() => expect(screen.getByTestId("count").textContent).toBe("0"));

    await act(async () => {
      document.dispatchEvent(new Event("visibilitychange"));
    });

    await waitFor(() => expect(screen.getByTestId("count").textContent).toBe("2"));
    expect(fetchPendingInboxCount).toHaveBeenCalledTimes(2);
  });

  it("polls so the receiving login sees a resend without navigating", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    fetchPendingInboxCount
      .mockResolvedValueOnce({ data: 0 })
      .mockResolvedValueOnce({ data: 1 });

    render(<Probe />);
    await act(async () => {
      await Promise.resolve();
    });
    expect(screen.getByTestId("count").textContent).toBe("0");

    await act(async () => {
      vi.advanceTimersByTime(INTERNAL_INBOX_BADGE_POLL_MS);
      await Promise.resolve();
    });

    expect(screen.getByTestId("count").textContent).toBe("1");
    vi.useRealTimers();
  });

  it("hides the badge when the count request fails", async () => {
    fetchPendingInboxCount.mockRejectedValue(new Error("offline"));
    render(<Probe />);
    await waitFor(() => expect(screen.getByTestId("count").textContent).toBe("0"));
  });
});
