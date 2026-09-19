/**
 * /announcements — always the read-only history list (Option B).
 */
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("@/features/announcements", () => ({
  AnnouncementHistoryView: () => <div data-testid="history-view" />,
  AnnouncementManagement: () => <div data-testid="management-view" />,
}));

import AnnouncementsHistoryPage from "./page";

describe("AnnouncementsHistoryPage", () => {
  afterEach(() => {
    cleanup();
  });

  it("always renders the history archive (manage is a separate route)", () => {
    render(<AnnouncementsHistoryPage />);
    expect(screen.getByTestId("history-view")).toBeInTheDocument();
    expect(screen.queryByTestId("management-view")).not.toBeInTheDocument();
  });
});
