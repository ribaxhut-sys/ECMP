/**
 * AnnouncementHistoryView — reader archive as a paginated list (default 10).
 * Read-only: never exposes Create/Edit/Publish/Unpublish/Delete.
 */
import { cleanup, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";

const fetchAnnouncementHistory = vi.fn();
const markAnnouncementRead = vi.fn();

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
    fetchAnnouncementHistory: (...args: unknown[]) => fetchAnnouncementHistory(...args),
    markAnnouncementRead: (...args: unknown[]) => markAnnouncementRead(...args),
  };
});

import { AnnouncementHistoryView } from "./AnnouncementHistoryView";

function announcement(overrides: Record<string, unknown> = {}) {
  return {
    id: "b2222222-2222-2222-2222-222222222222",
    referenceNumber: "PGM-2608-0001",
    title: "Jadwal Layanan Libur Nasional",
    body: "Layanan tutup sementara pada tanggal libur nasional berikutnya.",
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
    isRead: false,
    ...overrides,
  };
}

function historyTable() {
  return screen.getByRole("table", { name: /announcement history list/i });
}

describe("AnnouncementHistoryView", () => {
  beforeEach(() => {
    fetchAnnouncementHistory.mockReset();
    markAnnouncementRead.mockReset();
  });

  afterEach(() => {
    cleanup();
  });

  it("renders the archive as a list table, newest first", async () => {
    fetchAnnouncementHistory.mockResolvedValue({
      data: [announcement()],
    });

    renderWithProviders(<AnnouncementHistoryView />);

    await waitFor(() =>
      expect(
        within(historyTable()).getByText("Jadwal Layanan Libur Nasional"),
      ).toBeInTheDocument(),
    );
    expect(fetchAnnouncementHistory).toHaveBeenCalledWith();
  });

  it("defaults to 10 rows per page and lets the user change page size", async () => {
    const user = userEvent.setup();
    fetchAnnouncementHistory.mockResolvedValue({
      data: Array.from({ length: 12 }, (_, i) =>
        announcement({
          id: `00000000-0000-4000-8000-${String(i).padStart(12, "0")}`,
          title: `Announcement ${i + 1}`,
          publishedAt: `2026-08-${String(Math.max(1, 12 - i)).padStart(2, "0")}T00:00:00Z`,
        }),
      ),
    });

    renderWithProviders(<AnnouncementHistoryView />);

    await waitFor(() =>
      expect(within(historyTable()).getByText("Announcement 1")).toBeInTheDocument(),
    );
    expect(within(historyTable()).getByText("Announcement 10")).toBeInTheDocument();
    expect(within(historyTable()).queryByText("Announcement 11")).not.toBeInTheDocument();

    const pageSize = screen.getByLabelText(/show per page/i);
    await user.selectOptions(pageSize, "25");

    await waitFor(() =>
      expect(within(historyTable()).getByText("Announcement 11")).toBeInTheDocument(),
    );
    expect(within(historyTable()).getByText("Announcement 12")).toBeInTheDocument();
  });

  it("never marks anything read from the list — only opening the detail does that (§4, LOCKED)", async () => {
    fetchAnnouncementHistory.mockResolvedValue({ data: [announcement()] });

    renderWithProviders(<AnnouncementHistoryView />);

    await waitFor(() =>
      expect(
        within(historyTable()).getByText("Jadwal Layanan Libur Nasional"),
      ).toBeInTheDocument(),
    );
    expect(markAnnouncementRead).not.toHaveBeenCalled();
  });

  it("never renders manage-only controls (Create/Edit/Publish/Unpublish/Delete)", async () => {
    fetchAnnouncementHistory.mockResolvedValue({ data: [announcement()] });

    renderWithProviders(<AnnouncementHistoryView />);

    await waitFor(() =>
      expect(
        within(historyTable()).getByText("Jadwal Layanan Libur Nasional"),
      ).toBeInTheDocument(),
    );

    expect(screen.queryByRole("button", { name: /create announcement/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /^edit$/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /^publish$/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /^unpublish$/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /^delete$/i })).toBeNull();
  });

  it("does not show a status column in the history list", async () => {
    fetchAnnouncementHistory.mockResolvedValue({ data: [announcement()] });

    renderWithProviders(<AnnouncementHistoryView />);

    await waitFor(() =>
      expect(
        within(historyTable()).getByText("Jadwal Layanan Libur Nasional"),
      ).toBeInTheDocument(),
    );

    const table = historyTable();
    expect(within(table).queryByRole("columnheader", { name: /^status$/i })).toBeNull();
    expect(within(table).queryByText(/^published$/i)).toBeNull();
  });

  it("opens detail from the reference number and does not render a View action", async () => {
    fetchAnnouncementHistory.mockResolvedValue({ data: [announcement()] });

    renderWithProviders(<AnnouncementHistoryView />);

    await waitFor(() =>
      expect(
        within(historyTable()).getByRole("link", { name: "PGM-2608-0001" }),
      ).toHaveAttribute("href", "/announcements/b2222222-2222-2222-2222-222222222222"),
    );
    expect(within(historyTable()).queryByRole("link", { name: /^view$/i })).toBeNull();
    expect(
      within(historyTable()).queryByRole("columnheader", { name: /attachment count/i }),
    ).toBeNull();
  });

  it("shows a truncated body preview and a full published datetime", async () => {
    const longBody =
      "Berdasarkan pengumuman nomor 12 tentang pemeliharaan sistem layanan pengaduan yang akan dilaksanakan pada akhir pekan dan berdampak pada seluruh cabang.";
    fetchAnnouncementHistory.mockResolvedValue({
      data: [announcement({ body: longBody })],
    });

    renderWithProviders(<AnnouncementHistoryView />);

    await waitFor(() =>
      expect(within(historyTable()).getByText(/Berdasarkan pengumuman nomor 12/)).toBeInTheDocument(),
    );
    const preview = within(historyTable()).getByText(/Berdasarkan pengumuman nomor 12/);
    expect(preview.textContent).toMatch(/…$/);
    expect(preview.textContent?.length ?? 0).toBeLessThan(longBody.length);
    expect(within(historyTable()).getByText(/August 1, 2026/)).toBeInTheDocument();
  });

  it("uses bold for unread and regular for read, without read-status badges", async () => {
    fetchAnnouncementHistory.mockResolvedValue({
      data: [
        announcement({
          id: "11111111-1111-4111-8111-111111111111",
          title: "Belum dibaca",
          isRead: false,
        }),
        announcement({
          id: "22222222-2222-4222-8222-222222222222",
          title: "Sudah dibaca",
          isRead: true,
        }),
      ],
    });

    renderWithProviders(<AnnouncementHistoryView />);

    await waitFor(() =>
      expect(within(historyTable()).getByText("Belum dibaca")).toBeInTheDocument(),
    );
    const table = historyTable();
    expect(within(table).getByText("Belum dibaca")).toHaveClass("font-semibold");
    expect(within(table).getByText("Sudah dibaca")).toHaveClass("font-normal");
    expect(within(table).queryByText(/^unread$/i)).toBeNull();
    expect(within(table).queryByText(/^read$/i)).toBeNull();
    expect(markAnnouncementRead).not.toHaveBeenCalled();
  });

  it("filters to unread only when the checkbox is checked, and restores all when unchecked", async () => {
    const user = userEvent.setup();
    fetchAnnouncementHistory.mockResolvedValue({
      data: [
        announcement({
          id: "11111111-1111-4111-8111-111111111111",
          title: "Belum dibaca",
          isRead: false,
        }),
        announcement({
          id: "22222222-2222-4222-8222-222222222222",
          title: "Sudah dibaca",
          isRead: true,
        }),
      ],
    });

    renderWithProviders(<AnnouncementHistoryView />);

    await waitFor(() =>
      expect(within(historyTable()).getByText("Sudah dibaca")).toBeInTheDocument(),
    );

    const filter = screen.getByRole("checkbox", { name: /show unread only/i });
    expect(filter).not.toBeChecked();

    await user.click(filter);

    await waitFor(() =>
      expect(within(historyTable()).queryByText("Sudah dibaca")).not.toBeInTheDocument(),
    );
    expect(within(historyTable()).getByText("Belum dibaca")).toBeInTheDocument();
    expect(filter).toBeChecked();
    expect(markAnnouncementRead).not.toHaveBeenCalled();

    await user.click(filter);

    await waitFor(() =>
      expect(within(historyTable()).getByText("Sudah dibaca")).toBeInTheDocument(),
    );
    expect(filter).not.toBeChecked();
  });

  it("keeps the unread filter available when every announcement is already read", async () => {
    const user = userEvent.setup();
    fetchAnnouncementHistory.mockResolvedValue({
      data: [
        announcement({
          title: "Semua sudah dibaca",
          isRead: true,
        }),
      ],
    });

    renderWithProviders(<AnnouncementHistoryView />);

    await waitFor(() =>
      expect(within(historyTable()).getByText("Semua sudah dibaca")).toBeInTheDocument(),
    );

    await user.click(screen.getByRole("checkbox", { name: /show unread only/i }));

    await waitFor(() =>
      expect(screen.getByText("No unread announcements.")).toBeInTheDocument(),
    );
    expect(screen.queryByRole("table", { name: /announcement history list/i })).toBeNull();
    expect(
      screen.getByRole("checkbox", { name: /show unread only/i }),
    ).toBeChecked();
  });

  it("shows the empty state when the archive is empty", async () => {
    fetchAnnouncementHistory.mockResolvedValue({ data: [] });

    renderWithProviders(<AnnouncementHistoryView />);

    await waitFor(() => expect(screen.getByText("No announcements yet.")).toBeInTheDocument());
    expect(fetchAnnouncementHistory).toHaveBeenCalledWith();
  });

  it("paginates with previous/next when more than one page exists", async () => {
    const user = userEvent.setup();
    fetchAnnouncementHistory.mockResolvedValue({
      data: Array.from({ length: 11 }, (_, i) =>
        announcement({
          id: `00000000-0000-4000-9000-${String(i).padStart(12, "0")}`,
          title: `Row ${i + 1}`,
          publishedAt: `2026-08-${String(Math.max(1, 15 - i)).padStart(2, "0")}T00:00:00Z`,
        }),
      ),
    });

    renderWithProviders(<AnnouncementHistoryView />);

    await waitFor(() =>
      expect(within(historyTable()).getByText("Row 1")).toBeInTheDocument(),
    );
    expect(within(historyTable()).queryByText("Row 11")).not.toBeInTheDocument();

    const nav = screen.getByRole("navigation", { name: /pagination/i });
    await user.click(within(nav).getByRole("button", { name: /next/i }));

    await waitFor(() =>
      expect(within(historyTable()).getByText("Row 11")).toBeInTheDocument(),
    );
    expect(within(historyTable()).queryByText("Row 1")).not.toBeInTheDocument();
  });
});
