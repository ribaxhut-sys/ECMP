import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { renderWithProviders } from "@/test/harness";
import { FoundationLegacyBanner } from "./FoundationLegacyBanner";

describe("FoundationLegacyBanner", () => {
  it("points officers to CM complaints and Case inbox without retiring Foundation", () => {
    renderWithProviders(<FoundationLegacyBanner />);

    expect(screen.getByTestId("foundation-legacy-banner")).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /open cm complaints/i }),
    ).toHaveAttribute("href", "/complaints");
    expect(screen.getByRole("link", { name: /open cases/i })).toHaveAttribute(
      "href",
      "/complaints/cm/cases",
    );
  });
});
