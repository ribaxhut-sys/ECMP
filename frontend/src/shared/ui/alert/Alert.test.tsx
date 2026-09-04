import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Alert } from "./Alert";

describe("Alert", () => {
  it("uses compact banner chrome instead of card padding and shadow", () => {
    render(
      <Alert
        tone="info"
        title="Lampiran terkait"
        description="Akun Anda tidak memiliki izin attachment:read."
      />,
    );
    const el = screen.getByRole("alert");
    expect(el.className).toContain("py-2");
    expect(el.className).toContain("px-3");
    expect(el.className).not.toContain("py-4");
    expect(el.className).not.toContain("shadow-ecmp-surface");
    expect(el.className).toContain("rounded-[var(--ecmp-radius-md)]");
  });

  it("keeps title and description readable", () => {
    render(
      <Alert
        tone="warning"
        title="Berkas belum lengkap"
        description="Lengkapi lampiran sebelum kirim ulang."
      />,
    );
    expect(screen.getByText("Berkas belum lengkap")).toBeInTheDocument();
    expect(
      screen.getByText("Lengkapi lampiran sebelum kirim ulang."),
    ).toBeInTheDocument();
  });
});
