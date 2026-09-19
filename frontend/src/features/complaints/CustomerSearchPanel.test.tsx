import { cleanup, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import { formatTaxpayerProfileClipboard } from "./taxpayerProfileClipboard";

const confirmCmBatch1Customer = vi.fn();
const fetchCmBatch1Customer360 = vi.fn();
const searchCmBatch1Customer = vi.fn();
const updateCustomerPhone = vi.fn();
const writeClipboardText = vi.fn();

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    confirmCmBatch1Customer: (...args: unknown[]) =>
      confirmCmBatch1Customer(...args),
    fetchCmBatch1Customer360: (...args: unknown[]) =>
      fetchCmBatch1Customer360(...args),
    searchCmBatch1Customer: (...args: unknown[]) =>
      searchCmBatch1Customer(...args),
    updateCustomerPhone: (...args: unknown[]) => updateCustomerPhone(...args),
  };
});

vi.mock("./taxpayerProfileClipboard", async () => {
  const actual = await vi.importActual<
    typeof import("./taxpayerProfileClipboard")
  >("./taxpayerProfileClipboard");
  return {
    ...actual,
    writeClipboardText: (...args: unknown[]) => writeClipboardText(...args),
  };
});

import { CustomerSearchPanel } from "./CustomerSearchPanel";

afterEach(() => {
  cleanup();
});

beforeEach(() => {
  confirmCmBatch1Customer.mockReset();
  fetchCmBatch1Customer360.mockReset();
  searchCmBatch1Customer.mockReset();
  updateCustomerPhone.mockReset();
  writeClipboardText.mockReset();
  writeClipboardText.mockResolvedValue(undefined);
  confirmCmBatch1Customer.mockResolvedValue({
    data: { customerId: "cust-1", locked: true, asOf: "2026-09-11T00:00:00Z" },
  });
  fetchCmBatch1Customer360.mockResolvedValue({
    data: {
      customerId: "cust-1",
      profile: {
        displayName: "Ayu Santoso",
        customerNumber: "3200000000000034",
        phone: "081212345678",
        email: "ayu@example.com",
      },
      activeComplaints: [],
      complaintHistory: [],
      complaintCount: 0,
      asOf: "2026-09-11T00:00:00Z",
    },
  });
});

function renderLockedPanel() {
  return renderWithProviders(
    <CustomerSearchPanel
      confirmedCustomerId="cust-1"
      confirmedDisplayName="Ayu Santoso"
      onConfirmed={vi.fn()}
      onCleared={vi.fn()}
    />,
  );
}

describe("CustomerSearchPanel taxpayer copy", () => {
  it("shows email and copies the ECMP-WP-1 profile block", async () => {
    const user = userEvent.setup();
    renderLockedPanel();

    await waitFor(() => {
      expect(screen.getByText("ayu@example.com")).toBeInTheDocument();
    });

    await user.click(
      screen.getByRole("button", { name: "Copy taxpayer profile" }),
    );

    await waitFor(() => {
      expect(writeClipboardText).toHaveBeenCalledWith(
        formatTaxpayerProfileClipboard({
          nama: "Ayu Santoso",
          idWp: "3200000000000034",
          telepon: "081212345678",
          email: "ayu@example.com",
        }),
      );
    });
    expect(writeClipboardText.mock.calls[0]![0]).not.toContain("cust-1");
    expect(await screen.findByText("Profile copied")).toBeInTheDocument();
  });

  it("copies the raw taxpayer id without grouping spaces", async () => {
    const user = userEvent.setup();
    renderLockedPanel();

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: "Copy taxpayer ID" }),
      ).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: "Copy taxpayer ID" }));

    await waitFor(() => {
      expect(writeClipboardText).toHaveBeenCalledWith("3200000000000034");
    });
    expect(await screen.findByText("Taxpayer ID copied")).toBeInTheDocument();
  });

  it("toasts a failure without repeating profile fields", async () => {
    writeClipboardText.mockRejectedValue(new Error("denied"));
    const user = userEvent.setup();
    renderLockedPanel();

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: "Copy taxpayer profile" }),
      ).toBeInTheDocument();
    });

    await user.click(
      screen.getByRole("button", { name: "Copy taxpayer profile" }),
    );

    const toast = await screen.findByRole("status");
    expect(toast).toHaveTextContent("Unable to copy profile.");
    expect(toast).not.toHaveTextContent("Ayu Santoso");
    expect(toast).not.toHaveTextContent("3200000000000034");
    expect(toast).not.toHaveTextContent("ayu@example.com");
    expect(screen.queryByText("denied")).not.toBeInTheDocument();
  });
});
