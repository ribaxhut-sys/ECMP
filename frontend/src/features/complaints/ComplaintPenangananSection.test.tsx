import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NextIntlClientProvider } from "next-intl";
import type { ComponentProps } from "react";
import { ComplaintPenangananSection } from "./ComplaintPenangananSection";

const push = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push, replace: vi.fn() }),
}));

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({
    hasPermission: (p: string) =>
      p === "complaints:read" || p === "complaints:create",
    user: null,
    roles: [],
  }),
}));

vi.mock("@/shared/providers", () => ({
  useToast: () => ({ pushSuccess: vi.fn(), pushError: vi.fn() }),
}));

const fetchCmCases = vi.fn();
const createCmCase = vi.fn();
vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchCmCases: (...args: unknown[]) => fetchCmCases(...args),
    createCmCase: (...args: unknown[]) => createCmCase(...args),
  };
});

vi.mock("@/features/cases/CreateCaseDialog", () => ({
  CreateCaseDialog: ({ open }: { open: boolean }) =>
    open ? <div>CreateCaseDialogOpen</div> : null,
}));

const messages = {
  complaints: {
    penangananTitle: "Penanganan",
    penangananDescription: "Desc",
    penangananSummary: "{open} terbuka · {pusat} ke Pusat · {done} selesai",
    penangananSummaryOpen: "{count} terbuka",
    penangananSummaryPusat: "{count} ke Pusat",
    penangananSummaryDone: "{count} selesai",
    penangananSummaryNone: "Belum ada penanganan",
    penangananGroupOpen: "Belum selesai (cabang)",
    penangananGroupPusat: "Menunggu / di Pusat",
    penangananGroupDone: "Selesai",
    penangananGroupCancelled: "Dibatalkan",
    penangananItemLabel: "Penanganan {n}",
    penangananNoSubject: "Tanpa subjek",
    penangananContinue: "Lanjutkan",
    penangananView: "Lihat",
    penangananEscalate: "Ajukan eskalasi ke Pusat",
    penangananStart: "Mulai penanganan",
    penangananStartAnother: "Mulai penanganan baru",
    penangananEmptyTitle: "Belum ada penanganan",
    penangananEmptyDescription: "Mulai dulu",
    penangananEmptyReadOnlyDescription: "Read only",
    penangananEmptyHqTitle: "Menunggu eskalasi",
    penangananEmptyHqDescription: "HQ empty",
    penangananEmptyClosedTitle: "Ditutup",
    penangananEmptyClosedDescription: "Closed empty",
    penangananLoadError: "Gagal",
    penangananCreated: "OK {number}",
    penangananHqPathTitle: "HQ path",
    penangananHqPathDescription: "HQ desc",
    penangananStatusCreated: "Baru",
    penangananStatusAssigned: "Ditugaskan",
    penangananStatusInProgress: "Sedang dikerjakan",
    penangananStatusPending: "Menunggu",
    penangananStatusEscalated: "Dieskalasi",
    penangananStatusResolved: "Terselesaikan",
    penangananStatusClosed: "Ditutup",
    penangananStatusCancelled: "Dibatalkan",
    penangananStatusUnknown: "{status}",
    penangananListClosed: "Ditutup",
    penangananListHqWaiting: "Menunggu eskalasi",
  },
  common: { success: "Sukses", emDash: "—", loadingContent: "Memuat" },
  cases: {
    type: "Tipe",
    priority: "Prioritas",
    unit: "Unit",
    customer: "Wajib Pajak",
    view: "Lihat",
  },
};

function renderSection(
  props: Partial<ComponentProps<typeof ComplaintPenangananSection>> = {},
) {
  return render(
    <NextIntlClientProvider locale="id" messages={messages}>
      <ComplaintPenangananSection
        complaintId="cmp-1"
        allowStart
        allowEscalate={false}
        {...props}
      />
    </NextIntlClientProvider>,
  );
}

describe("ComplaintPenangananSection", () => {
  beforeEach(() => {
    push.mockReset();
    fetchCmCases.mockReset();
    createCmCase.mockReset();
    fetchCmCases.mockResolvedValue({ data: [], meta: { totalItems: 0 } });
    createCmCase.mockResolvedValue({
      data: {
        caseId: "new-case-1",
        caseNumber: "CASE-NEW",
        complaintId: "cmp-1",
        status: "CREATED",
      },
    });
  });

  it("groups open and done penanganan", async () => {
    fetchCmCases.mockResolvedValue({
      data: [
        {
          caseId: "c1",
          caseNumber: "CASE-1",
          complaintId: "cmp-1",
          status: "IN_PROGRESS",
          subject: "Tagihan",
        },
        {
          caseId: "c2",
          caseNumber: "CASE-2",
          complaintId: "cmp-1",
          status: "CLOSED",
          subject: "Lama",
        },
      ],
      meta: { totalItems: 2 },
    });

    renderSection();

    await waitFor(() => {
      expect(screen.getByText("1 terbuka · 1 selesai")).toBeInTheDocument();
    });
    expect(screen.getByText("Belum selesai (cabang)")).toBeInTheDocument();
    expect(screen.getByText("Selesai")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Lanjutkan" })).toBeInTheDocument();
  });

  it("continues to case detail route", async () => {
    const user = userEvent.setup();
    fetchCmCases.mockResolvedValue({
      data: [
        {
          caseId: "c1",
          caseNumber: "CASE-1",
          complaintId: "cmp-1",
          status: "ASSIGNED",
          subject: "X",
        },
      ],
      meta: { totalItems: 1 },
    });

    const { unmount } = renderSection();
    const continueBtn = await screen.findByRole("button", { name: "Lanjutkan" });
    await user.click(continueBtn);
    expect(push).toHaveBeenCalledWith("/complaints/cm/cases/c1");
    unmount();
  });

  it("manageRequestToken creates case and opens case workspace", async () => {
    const { rerender } = renderSection({
      manageRequestToken: 0,
      seed: {
        category: "BILLING",
        subject: "Tagihan",
        description: "Detail tagihan",
        priority: "HIGH",
      },
    });
    await waitFor(() => {
      expect(screen.getByText("Belum ada penanganan")).toBeInTheDocument();
    });
    // Agent empty state: no duplicate Empty CTA — parent "Tangani" drives create.
    expect(
      screen.queryByRole("button", { name: "Mulai penanganan" }),
    ).not.toBeInTheDocument();

    rerender(
      <NextIntlClientProvider locale="id" messages={messages}>
        <ComplaintPenangananSection
          complaintId="cmp-1"
          allowStart
          allowEscalate={false}
          manageRequestToken={1}
          seed={{
            category: "BILLING",
            subject: "Tagihan",
            description: "Detail tagihan",
            priority: "HIGH",
          }}
        />
      </NextIntlClientProvider>,
    );

    await waitFor(() => {
      expect(createCmCase).toHaveBeenCalled();
      expect(push).toHaveBeenCalledWith("/complaints/cm/cases/new-case-1");
    });
  });

  it("manageRequestToken opens existing open case workspace", async () => {
    fetchCmCases.mockResolvedValue({
      data: [
        {
          caseId: "c-open",
          caseNumber: "CASE-OPEN",
          complaintId: "cmp-1",
          status: "IN_PROGRESS",
          subject: "Aktif",
        },
      ],
      meta: { totalItems: 1 },
    });

    const { rerender } = renderSection({ manageRequestToken: 0 });
    await screen.findByRole("button", { name: "Lanjutkan" });

    rerender(
      <NextIntlClientProvider locale="id" messages={messages}>
        <ComplaintPenangananSection
          complaintId="cmp-1"
          allowStart
          allowEscalate={false}
          manageRequestToken={1}
        />
      </NextIntlClientProvider>,
    );

    await waitFor(() => {
      expect(push).toHaveBeenCalledWith("/complaints/cm/cases/c-open");
    });
    expect(createCmCase).not.toHaveBeenCalled();
  });
});
