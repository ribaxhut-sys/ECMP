import { describe, expect, it, vi, beforeEach } from "vitest";
import { cleanup, render, screen, waitFor, act } from "@testing-library/react";
import { useCmWorkBadges } from "./useCmWorkBadges";
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
});
