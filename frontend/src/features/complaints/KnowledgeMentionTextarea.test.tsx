/**
 * KnowledgeMentionTextarea — `@` autocomplete (Option A: inline chips).
 * Outermost picker: Pengetahuan / Pengumuman / Lampiran, then per-source flow.
 */
import { useState } from "react";
import { cleanup, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import type { Announcement, AnnouncementAttachmentLibraryItem, Knowledge } from "@/lib/api/types";

const searchKnowledge = vi.fn();
const fetchKnowledge = vi.fn();
const fetchKnowledgeTypeCounts = vi.fn();
const fetchActiveAnnouncements = vi.fn();
const fetchAnnouncementAttachmentLibrary = vi.fn();
const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    searchKnowledge: (...args: unknown[]) => searchKnowledge(...args),
    fetchKnowledge: (...args: unknown[]) => fetchKnowledge(...args),
    fetchKnowledgeTypeCounts: (...args: unknown[]) =>
      fetchKnowledgeTypeCounts(...args),
    fetchActiveAnnouncements: (...args: unknown[]) =>
      fetchActiveAnnouncements(...args),
    fetchAnnouncementAttachmentLibrary: (...args: unknown[]) =>
      fetchAnnouncementAttachmentLibrary(...args),
  };
});

import { KnowledgeMentionTextarea } from "./KnowledgeMentionTextarea";

function knowledge(overrides: Partial<Knowledge> = {}): Knowledge {
  return {
    id: "e5555555-5555-5555-5555-555555555555",
    title: "SOP Penanganan Pengaduan",
    knowledgeType: "SOP",
    status: "ACTIVE",
    documentNumber: "SOP-001",
    summary: null,
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
    editable: true,
    editableUntil: null,
    files: [],
    ...overrides,
  };
}

function announcement(overrides: Partial<Announcement> = {}): Announcement {
  return {
    id: "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
    referenceNumber: "PGM-2608-0001",
    title: "Libur Nasional",
    body: "Kantor tutup.",
    priority: "NORMAL",
    status: "PUBLISHED",
    effectiveStatus: "PUBLISHED",
    startAt: null,
    endAt: null,
    publishedAt: "2026-08-01T00:00:00Z",
    publishedBy: null,
    createdBy: null,
    createdAt: "2026-07-30T00:00:00Z",
    updatedBy: null,
    updatedAt: "2026-07-30T00:00:00Z",
    attachments: [],
    attachmentCount: 0,
    ...overrides,
  };
}

function libraryFile(
  overrides: Partial<AnnouncementAttachmentLibraryItem> = {},
): AnnouncementAttachmentLibraryItem {
  return {
    id: "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
    fileName: "Formulir Klaim.pdf",
    mimeType: "application/pdf",
    sizeBytes: 1024,
    createdAt: "2026-07-30T00:00:00Z",
    accessLevel: "PUBLIC",
    uploadedOrgUnitId: "PUSAT",
    uploadedBy: null,
    uploadedByName: null,
    usageCount: 0,
    ...overrides,
  };
}

function Harness({
  onValue,
  initialValue = "",
}: {
  onValue?: (value: string) => void;
  initialValue?: string;
}) {
  const [value, setValue] = useState(initialValue);
  return (
    <KnowledgeMentionTextarea
      label="Catatan Penyelesaian"
      value={value}
      onChange={(next) => {
        setValue(next);
        onValue?.(next);
      }}
    />
  );
}

/** Types `@` and picks "Knowledge" from the outermost source picker, landing
 * on the pre-existing type-picker flow (SOP…Panduan). */
async function openKnowledgeTypePicker(
  user: ReturnType<typeof userEvent.setup>,
  editor: HTMLElement,
  extra = "",
) {
  await user.click(editor);
  await user.keyboard(`Sesuai @${extra}`);
  await screen.findByRole("option", { name: /^Knowledge/ });
  await user.click(screen.getByRole("option", { name: /^Knowledge/ }));
}

describe("KnowledgeMentionTextarea", () => {
  beforeEach(() => {
    searchKnowledge.mockReset();
    fetchKnowledge.mockReset();
    fetchKnowledgeTypeCounts.mockReset();
    fetchActiveAnnouncements.mockReset();
    fetchAnnouncementAttachmentLibrary.mockReset();
    fetchKnowledgeTypeCounts.mockResolvedValue({
      data: {
        SOP: 23,
        PERATURAN: 90,
        SURAT_EDARAN: 12,
        KEPUTUSAN: 4,
        PANDUAN: 0,
      },
    });
    fetchKnowledge.mockResolvedValue({
      data: knowledge({ status: "ACTIVE" }),
    });
    fetchActiveAnnouncements.mockResolvedValue({ data: [] });
    fetchAnnouncementAttachmentLibrary.mockResolvedValue({ data: [] });
    push.mockReset();
  });

  afterEach(() => {
    cleanup();
  });

  it("shows the 3-source picker (Pengetahuan/Pengumuman/Lampiran) on a bare @", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await user.click(editor);
    await user.keyboard("Sesuai @");

    await waitFor(() => {
      expect(screen.getByText("Choose a source")).toBeInTheDocument();
    });
    expect(screen.getByRole("option", { name: /^Knowledge/ })).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: /^Announcement/ }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: /^Attachment/ }),
    ).toBeInTheDocument();
    expect(searchKnowledge).not.toHaveBeenCalled();
    // The outer picker fetches counts (not search results) for all 3
    // sources up front, so it can show "Announcement (3)" etc.
    expect(fetchActiveAnnouncements).toHaveBeenCalled();
    expect(fetchAnnouncementAttachmentLibrary).toHaveBeenCalled();
  });

  it("typing after a bare @ does not fall through — the source picker stays", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await user.click(editor);
    await user.keyboard("Sesuai @pengaduan");

    await waitFor(() => {
      expect(screen.getByText("Choose a source")).toBeInTheDocument();
    });
    expect(searchKnowledge).not.toHaveBeenCalled();
  });

  it("removes the bare @ from the text when Escape is pressed on the source picker", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await user.click(editor);
    await user.keyboard("Sesuai @");
    await screen.findByText("Choose a source");

    await user.keyboard("{Escape}");

    await waitFor(() => {
      expect(screen.queryByText("Choose a source")).not.toBeInTheDocument();
    });
    expect(editor.textContent).toBe("Sesuai ");
    expect(editor.textContent).not.toContain("@");
  });

  it("shows the type picker (SOP…Panduan) after choosing Knowledge as the source", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await openKnowledgeTypePicker(user, editor);

    await waitFor(() => {
      expect(screen.getByText(/Choose type/i)).toBeInTheDocument();
      expect(screen.getByRole("option", { name: /SOP \(23\)/i })).toBeInTheDocument();
    });
    expect(
      screen.getByRole("option", { name: /Peraturan \(90\)|Regulation \(90\)/i }),
    ).toBeInTheDocument();
    expect(searchKnowledge).not.toHaveBeenCalled();
    expect(fetchKnowledgeTypeCounts).toHaveBeenCalled();
  });

  it("Escape on the type picker goes back to the source picker (not dismiss)", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await openKnowledgeTypePicker(user, editor);
    await screen.findByText(/Choose type/i);

    await user.keyboard("{Escape}");

    await waitFor(() => {
      expect(screen.getByText("Choose a source")).toBeInTheDocument();
    });
    expect(editor.textContent).toContain("@");
  });

  it("searches by type after a type is chosen from the picker", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [knowledge()] });
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await openKnowledgeTypePicker(user, editor);
    await screen.findByRole("option", { name: /SOP \(23\)/i });
    await user.click(screen.getByRole("option", { name: /SOP \(23\)/i }));

    await waitFor(() => {
      expect(searchKnowledge).toHaveBeenCalledWith(
        expect.objectContaining({
          q: "",
          type: "SOP",
          status: "ACTIVE",
          referenceOnly: true,
          limit: 10,
        }),
      );
    });
    expect(
      await screen.findByRole("option", { name: /SOP Penanganan Pengaduan/i }),
    ).toBeInTheDocument();
  });

  it("filters the Knowledge search by the typed query (skips type picker)", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [] });
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await openKnowledgeTypePicker(user, editor, "pengaduan");

    await waitFor(() => {
      expect(searchKnowledge).toHaveBeenCalledWith(
        expect.objectContaining({
          q: "pengaduan",
          status: "ACTIVE",
          referenceOnly: true,
          limit: 10,
        }),
      );
    });
  });

  it("shows the empty state when no Knowledge matches", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [] });
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await openKnowledgeTypePicker(user, editor, "xyz");

    await waitFor(() => {
      expect(screen.getByText("No Knowledge found.")).toBeInTheDocument();
    });
  });

  it("shows an error state when the Knowledge search fails", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockRejectedValue(new Error("network down"));
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await openKnowledgeTypePicker(user, editor, "x");

    await waitFor(() => {
      expect(screen.getByText("Unable to load Knowledge.")).toBeInTheDocument();
    });
  });

  it("selecting a Knowledge result inserts an inline chip (no raw marker)", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [knowledge()] });
    const onValue = vi.fn();
    renderWithProviders(<Harness onValue={onValue} />);

    const editor = screen.getByRole("combobox");
    await openKnowledgeTypePicker(user, editor, "pengaduan");

    const option = await screen.findByRole("option", {
      name: /SOP Penanganan Pengaduan/i,
    });
    await user.click(option);

    await waitFor(() => {
      expect(onValue).toHaveBeenCalledWith(
        expect.stringContaining(
          "@[SOP Penanganan Pengaduan v2.1](knowledge:e5555555-5555-5555-5555-555555555555)",
        ),
      );
    });

    expect(editor.textContent).toContain("SOP Penanganan Pengaduan v2.1");
    expect(
      editor
        .querySelector('[data-mention-kind="knowledge"]')
        ?.getAttribute("data-mention-type-label"),
    ).toBe("SOP");
    expect(editor.textContent).not.toContain("knowledge:");
  });

  it("selects the highlighted Knowledge result with Enter", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [knowledge()] });
    const onValue = vi.fn();
    renderWithProviders(<Harness onValue={onValue} />);

    const editor = screen.getByRole("combobox");
    await openKnowledgeTypePicker(user, editor, "sop");
    await screen.findByRole("option", { name: /SOP Penanganan Pengaduan/i });
    await user.keyboard("{Enter}");

    await waitFor(() => {
      expect(onValue).toHaveBeenCalledWith(
        expect.stringContaining("knowledge:e5555555-5555-5555-5555-555555555555"),
      );
    });
  });

  it("caps client Knowledge search requests at limit 10", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({
      data: Array.from({ length: 15 }, (_, i) =>
        knowledge({
          id: `e5555555-5555-5555-5555-5555555555${i.toString().padStart(2, "0")}`,
          title: `SOP ${i}`,
        }),
      ),
    });
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await openKnowledgeTypePicker(user, editor, "sop");

    await waitFor(() => {
      expect(screen.getAllByRole("option")).toHaveLength(10);
    });
  });

  it("closes the dropdown on Escape without keeping a selection", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [knowledge()] });
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await openKnowledgeTypePicker(user, editor, "pengaduan");
    await waitFor(() => {
      expect(screen.getByText("Search Knowledge")).toBeInTheDocument();
    });

    await user.keyboard("{Escape}");

    await waitFor(() => {
      expect(screen.queryByText("Search Knowledge")).not.toBeInTheDocument();
    });
    expect(editor.textContent).toContain("@pengaduan");
  });

  it("shows a type tag in front of each Knowledge result title", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({
      data: [knowledge({ documentNumber: null, versionLabel: "1.0" })],
    });
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await openKnowledgeTypePicker(user, editor, "sop");

    await waitFor(() => {
      expect(
        screen.getByRole("option", { name: /SOP.*SOP Penanganan Pengaduan v1\.0/i }),
      ).toBeInTheDocument();
    });
  });

  it("clicking an inline Knowledge chip opens a read-only preview modal instead of navigating", async () => {
    const user = userEvent.setup();
    fetchKnowledge.mockResolvedValue({
      data: knowledge({ status: "ACTIVE", summary: "Ringkasan uji" }),
    });
    renderWithProviders(
      <Harness initialValue="Sesuai @[SOP Penanganan Pengaduan v2.1](knowledge:e5555555-5555-5555-5555-555555555555)" />,
    );

    const chip = await screen.findByText("SOP Penanganan Pengaduan v2.1");
    await user.click(chip);

    expect(push).not.toHaveBeenCalled();
    expect(await screen.findByRole("dialog")).toBeInTheDocument();
    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: "SOP Penanganan Pengaduan" }),
      ).toBeInTheDocument();
    });
    expect(screen.getByText("Ringkasan uji")).toBeInTheDocument();
  });

  it("closing the preview modal calls onClose and does not navigate", async () => {
    const user = userEvent.setup();
    fetchKnowledge.mockResolvedValue({ data: knowledge({ status: "ACTIVE" }) });
    renderWithProviders(
      <Harness initialValue="Sesuai @[SOP Penanganan Pengaduan v2.1](knowledge:e5555555-5555-5555-5555-555555555555)" />,
    );

    const chip = await screen.findByText("SOP Penanganan Pengaduan v2.1");
    await user.click(chip);
    await screen.findByRole("dialog");

    await user.click(screen.getByRole("button", { name: /^close dialog$/i }));

    await waitFor(() => {
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });
    expect(push).not.toHaveBeenCalled();
  });

  describe("Pengumuman source", () => {
    it("searches active announcements immediately (empty query) after choosing the source", async () => {
      const user = userEvent.setup();
      fetchActiveAnnouncements.mockResolvedValue({ data: [announcement()] });
      renderWithProviders(<Harness />);

      const editor = screen.getByRole("combobox");
      await user.click(editor);
      await user.keyboard("@");
      await screen.findByRole("option", { name: /^Announcement/ });
      await user.click(screen.getByRole("option", { name: /^Announcement/ }));

      await waitFor(() => {
        expect(fetchActiveAnnouncements).toHaveBeenCalled();
      });
      expect(
        await screen.findByRole("option", { name: /Libur Nasional/i }),
      ).toBeInTheDocument();
    });

    it("filters announcement results client-side by the typed title", async () => {
      const user = userEvent.setup();
      fetchActiveAnnouncements.mockResolvedValue({
        data: [
          announcement({ title: "Libur Nasional" }),
          announcement({
            id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            title: "Perubahan Jam Layanan",
          }),
        ],
      });
      renderWithProviders(<Harness />);

      const editor = screen.getByRole("combobox");
      await user.click(editor);
      await user.keyboard("@");
      await user.click(await screen.findByRole("option", { name: /^Announcement/ }));
      await user.keyboard("libur");

      await waitFor(() => {
        expect(
          screen.getByRole("option", { name: /Libur Nasional/i }),
        ).toBeInTheDocument();
        expect(
          screen.queryByRole("option", { name: /Perubahan Jam Layanan/i }),
        ).not.toBeInTheDocument();
      });
    });

    it("shows the announcement empty state when none match", async () => {
      const user = userEvent.setup();
      fetchActiveAnnouncements.mockResolvedValue({ data: [] });
      renderWithProviders(<Harness />);

      const editor = screen.getByRole("combobox");
      await user.click(editor);
      await user.keyboard("@");
      await user.click(await screen.findByRole("option", { name: /^Announcement/ }));

      await waitFor(() => {
        expect(
          screen.getByText("No active Announcement found."),
        ).toBeInTheDocument();
      });
    });

    it("inserts an announcement marker on selection", async () => {
      const user = userEvent.setup();
      fetchActiveAnnouncements.mockResolvedValue({ data: [announcement()] });
      const onValue = vi.fn();
      renderWithProviders(<Harness onValue={onValue} />);

      const editor = screen.getByRole("combobox");
      await user.click(editor);
      await user.keyboard("@");
      await user.click(await screen.findByRole("option", { name: /^Announcement/ }));
      const option = await screen.findByRole("option", { name: /Libur Nasional/i });
      await user.click(option);

      await waitFor(() => {
        expect(onValue).toHaveBeenCalledWith(
          expect.stringContaining(
            "@[Libur Nasional](announcement:cccccccc-cccc-4ccc-8ccc-cccccccccccc)",
          ),
        );
      });
      expect(editor.textContent).not.toContain("announcement:");
    });

    it("clicking an inserted announcement chip does not navigate or open a dialog (edit-time)", async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <Harness initialValue="Lihat @[Libur Nasional](announcement:cccccccc-cccc-4ccc-8ccc-cccccccccccc)" />,
      );

      const chip = await screen.findByText("Libur Nasional");
      await user.click(chip);

      expect(push).not.toHaveBeenCalled();
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });
  });

  describe("Lampiran source", () => {
    it("searches the PUBLIC-filtered attachment catalog after choosing the source", async () => {
      const user = userEvent.setup();
      fetchAnnouncementAttachmentLibrary.mockResolvedValue({
        data: [libraryFile()],
      });
      renderWithProviders(<Harness />);

      const editor = screen.getByRole("combobox");
      await user.click(editor);
      await user.keyboard("@");
      await user.click(await screen.findByRole("option", { name: /^Attachment/ }));

      await waitFor(() => {
        expect(fetchAnnouncementAttachmentLibrary).toHaveBeenCalled();
      });
      expect(
        await screen.findByRole("option", { name: /Formulir Klaim\.pdf/i }),
      ).toBeInTheDocument();
    });

    it("never offers a PRIVATE file, even if the catalog endpoint returns one", async () => {
      const user = userEvent.setup();
      fetchAnnouncementAttachmentLibrary.mockResolvedValue({
        data: [
          libraryFile({ accessLevel: "PUBLIC", fileName: "Publik.pdf" }),
          libraryFile({
            id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            accessLevel: "PRIVATE",
            fileName: "Rahasia.pdf",
          }),
        ],
      });
      renderWithProviders(<Harness />);

      const editor = screen.getByRole("combobox");
      await user.click(editor);
      await user.keyboard("@");
      await user.click(await screen.findByRole("option", { name: /^Attachment/ }));

      await waitFor(() => {
        expect(
          screen.getByRole("option", { name: /Publik\.pdf/i }),
        ).toBeInTheDocument();
      });
      expect(
        screen.queryByRole("option", { name: /Rahasia\.pdf/i }),
      ).not.toBeInTheDocument();
    });

    it("shows the attachment empty state when none match", async () => {
      const user = userEvent.setup();
      fetchAnnouncementAttachmentLibrary.mockResolvedValue({ data: [] });
      renderWithProviders(<Harness />);

      const editor = screen.getByRole("combobox");
      await user.click(editor);
      await user.keyboard("@");
      await user.click(await screen.findByRole("option", { name: /^Attachment/ }));

      await waitFor(() => {
        expect(screen.getByText("No public Attachment found.")).toBeInTheDocument();
      });
    });

    it("inserts an attachment marker on selection", async () => {
      const user = userEvent.setup();
      fetchAnnouncementAttachmentLibrary.mockResolvedValue({
        data: [libraryFile()],
      });
      const onValue = vi.fn();
      renderWithProviders(<Harness onValue={onValue} />);

      const editor = screen.getByRole("combobox");
      await user.click(editor);
      await user.keyboard("@");
      await user.click(await screen.findByRole("option", { name: /^Attachment/ }));
      const option = await screen.findByRole("option", { name: /Formulir Klaim/i });
      await user.click(option);

      await waitFor(() => {
        expect(onValue).toHaveBeenCalledWith(
          expect.stringContaining(
            "@[Formulir Klaim.pdf](attachment:dddddddd-dddd-4ddd-8ddd-dddddddddddd)",
          ),
        );
      });
      expect(editor.textContent).not.toContain("attachment:");
    });
  });

  it("Escape from an announcement/attachment results view goes back to the source picker", async () => {
    const user = userEvent.setup();
    fetchActiveAnnouncements.mockResolvedValue({ data: [announcement()] });
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await user.click(editor);
    await user.keyboard("@");
    await user.click(await screen.findByRole("option", { name: /^Announcement/ }));
    await screen.findByRole("option", { name: /Libur Nasional/i });

    await user.keyboard("{Escape}");

    await waitFor(() => {
      expect(screen.getByText("Choose a source")).toBeInTheDocument();
    });
  });
});
