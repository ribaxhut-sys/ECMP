import { describe, expect, it, vi, beforeEach } from "vitest";
import { act, renderHook, waitFor } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import type { ReactNode } from "react";
import { useReportsData } from "./useReportsData";
import type { ReportsData } from "./loadReportsData";

const loadReportsData = vi.hoisted(() => vi.fn());
vi.mock("./loadReportsData", () => ({ loadReportsData }));

function data(total: number): ReportsData {
  return {
    summary: { total, byStatus: [{ status: "CLOSED", count: total }] },
    byStatus: [{ status: "CLOSED", count: total }],
    cycleTime: null,
  } as ReportsData;
}

function wrapper({ children }: { children: ReactNode }) {
  return (
    <NextIntlClientProvider
      locale="id"
      timeZone="Asia/Jakarta"
      messages={{ errors: {}, common: { unexpectedError: "Galat" } }}
    >
      {children}
    </NextIntlClientProvider>
  );
}

describe("useReportsData", () => {
  beforeEach(() => loadReportsData.mockReset());

  it("keeps the newest period when a second load starts before the first lands", async () => {
    // The stale "all" response resolves last; it must not overwrite the
    // numbers for the period the user actually has selected.
    let resolveAll: (value: ReportsData) => void = () => {};
    loadReportsData
      .mockImplementationOnce(
        () => new Promise<ReportsData>((resolve) => (resolveAll = resolve)),
      )
      .mockResolvedValueOnce(data(7));

    const { result } = renderHook(() => useReportsData(), { wrapper });

    await act(async () => {
      void result.current.reload("all");
      void result.current.reload("thisMonth");
    });
    await waitFor(() =>
      expect(result.current.state.status).toBe("success"),
    );
    await act(async () => {
      resolveAll(data(99));
    });

    expect(result.current.state.status).toBe("success");
    expect(
      result.current.state.status === "success"
        ? result.current.state.data.summary?.total
        : null,
    ).toBe(7);
    expect(loadReportsData).toHaveBeenCalledTimes(2);
  });
});
