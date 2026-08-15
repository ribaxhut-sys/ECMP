import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, cleanup } from "@testing-library/react";
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
    user: { id: "officer-1" },
    roles: [],
  }),
}));

vi.mock("@/shared/providers", () => ({
  useToast: () => ({ pushSuccess: vi.fn(), pushError: vi.fn() }),
}));

const fetchCmCases = vi.fn();
const createCmCase = vi.fn();
const updateCmCaseStatus = vi.fn();
vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchCmCases: (...args: unknown[]) => fetchCmCases(...args),
    createCmCase: (...args: unknown[]) => createCmCase(...args),
    updateCmCaseStatus: (...args: unknown[]) => updateCmCaseStatus(...args),
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
    penangananHandler: "Petugas",
    penangananHandledBy: "Ditangani oleh {name}",
    penangananReassign: "Alihkan penanganan",
    penangananReassignTitle: "Alihkan ke petugas lain?",
    penangananReassignBody: "Pilih petugas.",
    penangananReassignPick: "Petugas baru",
    penangananReassignDone: "Dialihkan",
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
    handleConfirmTitle: "Tangani pengaduan",
    handleConfirmContinueBody: "Lanjutkan penanganan?",
    handleConfirmTakeoverBody: "Didaftarkan {name}. Ambil alih?",
    number: "Nomor",
    subject: "Subjek",
    status: "Status",
  },
  common: {
    success: "Sukses",
    emDash: "—",
    loadingContent: "Memuat",
    yes: "Ya",
    no: "Tidak",
    closeDialog: "Tutup",
    closeDialogOverlay: "Tutup dialog",
    actions: "Tindakan",
  },
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
    updateCmCaseStatus.mockReset();
    fetchCmCases.mockResolvedValue({ data: [], meta: { totalItems: 0 } });
    createCmCase.mockResolvedValue({
      data: {
        caseId: "new-case-1",
        caseNumber: "CASE-NEW",
        complaintId: "cmp-1",
        status: "CREATED",
      },
    });
    updateCmCaseStatus.mockResolvedValue({
      data: { caseId: "c-open", status: "IN_PROGRESS" },
    });
  });

  afterEach(() => {
    cleanup();
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
    expect(screen.getByRole("heading", { name: "Belum selesai (cabang)" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Selesai" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Lanjutkan" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "CASE-1" })).toHaveAttribute(
      "href",
      "/complaints/cm/cases/c1",
    );
    expect(screen.getByRole("link", { name: "CASE-2" })).toHaveAttribute(
      "href",
      "/complaints/cm/cases/c2",
    );
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
    expect(push).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "Ya" }));
    await waitFor(() => {
      expect(push).toHaveBeenCalledWith("/complaints/cm/cases/c1");
    });
    expect(updateCmCaseStatus).toHaveBeenCalledWith("c1", {
      toStatus: "ASSIGNED",
      reason: "HANDLE_CLAIM",
    });
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
    expect(updateCmCaseStatus).toHaveBeenCalledWith("c-open", {
      toStatus: "IN_PROGRESS",
      reason: "HANDLE_CLAIM",
    });
  });

  it("does not re-ask or re-claim when the current officer already handles", async () => {
    const user = userEvent.setup();
    fetchCmCases.mockResolvedValue({
      data: [
        {
          caseId: "c1",
          caseNumber: "CASE-1",
          complaintId: "cmp-1",
          status: "IN_PROGRESS",
          subject: "Aktif",
          handlingClaimedBy: "officer-1",
        },
      ],
      meta: { totalItems: 1 },
    });

    renderSection();
    const continueBtn = await screen.findByRole("button", { name: "Lanjutkan" });
    await user.click(continueBtn);
    expect(
      screen.queryByRole("button", { name: "Ya" }),
    ).not.toBeInTheDocument();
    await waitFor(() => {
      expect(push).toHaveBeenCalledWith("/complaints/cm/cases/c1");
    });
    expect(updateCmCaseStatus).not.toHaveBeenCalled();
  });
});
