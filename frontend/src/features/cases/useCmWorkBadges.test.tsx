import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { cleanup, render, screen, waitFor, act } from "@testing-library/react";
import { WORK_BADGES_POLL_MS, useCmWorkBadges } from "./useCmWorkBadges";
import { refreshWorkBadges } from "./workBadgesSignal";

const fetchCmWorkBadges = vi.fn();

vi.mock("@/lib/api", () => ({
  fetchCmWorkBadges: (...args: unknown[]) => fetchCmWorkBadges(...args),
}));

vi.mock("next/navigation", () => ({
  usePathname: () => "/complaints",
}));

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({ hasPermission: () => true }),
}));

function Probe() {
  const { pusatQueue } = useCmWorkBadges();
  return <span data-testid="queue">{pusatQueue}</span>;
}

describe("useCmWorkBadges", () => {
  beforeEach(() => {
    cleanup();
    fetchCmWorkBadges.mockReset();
  });

  afterEach(() => {
    cleanup();
  });

  it("refetches when a detail view signals it has been read", async () => {
    fetchCmWorkBadges
      .mockResolvedValueOnce({ data: { unreadCases: 0, pusatQueue: 2 } })
      .mockResolvedValueOnce({ data: { unreadCases: 0, pusatQueue: 1 } });

    render(<Probe />);
    await waitFor(() => expect(screen.getByTestId("queue").textContent).toBe("2"));

    await act(async () => {
      refreshWorkBadges();
    });

    await waitFor(() => expect(screen.getByTestId("queue").textContent).toBe("1"));
    expect(fetchCmWorkBadges).toHaveBeenCalledTimes(2);
  });

  it("hides the count when the badge request fails", async () => {
    fetchCmWorkBadges.mockRejectedValue(new Error("offline"));

    render(<Probe />);
    await waitFor(() => expect(screen.getByTestId("queue").textContent).toBe("0"));
  });

  it("exposes Cabang HQ schedule unread", async () => {
    fetchCmWorkBadges.mockResolvedValue({
      data: { unreadCases: 1, pusatQueue: 0, hqScheduleUnread: 4 },
    });

    function HqProbe() {
      const { hqScheduleUnread } = useCmWorkBadges();
      return <span data-testid="hq">{hqScheduleUnread}</span>;
    }

    render(<HqProbe />);
    await waitFor(() => expect(screen.getByTestId("hq").textContent).toBe("4"));
  });

  it("refetches when the receiving tab becomes visible again", async () => {
    fetchCmWorkBadges
      .mockResolvedValueOnce({ data: { unreadCases: 0, pusatQueue: 0 } })
      .mockResolvedValueOnce({ data: { unreadCases: 0, pusatQueue: 3 } });

    render(<Probe />);
    await waitFor(() => expect(screen.getByTestId("queue").textContent).toBe("0"));

    await act(async () => {
      document.dispatchEvent(new Event("visibilitychange"));
    });

    await waitFor(() => expect(screen.getByTestId("queue").textContent).toBe("3"));
    expect(fetchCmWorkBadges).toHaveBeenCalledTimes(2);
  });

  it("polls so login Pusat sees a Cabang resend without navigating", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    fetchCmWorkBadges
      .mockResolvedValueOnce({ data: { unreadCases: 0, pusatQueue: 0 } })
      .mockResolvedValueOnce({ data: { unreadCases: 0, pusatQueue: 1 } });

    render(<Probe />);
    await act(async () => {
      await Promise.resolve();
    });
    expect(screen.getByTestId("queue").textContent).toBe("0");

    await act(async () => {
      vi.advanceTimersByTime(WORK_BADGES_POLL_MS);
      await Promise.resolve();
    });

    expect(screen.getByTestId("queue").textContent).toBe("1");
    vi.useRealTimers();
  });
});
