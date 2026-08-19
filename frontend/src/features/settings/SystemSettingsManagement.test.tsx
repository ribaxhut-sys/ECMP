/**
 * System settings (Pengaturan → Lanjutan): Edit must not persist until Save.
 */
import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { NextIntlClientProvider } from "next-intl";
import { renderWithProviders } from "@/test/harness";
import { ToastProvider } from "@/shared/providers";
import idMessages from "../../../messages/id.json";
import type { Setting } from "@/lib/api/types";

const fetchSettings = vi.fn();
const updateSetting = vi.fn();
const hasPermission = vi.fn<(permission: string) => boolean>(() => false);

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: vi.fn(), push: vi.fn(), back: vi.fn() }),
}));

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({
    hasPermission,
    user: null,
    roles: ["ADMIN"],
    status: "authenticated",
  }),
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchSettings: (...args: unknown[]) => fetchSettings(...args),
    updateSetting: (...args: unknown[]) => updateSetting(...args),
  };
});

import { SystemSettingsManagement } from "./SystemSettingsManagement";

function setting(overrides: Partial<Setting> = {}): Setting {
  return {
    id: "s-capacity",
    key: "hq.schedule.capacity_per_slot",
    value: "2",
    valueType: "INTEGER",
    category: "hq_schedule",
    visibility: "PROTECTED",
    description: "Max taxpayer arrivals accommodated per HQ schedule slot",
    createdAt: "2026-08-17T00:00:00Z",
    updatedAt: "2026-08-17T00:00:00Z",
    ...overrides,
  };
}

describe("SystemSettingsManagement", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    fetchSettings.mockReset();
    updateSetting.mockReset();
    hasPermission.mockReset().mockImplementation((permission: string) => {
      return permission === "settings:read" || permission === "settings:update";
    });
    fetchSettings.mockResolvedValue({ data: [setting()] });
    updateSetting.mockImplementation(async (_key: string, body: { value: string }) => ({
      data: setting({ value: body.value, updatedAt: "2026-08-18T00:00:00Z" }),
    }));
  });

  it("does not persist when Edit is clicked before the value changes", async () => {
    const user = userEvent.setup();
    renderWithProviders(<SystemSettingsManagement />);

    const card = await screen.findByTestId(
      "setting-key-hq.schedule.capacity_per_slot",
    );
    await user.click(within(card).getByRole("button", { name: "Edit" }));

    expect(
      await within(card).findByRole("textbox", {
        name: /Arrivals per slot/i,
      }),
    ).toHaveValue("2");
    expect(within(card).getByRole("button", { name: "Save" })).toBeInTheDocument();
    expect(updateSetting).not.toHaveBeenCalled();
    expect(screen.queryByRole("status", { name: /saved/i })).not.toBeInTheDocument();
  });

  it("does not call the API when Save is clicked with the same value", async () => {
    const user = userEvent.setup();
    renderWithProviders(<SystemSettingsManagement />);

    const card = await screen.findByTestId(
      "setting-key-hq.schedule.capacity_per_slot",
    );
    await user.click(within(card).getByRole("button", { name: "Edit" }));
    await user.click(within(card).getByRole("button", { name: "Save" }));

    await waitFor(() => {
      expect(within(card).getByRole("button", { name: "Edit" })).toBeInTheDocument();
    });
    expect(updateSetting).not.toHaveBeenCalled();
  });

  it("persists only after the value changes and Save is clicked", async () => {
    const user = userEvent.setup();
    renderWithProviders(<SystemSettingsManagement />);

    const card = await screen.findByTestId(
      "setting-key-hq.schedule.capacity_per_slot",
    );
    await user.click(within(card).getByRole("button", { name: "Edit" }));
    const input = await within(card).findByRole("textbox", {
      name: /Arrivals per slot/i,
    });
    await user.clear(input);
    await user.type(input, "4");
    await user.click(within(card).getByRole("button", { name: "Save" }));

    await waitFor(() => {
      expect(updateSetting).toHaveBeenCalledWith(
        "hq.schedule.capacity_per_slot",
        { value: "4" },
      );
    });
  });

  it("renders Indonesian labels when the locale is id", async () => {
    render(
      <NextIntlClientProvider
        locale="id"
        messages={idMessages}
        timeZone="Asia/Jakarta"
        now={new Date("2026-08-01T00:00:00Z")}
      >
        <ToastProvider>
          <SystemSettingsManagement />
        </ToastProvider>
      </NextIntlClientProvider>,
    );

    const card = await screen.findByTestId(
      "setting-key-hq.schedule.capacity_per_slot",
    );
    expect(within(card).getByText("Kapasitas per slot")).toBeInTheDocument();
    expect(
      within(card).getByText(
        "Jumlah maksimum kedatangan wajib pajak per slot jadwal HQ.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByText("Jadwal HQ")).toBeInTheDocument();
    expect(
      screen.queryByText(
        "Max taxpayer arrivals accommodated per HQ schedule slot",
      ),
    ).not.toBeInTheDocument();
  });
});
