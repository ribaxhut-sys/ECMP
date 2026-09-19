import { cleanup, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";

const replace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace }),
}));

import { EscalateIntakeView } from "./EscalateIntakeView";

afterEach(() => {
  cleanup();
  replace.mockReset();
});

describe("EscalateIntakeView", () => {
  it("redirects the retired priority step back to /complaints/new", async () => {
    renderWithProviders(<EscalateIntakeView />);
    await waitFor(() => {
      expect(replace).toHaveBeenCalledWith("/complaints/new");
    });
  });
});
