/**
 * KnowledgeMentionTextarea — `@` autocomplete (Option A: inline chips).
 */
import { useState } from "react";
import { cleanup, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import type { Knowledge } from "@/lib/api/types";

const searchKnowledge = vi.fn();
const fetchKnowledge = vi.fn();
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
    files: [],
    ...overrides,
  };
}

function Harness({ onValue }: { onValue?: (value: string) => void }) {
  const [value, setValue] = useState("");
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

describe("KnowledgeMentionTextarea", () => {
  beforeEach(() => {
    searchKnowledge.mockReset();
    fetchKnowledge.mockReset();
    fetchKnowledge.mockResolvedValue({
      data: knowledge({ status: "ACTIVE" }),
    });
    push.mockReset();
  });

  afterEach(() => {
    cleanup();
  });

  it("shows the type picker (SOP…Panduan) when @ is typed with an empty query", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await user.click(editor);
    await user.keyboard("Sesuai @");

    await waitFor(() => {
      expect(screen.getByText(/Choose type/i)).toBeInTheDocument();
      expect(screen.getAllByText(/Esc to go back/i).length).toBeGreaterThan(0);
    });
    expect(screen.getByRole("option", { name: /Browse SOP/i })).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: /Browse Peraturan|Browse Regulation/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: /Browse Surat Edaran|Browse Circular/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: /Browse Keputusan|Browse Decision/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: /Browse Panduan|Browse Guide/i }),
    ).toBeInTheDocument();
    expect(searchKnowledge).not.toHaveBeenCalled();
  });

  it("searches by type after a type is chosen from the picker", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [knowledge()] });
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await user.click(editor);
    await user.keyboard("@");
    await screen.findByText(/Choose type/i);

    await user.click(screen.getByRole("option", { name: /Browse SOP/i }));

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

  it("filters the search by the typed query (skips type picker)", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [] });
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await user.click(editor);
    await user.keyboard("@pengaduan");

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
    await user.click(editor);
    await user.keyboard("@xyz");

    await waitFor(() => {
      expect(screen.getByText("No Knowledge found.")).toBeInTheDocument();
    });
  });

  it("shows an error state when the search fails", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockRejectedValue(new Error("network down"));
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await user.click(editor);
    await user.keyboard("@x");

    await waitFor(() => {
      expect(screen.getByText("Unable to load Knowledge.")).toBeInTheDocument();
    });
  });

  it("selecting a result inserts an inline chip (no raw marker, no below preview)", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [knowledge()] });
    const onValue = vi.fn();
    renderWithProviders(<Harness onValue={onValue} />);

    const editor = screen.getByRole("combobox");
    await user.click(editor);
    await user.keyboard("Sesuai @pengaduan");

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
    expect(editor.textContent).not.toContain("knowledge:");
    expect(
      screen.queryByText(/Selected references|Rujukan terpilih/i),
    ).not.toBeInTheDocument();
    expect(screen.queryByText("Search Knowledge")).not.toBeInTheDocument();
  });

  it("selects the highlighted result with Enter", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [knowledge()] });
    const onValue = vi.fn();
    renderWithProviders(<Harness onValue={onValue} />);

    const editor = screen.getByRole("combobox");
    await user.click(editor);
    await user.keyboard("@sop");
    await screen.findByRole("option", { name: /SOP Penanganan Pengaduan/i });
    await user.keyboard("{Enter}");

    await waitFor(() => {
      expect(onValue).toHaveBeenCalledWith(
        expect.stringContaining("knowledge:e5555555-5555-5555-5555-555555555555"),
      );
    });
  });

  it("caps client search requests at limit 10", async () => {
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
    await user.click(editor);
    await user.keyboard("@sop");

    await waitFor(() => {
      expect(screen.getAllByRole("option")).toHaveLength(10);
    });
  });

  it("closes the dropdown on Escape without keeping a selection", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [knowledge()] });
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await user.click(editor);
    await user.keyboard("Sesuai @pengaduan");
    await waitFor(() => {
      expect(screen.getByText("Search Knowledge")).toBeInTheDocument();
    });

    await user.keyboard("{Escape}");

    await waitFor(() => {
      expect(screen.queryByText("Search Knowledge")).not.toBeInTheDocument();
    });
    expect(editor.textContent).toContain("@pengaduan");
  });

  it("shows a type tag in front of each result title (no status subtitle)", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({
      data: [knowledge({ documentNumber: null, versionLabel: "1.0" })],
    });
    renderWithProviders(<Harness />);

    const editor = screen.getByRole("combobox");
    await user.click(editor);
    await user.keyboard("@sop");

    await waitFor(() => {
      expect(
        screen.getByRole("option", { name: /SOP.*SOP Penanganan Pengaduan v1\.0/i }),
      ).toBeInTheDocument();
    });
    expect(screen.queryByText(/· Active|· Aktif/i)).not.toBeInTheDocument();
  });
});
