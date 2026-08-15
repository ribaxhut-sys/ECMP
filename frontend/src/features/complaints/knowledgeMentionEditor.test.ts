import { describe, expect, it } from "vitest";
import {
  createKnowledgeChip,
  getVisibleOffsetRect,
  renderMentionEditor,
  serializeMentionEditor,
} from "./knowledgeMentionEditor";

describe("knowledgeMentionEditor", () => {
  it("round-trips storage markers to inline chips and back", () => {
    const root = document.createElement("div");
    const storage =
      "Sesuai @[SOP Penanganan Pengaduan v2.1](knowledge:e5555555-5555-5555-5555-555555555555) ya.";
    renderMentionEditor(root, storage);

    expect(root.textContent).toBe("Sesuai SOP Penanganan Pengaduan v2.1 ya.");
    expect(root.textContent).not.toContain("knowledge:");
    expect(root.querySelector("[data-knowledge-id]")?.textContent).toBe(
      "SOP Penanganan Pengaduan v2.1",
    );
    expect(serializeMentionEditor(root)).toBe(storage);
  });

  it("serializes a freshly created chip", () => {
    const root = document.createElement("div");
    root.appendChild(document.createTextNode("Hi "));
    root.appendChild(
      createKnowledgeChip(
        document,
        "SOP A",
        "e5555555-5555-5555-5555-555555555555",
      ),
    );
    expect(serializeMentionEditor(root)).toBe(
      "Hi @[SOP A](knowledge:e5555555-5555-5555-5555-555555555555)",
    );
  });

  it("shows a type tag on the chip without storing it in the marker", () => {
    const root = document.createElement("div");
    root.appendChild(
      createKnowledgeChip(
        document,
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
