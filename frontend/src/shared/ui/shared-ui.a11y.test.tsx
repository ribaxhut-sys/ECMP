/**
 * Accessibility smoke checks (FE-CI-POL-001 Phase B — warn mode in CI).
 * Uses axe-core against shared design-system primitives (no Mode B AuthN).
 */
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import axe from "axe-core";
import { Alert } from "@/shared/ui/alert";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Breadcrumb } from "@/shared/ui/breadcrumb";

async function runAxe(container: HTMLElement) {
  const results = await axe.run(container, {
    rules: {
      // jsdom lacks full layout/CSS; keep rules meaningful without a browser.
      "color-contrast": { enabled: false },
    },
  });
  return results.violations;
}

describe("a11y smoke (shared UI)", () => {
  it("primary Button has no axe violations", async () => {
    const { container } = render(<Button>Save</Button>);
    expect(await runAxe(container)).toEqual([]);
  });

  it("loading Button exposes busy state without axe violations", async () => {
    const { container } = render(<Button loading>Saving</Button>);
    expect(await runAxe(container)).toEqual([]);
  });

  it("danger Alert has no axe violations", async () => {
    const { container } = render(
      <Alert
        tone="danger"
        title="Unable to load"
        description="Request failed."
        actionLabel="Retry"
        onAction={() => undefined}
      />,
    );
    expect(await runAxe(container)).toEqual([]);
  });

  it("labeled Input has no axe violations", async () => {
    const { container } = render(
      <Input id="subject" label="Subject" hint="Max 200 characters" />,
    );
    expect(await runAxe(container)).toEqual([]);
  });

  it("Breadcrumb navigation has no axe violations", async () => {
    const { container } = render(
      <Breadcrumb
        items={[
          { label: "Home", href: "/dashboard" },
          { label: "Complaints", href: "/complaints" },
          { label: "Detail" },
        ]}
      />,
    );
    expect(await runAxe(container)).toEqual([]);
  });
});
