import { cleanup, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import type { Announcement, Attachment, Knowledge } from "@/lib/api/types";

const push = vi.fn();
const fetchKnowledge = vi.fn();
const fetchAnnouncement = vi.fn();
const fetchAttachment = vi.fn();
const pushError = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

vi.mock("@/shared/providers", async () => {
  const actual = await vi.importActual<typeof import("@/shared/providers")>(
    "@/shared/providers",
  );
  return {
    ...actual,
    useToast: () => ({ push: vi.fn(), pushSuccess: vi.fn(), pushError }),
  };
});

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchKnowledge: (...args: unknown[]) => fetchKnowledge(...args),
    fetchAnnouncement: (...args: unknown[]) => fetchAnnouncement(...args),
    fetchAttachment: (...args: unknown[]) => fetchAttachment(...args),
  };
});

import { KnowledgeReferenceText } from "./KnowledgeReferenceText";

function knowledge(overrides: Partial<Knowledge> = {}): Knowledge {
  return {
    id: "e5555555-5555-5555-5555-555555555555",
    title: "SOP Pengaduan",
    knowledgeType: "SOP",
    status: "ACTIVE",
    documentNumber: null,
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
    pinned: false,
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

function attachment(overrides: Partial<Attachment> = {}): Attachment {
  return {
    id: "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
    aggregateType: "Announcement",
    aggregateId: "00000000-0000-4000-8000-0000000000a1",
    fileName: "formulir-klaim.pdf",
    originalName: "Formulir Klaim.pdf",
    mimeType: "application/pdf",
    extension: "pdf",
    sizeBytes: 1024,
    checksumSha256: "abc123",
    storageProvider: "local",
    uploadedBy: null,
    uploadedAt: "2026-07-30T00:00:00Z",
    status: "AVAILABLE",
    ...overrides,
  };
}

describe("KnowledgeReferenceText", () => {
  afterEach(() => {
    cleanup();
    push.mockReset();
    fetchKnowledge.mockReset();
    fetchAnnouncement.mockReset();
    fetchAttachment.mockReset();
    pushError.mockReset();
  });

  it("renders plain text unchanged when there is no reference", () => {
    renderWithProviders(<KnowledgeReferenceText text="Penyelesaian tanpa rujukan." />);
    expect(screen.getByText("Penyelesaian tanpa rujukan.")).toBeInTheDocument();
  });

  it("renders a reference marker as a clickable element showing the snapshot title", () => {
    fetchKnowledge.mockResolvedValue({ data: knowledge() });
    const text =
      "Penyelesaian sesuai @[SOP Penanganan Pengaduan v2.1](knowledge:e5555555-5555-5555-5555-555555555555).";
    renderWithProviders(<KnowledgeReferenceText text={text} />);
    expect(
      screen.getByRole("button", { name: /SOP Penanganan Pengaduan v2\.1/i }),
    ).toBeInTheDocument();
  });

  it("navigates to the Knowledge detail page when the reference is clicked", async () => {
    const user = userEvent.setup();
    fetchKnowledge.mockResolvedValue({ data: knowledge() });
    const text = "Sesuai @[SOP Pengaduan](knowledge:e5555555-5555-5555-5555-555555555555).";
    renderWithProviders(<KnowledgeReferenceText text={text} />);

    await user.click(screen.getByRole("button", { name: /SOP Pengaduan/i }));

    expect(push).toHaveBeenCalledWith(
      "/knowledge/e5555555-5555-5555-5555-555555555555",
    );
  });

  it("renders the reference title in italic blue when Knowledge is active", async () => {
    fetchKnowledge.mockResolvedValue({ data: knowledge({ status: "ACTIVE" }) });
    const text = "Sesuai @[SOP Pengaduan](knowledge:e5555555-5555-5555-5555-555555555555).";
    renderWithProviders(<KnowledgeReferenceText text={text} />);
    const button = screen.getByRole("button", { name: /SOP Pengaduan/i });
    expect(button.className).toContain("italic");
    expect(button.className).toContain("text-ecmp-primary");
    await waitFor(() => {
      expect(screen.getByText("SOP")).toBeInTheDocument();
    });
  });

  it("renders inactive Knowledge references in red", async () => {
    fetchKnowledge.mockResolvedValue({
      data: knowledge({ status: "ARCHIVED" }),
    });
    const text = "Sesuai @[SOP Pengaduan](knowledge:e5555555-5555-5555-5555-555555555555).";
    renderWithProviders(<KnowledgeReferenceText text={text} />);

    await waitFor(() => {
      const button = screen.getByRole("button", { name: /SOP Pengaduan/i });
      expect(button.className).toContain("text-ecmp-danger");
      expect(button.className).not.toContain("text-ecmp-primary");
    });
  });

  it("renders multiple references with plain text preserved between them", () => {
    fetchKnowledge.mockResolvedValue({ data: knowledge() });
    const text =
      "Berdasarkan @[SOP A](knowledge:e5555555-5555-5555-5555-555555555555) dan @[Peraturan B](knowledge:f6666666-6666-6666-6666-666666666666), penyelesaian dilakukan.";
    renderWithProviders(<KnowledgeReferenceText text={text} />);
    expect(screen.getByRole("button", { name: /SOP A/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Peraturan B/i })).toBeInTheDocument();
    expect(screen.getByText(/dan/)).toBeInTheDocument();
  });

  it("degrades a malformed marker to plain text without crashing", () => {
    renderWithProviders(<KnowledgeReferenceText text="Sesuai @[Rusak](knowledge:not-a-uuid)." />);
    expect(
      screen.getByText("Sesuai @[Rusak](knowledge:not-a-uuid)."),
    ).toBeInTheDocument();
  });

  it("degrades an unknown mention kind to plain text without crashing", () => {
    renderWithProviders(
      <KnowledgeReferenceText text="Sesuai @[X](unknown:e5555555-5555-5555-5555-555555555555)." />,
    );
    expect(
      screen.getByText(
        "Sesuai @[X](unknown:e5555555-5555-5555-5555-555555555555).",
      ),
    ).toBeInTheDocument();
  });

  describe("announcement reference", () => {
    it("navigates to the announcement detail page when clicked", async () => {
      const user = userEvent.setup();
      fetchAnnouncement.mockResolvedValue({ data: announcement() });
      const text =
        "Lihat @[Libur Nasional](announcement:cccccccc-cccc-4ccc-8ccc-cccccccccccc).";
      renderWithProviders(<KnowledgeReferenceText text={text} />);

      await user.click(screen.getByRole("button", { name: /Libur Nasional/i }));

      expect(push).toHaveBeenCalledWith(
        "/announcements/cccccccc-cccc-4ccc-8ccc-cccccccccccc",
      );
    });

    it("renders active (PUBLISHED) announcements in blue", async () => {
      fetchAnnouncement.mockResolvedValue({
        data: announcement({ effectiveStatus: "PUBLISHED" }),
      });
      const text =
        "Lihat @[Libur Nasional](announcement:cccccccc-cccc-4ccc-8ccc-cccccccccccc).";
      renderWithProviders(<KnowledgeReferenceText text={text} />);

      await waitFor(() => {
        const button = screen.getByRole("button", { name: /Libur Nasional/i });
        expect(button.className).toContain("text-ecmp-primary");
      });
    });

    it("renders expired/unpublished announcements in red", async () => {
      fetchAnnouncement.mockResolvedValue({
        data: announcement({ effectiveStatus: "EXPIRED" }),
      });
      const text =
        "Lihat @[Libur Nasional](announcement:cccccccc-cccc-4ccc-8ccc-cccccccccccc).";
      renderWithProviders(<KnowledgeReferenceText text={text} />);

      await waitFor(() => {
        const button = screen.getByRole("button", { name: /Libur Nasional/i });
        expect(button.className).toContain("text-ecmp-danger");
      });
    });

    it("renders in red when the announcement no longer exists", async () => {
      fetchAnnouncement.mockRejectedValue(new Error("404"));
      const text =
        "Lihat @[Dihapus](announcement:cccccccc-cccc-4ccc-8ccc-cccccccccccc).";
      renderWithProviders(<KnowledgeReferenceText text={text} />);

      await waitFor(() => {
        const button = screen.getByRole("button", { name: /Dihapus/i });
        expect(button.className).toContain("text-ecmp-danger");
      });
    });
  });

  describe("attachment reference", () => {
    it("opens the attachment viewer instead of navigating when clicked", async () => {
      const user = userEvent.setup();
      fetchAttachment.mockResolvedValue({ data: attachment() });
      const text =
        "Lihat @[Formulir Klaim.pdf](attachment:dddddddd-dddd-4ddd-8ddd-dddddddddddd).";
      renderWithProviders(<KnowledgeReferenceText text={text} />);

      await user.click(
        screen.getByRole("button", { name: /Formulir Klaim\.pdf/i }),
      );

      expect(push).not.toHaveBeenCalled();
      await waitFor(() => {
        expect(fetchAttachment).toHaveBeenCalledWith(
          "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
        );
      });
    });

    it("shows an error toast when the attachment can no longer be opened", async () => {
      const user = userEvent.setup();
      fetchAttachment.mockRejectedValue(new Error("403"));
      const text =
        "Lihat @[Formulir Klaim.pdf](attachment:dddddddd-dddd-4ddd-8ddd-dddddddddddd).";
      renderWithProviders(<KnowledgeReferenceText text={text} />);

      await user.click(
        screen.getByRole("button", { name: /Formulir Klaim\.pdf/i }),
      );

      await waitFor(() => {
        expect(pushError).toHaveBeenCalled();
      });
    });

    it("renders AVAILABLE attachments in blue", async () => {
      fetchAttachment.mockResolvedValue({
        data: attachment({ status: "AVAILABLE" }),
      });
      const text =
        "Lihat @[Formulir Klaim.pdf](attachment:dddddddd-dddd-4ddd-8ddd-dddddddddddd).";
      renderWithProviders(<KnowledgeReferenceText text={text} />);

      await waitFor(() => {
        const button = screen.getByRole("button", {
          name: /Formulir Klaim\.pdf/i,
        });
        expect(button.className).toContain("text-ecmp-primary");
      });
    });

    it("renders DELETED (soft-deleted) attachments in red", async () => {
      fetchAttachment.mockResolvedValue({
        data: attachment({ status: "DELETED" }),
      });
      const text =
        "Lihat @[Formulir Klaim.pdf](attachment:dddddddd-dddd-4ddd-8ddd-dddddddddddd).";
      renderWithProviders(<KnowledgeReferenceText text={text} />);

      await waitFor(() => {
        const button = screen.getByRole("button", {
          name: /Formulir Klaim\.pdf/i,
        });
        expect(button.className).toContain("text-ecmp-danger");
      });
    });

    it("renders in red when the attachment is no longer accessible (403/404)", async () => {
      fetchAttachment.mockRejectedValue(new Error("404"));
      const text =
        "Lihat @[Formulir Klaim.pdf](attachment:dddddddd-dddd-4ddd-8ddd-dddddddddddd).";
      renderWithProviders(<KnowledgeReferenceText text={text} />);

      await waitFor(() => {
        const button = screen.getByRole("button", {
          name: /Formulir Klaim\.pdf/i,
        });
        expect(button.className).toContain("text-ecmp-danger");
      });
    });
  });

  it("resolves mixed-kind references independently in the same text", async () => {
    fetchKnowledge.mockResolvedValue({ data: knowledge({ status: "ACTIVE" }) });
    fetchAnnouncement.mockResolvedValue({
      data: announcement({ effectiveStatus: "EXPIRED" }),
    });
    const text =
      "Sesuai @[SOP A](knowledge:e5555555-5555-5555-5555-555555555555) dan @[Libur](announcement:cccccccc-cccc-4ccc-8ccc-cccccccccccc).";
    renderWithProviders(<KnowledgeReferenceText text={text} />);

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /SOP A/i }).className,
      ).toContain("text-ecmp-primary");
      expect(
        screen.getByRole("button", { name: /Libur/i }).className,
      ).toContain("text-ecmp-danger");
    });
  });
});
