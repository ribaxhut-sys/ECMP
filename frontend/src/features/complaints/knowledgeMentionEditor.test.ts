import { describe, expect, it } from "vitest";
import {
  createMentionChip,
  getVisibleOffsetRect,
  renderMentionEditor,
  serializeMentionEditor,
} from "./knowledgeMentionEditor";

describe("knowledgeMentionEditor", () => {
  it("round-trips a knowledge storage marker to an inline chip and back", () => {
    const root = document.createElement("div");
    const storage =
      "Sesuai @[SOP Penanganan Pengaduan v2.1](knowledge:e5555555-5555-5555-5555-555555555555) ya.";
    renderMentionEditor(root, storage);

    expect(root.textContent).toBe("Sesuai SOP Penanganan Pengaduan v2.1 ya.");
    expect(root.textContent).not.toContain("knowledge:");
    expect(root.querySelector('[data-mention-kind="knowledge"]')?.textContent).toBe(
      "SOP Penanganan Pengaduan v2.1",
    );
    expect(serializeMentionEditor(root)).toBe(storage);
  });

  it("round-trips announcement and attachment storage markers", () => {
    const root = document.createElement("div");
    const storage =
      "Lihat @[Libur Nasional](announcement:cccccccc-cccc-4ccc-8ccc-cccccccccccc) dan @[Formulir.pdf](attachment:dddddddd-dddd-4ddd-8ddd-dddddddddddd).";
    renderMentionEditor(root, storage);

    expect(root.textContent).toBe("Lihat Libur Nasional dan Formulir.pdf.");
    expect(
      root.querySelector('[data-mention-kind="announcement"]')?.textContent,
    ).toBe("Libur Nasional");
    expect(
      root.querySelector('[data-mention-kind="attachment"]')?.textContent,
    ).toBe("Formulir.pdf");
    expect(serializeMentionEditor(root)).toBe(storage);
  });

  it("serializes a freshly created knowledge chip", () => {
    const root = document.createElement("div");
    root.appendChild(document.createTextNode("Hi "));
    root.appendChild(
      createMentionChip(
        document,
        "knowledge",
        "SOP A",
        "e5555555-5555-5555-5555-555555555555",
      ),
    );
    expect(serializeMentionEditor(root)).toBe(
      "Hi @[SOP A](knowledge:e5555555-5555-5555-5555-555555555555)",
    );
  });

  it("serializes a freshly created attachment chip", () => {
    const root = document.createElement("div");
    root.appendChild(
      createMentionChip(
        document,
        "attachment",
        "Formulir.pdf",
        "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
      ),
    );
    expect(serializeMentionEditor(root)).toBe(
      "@[Formulir.pdf](attachment:dddddddd-dddd-4ddd-8ddd-dddddddddddd)",
    );
  });

  it("shows a type tag on the chip without storing it in the marker", () => {
    const root = document.createElement("div");
    root.appendChild(
      createMentionChip(
        document,
        "knowledge",
        "Tata cara v1.0",
        "e5555555-5555-5555-5555-555555555555",
        "SOP",
      ),
    );
    expect(root.textContent).toBe("SOP Tata cara v1.0");
    expect(serializeMentionEditor(root)).toBe(
      "@[Tata cara v1.0](knowledge:e5555555-5555-5555-5555-555555555555)",
    );
  });

  it("returns a client rect for a visible offset (menu anchor)", () => {
    const root = document.createElement("div");
    document.body.appendChild(root);
    root.appendChild(document.createTextNode("Hi @sop"));
    const rect = getVisibleOffsetRect(root, 3);
    expect(rect).not.toBeNull();
    root.remove();
  });
});
