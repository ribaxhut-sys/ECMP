/**
 * KnowledgeMentionTextarea — `@` autocomplete for Knowledge Reference on
 * Penyelesaian. Reuses the existing Textarea component; no rich-text editor.
 */
import { useState } from "react";
import { cleanup, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import type { Knowledge } from "@/lib/api/types";

const searchKnowledge = vi.fn();

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    searchKnowledge: (...args: unknown[]) => searchKnowledge(...args),
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
  });

  afterEach(() => {
    cleanup();
  });

  it("opens the dropdown and searches Knowledge (ACTIVE, referenceOnly) when @ is typed", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [knowledge()] });
    renderWithProviders(<Harness />);

    const textarea = screen.getByLabelText("Catatan Penyelesaian");
    await user.type(textarea, "Sesuai @");

    await waitFor(() => {
      expect(screen.getByText("Search Knowledge")).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(searchKnowledge).toHaveBeenCalledWith(
        expect.objectContaining({ q: "", status: "ACTIVE", referenceOnly: true }),
      );
    });
  });

  it("filters the search by the typed query", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [] });
    renderWithProviders(<Harness />);

    await user.type(screen.getByLabelText("Catatan Penyelesaian"), "@pengaduan");

    await waitFor(() => {
      expect(searchKnowledge).toHaveBeenCalledWith(
        expect.objectContaining({ q: "pengaduan", status: "ACTIVE", referenceOnly: true }),
      );
    });
  });

  it("shows the empty state when no Knowledge matches", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [] });
    renderWithProviders(<Harness />);

    await user.type(screen.getByLabelText("Catatan Penyelesaian"), "@xyz");

    await waitFor(() => {
      expect(screen.getByText("No Knowledge found.")).toBeInTheDocument();
    });
  });

  it("shows an error state when the search fails", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockRejectedValue(new Error("network down"));
    renderWithProviders(<Harness />);

    await user.type(screen.getByLabelText("Catatan Penyelesaian"), "@x");

    await waitFor(() => {
      expect(screen.getByText("Unable to load Knowledge.")).toBeInTheDocument();
    });
  });

  it("selecting a result inserts a @[title](knowledge:id) marker and closes the dropdown", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [knowledge()] });
    const onValue = vi.fn();
    renderWithProviders(<Harness onValue={onValue} />);

    const textarea = screen.getByLabelText("Catatan Penyelesaian") as HTMLTextAreaElement;
    await user.type(textarea, "Sesuai @pengaduan");

    const option = await screen.findByRole("option", { name: /SOP Penanganan Pengaduan/i });
    await user.click(option);

    await waitFor(() => {
      expect(textarea.value).toBe(
        "Sesuai @[SOP Penanganan Pengaduan v2.1](knowledge:e5555555-5555-5555-5555-555555555555) ",
      );
    });
    expect(screen.queryByText("Search Knowledge")).not.toBeInTheDocument();
  });

  it("closes the dropdown on Escape without changing the text", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({ data: [knowledge()] });
    renderWithProviders(<Harness />);

    const textarea = screen.getByLabelText("Catatan Penyelesaian") as HTMLTextAreaElement;
    await user.type(textarea, "Sesuai @pengaduan");
    await waitFor(() => {
      expect(screen.getByText("Search Knowledge")).toBeInTheDocument();
    });

    await user.keyboard("{Escape}");

    expect(screen.queryByText("Search Knowledge")).not.toBeInTheDocument();
    expect(textarea.value).toBe("Sesuai @pengaduan");
  });

  it("shows type/version/status subtitle for each result", async () => {
    const user = userEvent.setup();
    searchKnowledge.mockResolvedValue({
      data: [knowledge({ documentNumber: null, versionLabel: "1.0" })],
    });
    renderWithProviders(<Harness />);

    await user.type(screen.getByLabelText("Catatan Penyelesaian"), "@sop");

    await waitFor(() => {
      expect(screen.getByText("SOP · v1.0 · Active")).toBeInTheDocument();
    });
  });
});
