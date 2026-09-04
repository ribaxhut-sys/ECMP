import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NextIntlClientProvider } from "next-intl";
import { AddCaseToComplaintView } from "./AddCaseToComplaintView";

const push = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push, replace: vi.fn() }),
}));

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({
    hasPermission: (p: string) =>
      p === "complaints:read" || p === "complaints:create",
    user: { id: "officer-1", branchId: "UNIT-A" },
    roles: [],
  }),
}));

vi.mock("@/shared/providers", () => ({
  useToast: () => ({ pushSuccess: vi.fn(), pushError: vi.fn() }),
}));

const fetchCmBatch1Complaint = vi.fn();
const fetchCmCases = vi.fn();
const addCmCase = vi.fn();
const createCmCase = vi.fn();

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchCmBatch1Complaint: (...args: unknown[]) =>
      fetchCmBatch1Complaint(...args),
    fetchCmCases: (...args: unknown[]) => fetchCmCases(...args),
    addCmCase: (...args: unknown[]) => addCmCase(...args),
    createCmCase: (...args: unknown[]) => createCmCase(...args),
  };
});

vi.mock("./KnowledgeMentionTextarea", () => ({
  KnowledgeMentionTextarea: ({
    label,
    value,
    onChange,
    name,
  }: {
    label: string;
    value: string;
    onChange: (next: string) => void;
    name: string;
  }) => (
    <label>
      {label}
      <textarea
        name={name}
        aria-label={label}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </label>
  ),
}));

const messages = {
  common: {
    home: "Beranda",
    cancel: "Batal",
    retry: "Coba lagi",
    success: "Sukses",
    create: "Buat",
    breadcrumb: "Breadcrumb",
    loadingContent: "Memuat",
  },
  complaints: {
    title: "Pengaduan",
    createComplaint: "Buat Pengaduan",
    penangananAddCase: "Tambah Case",
    addCasePageTitle: "Tambah Case",
    addCasePageDescription: "Deskripsi halaman",
    addCaseParentBannerTitle: "Pengaduan induk",
    addCaseParentBannerDescription:
      "{number} · {status} · Case {count}/{max}",
    addCaseBlockedTitle: "Tidak dapat menambah Case",
    addCaseBlockedClosed: "Sudah ditutup",
    addCaseBlockedHq: "Jalur Pusat",
    addCaseBlockedMax: "Batas {max}",
    addCaseMissingId: "ID hilang",
    addCaseBackToComplaint: "Kembali ke pengaduan",
    complaintNumber: "Nomor pengaduan",
    statusLabel: "Status",
    statusClosed: "Ditutup",
    statusInProgress: "Dalam proses",
    registered: "Terdaftar",
    unableToLoadDetail: "Gagal muat",
    createRestrictedTitle: "Dibatasi",
    createAccessRestrictedDescription: "Tidak boleh",
    penangananCreated: "OK {number}",
  },
  cases: {
    unableToLoad: "Gagal Case",
    caseType: "Jenis Case",
    category: "Kategori",
    subject: "Subjek",
    description: "Deskripsi",
    priority: "Prioritas",
    low: "Rendah",
    medium: "Sedang",
    high: "Tinggi",
    critical: "Kritis",
    destinationUnitOptional: "Unit",
    destinationUnitHint: "Hint",
    branchUnitAssignedTitle: "Unit terkunci",
    branchUnitAssignedDescription: "Cabang Anda",
  },
  validation: {
    caseTypeRequired: "Jenis wajib",
    subjectRequired: "Subjek wajib",
    descriptionRequired: "Deskripsi wajib",
    priorityRequired: "Prioritas wajib",
  },
  errors: {},
};

function renderView(complaintId: string) {
  return render(
    <NextIntlClientProvider locale="id" messages={messages}>
      <AddCaseToComplaintView complaintId={complaintId} />
    </NextIntlClientProvider>,
  );
}

describe("AddCaseToComplaintView", () => {
  beforeEach(() => {
    push.mockReset();
    fetchCmBatch1Complaint.mockReset();
    fetchCmCases.mockReset();
    addCmCase.mockReset();
    createCmCase.mockReset();
    fetchCmBatch1Complaint.mockResolvedValue({
      data: {
        complaintId: "cmp-1",
        complaintNumber: "TAB-2608-0001",
        status: "IN_PROGRESS",
        customerId: "cust-1",
        caseCreated: true,
        replayed: false,
        category: "BILLING",
        subject: "Tagihan",
        description: "Detail",
        intakeNarrative: "Uraian WP",
        priority: "HIGH",
        owningUnitId: "UNIT-A",
      },
    });
    fetchCmCases.mockResolvedValue({
      data: [
        {
          caseId: "c1",
          caseNumber: "CASE-1",
          complaintId: "cmp-1",
          status: "IN_PROGRESS",
          subject: "Satu",
        },
      ],
      meta: { totalItems: 1 },
    });
    addCmCase.mockResolvedValue({
      data: { caseId: "c2", caseNumber: "CASE-2", complaintId: "cmp-1" },
    });
    createCmCase.mockResolvedValue({
      data: { caseId: "c1", caseNumber: "CASE-1", complaintId: "cmp-1" },
    });
  });

  afterEach(() => {
    cleanup();
  });

  it("shows missing-id block without loading a complaint", async () => {
    renderView("");
    expect(await screen.findByText("ID hilang")).toBeInTheDocument();
    expect(fetchCmBatch1Complaint).not.toHaveBeenCalled();
  });

  it("blocks CLOSED complaints", async () => {
    fetchCmBatch1Complaint.mockResolvedValue({
      data: {
        complaintId: "cmp-1",
        complaintNumber: "TAB-2608-0001",
        status: "CLOSED",
        customerId: "cust-1",
        caseCreated: true,
        replayed: false,
      },
    });
    renderView("cmp-1");
    expect(await screen.findByText("Sudah ditutup")).toBeInTheDocument();
    expect(screen.queryByLabelText("Jenis Case")).not.toBeInTheDocument();
  });

  it("submits addCmCase and returns to complaint detail", async () => {
    const user = userEvent.setup();
    renderView("cmp-1");
    const submit = await screen.findByRole("button", { name: "Tambah Case" });
    expect(screen.getAllByText("TAB-2608-0001").length).toBeGreaterThan(0);
    await user.click(submit);

    await waitFor(() => {
      expect(addCmCase).toHaveBeenCalled();
    });
    expect(addCmCase.mock.calls[0]?.[0]).toBe("cmp-1");
    expect(addCmCase.mock.calls[0]?.[1]).toMatchObject({
      caseType: "BILLING",
      subject: "Tagihan",
      description: "Uraian WP",
      priority: "HIGH",
    });
    expect(createCmCase).not.toHaveBeenCalled();
    expect(push).toHaveBeenCalledWith("/complaints/cm/cmp-1");
  });

  it("uses createCmCase when the complaint has no Cases yet", async () => {
    fetchCmCases.mockResolvedValue({ data: [], meta: { totalItems: 0 } });
    const user = userEvent.setup();
    renderView("cmp-1");
    await screen.findByRole("button", { name: "Tambah Case" });
    await user.click(screen.getByRole("button", { name: "Tambah Case" }));
    await waitFor(() => {
      expect(createCmCase).toHaveBeenCalled();
    });
    expect(addCmCase).not.toHaveBeenCalled();
  });
});
