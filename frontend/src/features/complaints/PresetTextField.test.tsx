/**
 * PresetTextField — quick-fill tags on top of the mention editor.
 * Clicking a tag must keep what the user already wrote and hand the caret back.
 */
import { useState } from "react";
import { cleanup, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

import { PresetTextField } from "./PresetTextField";

function Harness({ initial = "" }: { initial?: string }) {
  const [value, setValue] = useState(initial);
  return (
    <PresetTextField
      presets={["Kasus selesai ditangani", "Duplikat"]}
      label="Catatan"
      name="note"
      value={value}
      onChange={setValue}
    />
  );
}

function editor(): HTMLElement {
  const node = document.querySelector<HTMLElement>('[role="combobox"]');
  if (!node) throw new Error("editor not found");
  return node;
}

/** The contenteditable renders line breaks as elements, so read the stored
 *  value from the hidden input the field submits. */
function storedValue(): string {
  const node = document.querySelector<HTMLInputElement>('input[name="note"]');
  if (!node) throw new Error("hidden input not found");
  return node.value;
}

afterEach(() => cleanup());

describe("PresetTextField", () => {
  it("menambahkan preset tanpa menghapus teks yang sudah diketik", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Harness initial="Sudah dihubungi pelapor" />);

    await user.click(screen.getByText("Kasus selesai ditangani"));

    expect(storedValue()).toBe(
      "Sudah dihubungi pelapor\nKasus selesai ditangani",
    );
  });

  it("mengembalikan fokus ke field setelah tag diklik", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Harness />);

    await user.click(screen.getByText("Duplikat"));

    expect(document.activeElement).toBe(editor());
  });
});
