import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, cleanup, fireEvent } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import { CmBatch1ConfirmationView } from "./CmBatch1ConfirmationView";
import type { CmBatch1ComplaintResponse, CmBatch1IntakeHistoryEntry } from "@/lib/api";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({
    hasPermission: (p: string) =>
      p === "complaints:read" || p === "complaints:create",
    user: { id: "officer-1", branchId: null },
    roles: [],
  }),
}));

vi.mock("@/shared/providers", () => ({
  useToast: () => ({ pushSuccess: vi.fn(), pushError: vi.fn() }),
}));

const fetchCmBatch1Complaint = vi.fn();
const fetchCmBatch1ComplaintHistory = vi.fn();
const fetchBranches = vi.fn();
vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchCmBatch1Complaint: (...args: unknown[]) => fetchCmBatch1Complaint(...args),
    fetchCmBatch1ComplaintHistory: (...args: unknown[]) =>
      fetchCmBatch1ComplaintHistory(...args),
    fetchBranches: (...args: unknown[]) => fetchBranches(...args),
  };
});

let lastPenangananProps: Record<string, unknown> | null = null;
vi.mock("./ComplaintPenangananSection", () => ({
  ComplaintPenangananSection: (props: Record<string, unknown>) => {
    lastPenangananProps = props;
    return <div>PenangananSection</div>;
  },
  CASE_ESCALATE_ACTION_QUERY: "escalate",
  PENANGANAN_FOCUS_QUERY: "penanganan",
  scrollToPenangananSection: vi.fn(),
}));

vi.mock("./CmBatch1BoundAttachmentsCard", () => ({
  CmBatch1BoundAttachmentsCard: () => <div>AttachmentsCard</div>,
}));

const messages = {
  common: {
    breadcrumb: "Navigasi",
    loadingContent: "Memuat…",
    emDash: "—",
    yes: "Ya",
    no: "Tidak",
    cancel: "Batal",
    showingItems: "{from}-{to} dari {total}",
    pageOf: "Hal {page}/{totalPages}",
    previous: "Sebelumnya",
    next: "Berikutnya",
  },
  priority: { LOW: "Rendah", MEDIUM: "Sedang", HIGH: "Tinggi", CRITICAL: "Kritis" },
  validation: { priorityRequired: "Prioritas wajib diisi" },
  complaints: {
    home: "Beranda",
    title: "Pengaduan",
    confirmation: "Konfirmasi",
    accessRestricted: "Akses dibatasi",
    confirmationAccessDescription: "Butuh akses",
    couldNotLoadComplaint: "Gagal memuat",
    complaintRegistered: "Pengaduan terdaftar",
    confirmationDescription: "Pengaduan sudah dicatat.",
    intakeClosedByUnitTitle: "Pengaduan telah selesai dan ditutup oleh {unit}",
    intakeClosedByUnitDescription: "Pengaduan berhasil ditangani dan ditutup di unit ini.",
    intakeClosedByHqTitle: "Pengaduan telah selesai dan ditutup oleh Kantor Pusat",
    intakeClosedByHqDescription: "Pengaduan berhasil diselesaikan melalui jalur Pusat.",
    penangananInProgressTitle: "Pengaduan masih dalam penanganan ({name})",
    penangananInProgressDescription: "Pengaduan sedang berjalan di unit penanganan.",
    complaintStatusLoading: "Memuat status pengaduan…",
    intakeEscalateBannerTitle: "Ajuan eskalasi tercatat",
    intakeEscalateBannerDescription: "Menunggu persetujuan.",
    escalationApproved: "Eskalasi disetujui",
    escalationApprovedPageDescription: "Eskalasi disetujui. Pusat belum menerima.",
    hqPathAcceptedPageTitle: "Diterima Pusat — belum dijadwalkan",
    hqPathAcceptedPageDescription: "Pusat sudah menerima.",
    hqPathScheduledPageTitle: "Jadwal kedatangan wajib pajak",
    hqPathScheduledPageDescription: "Pusat sudah menetapkan jadwal.",
    returnedToBranchBannerTitle: "Dikembalikan ke cabang",
    returnedToBranchBannerDescription: "Lengkapi dokumen.",
    hqScheduledBranchNotifyTitle: "Kedatangan dijadwalkan",
    hqScheduledBranchNotifyBody: "{date} {time}",
    registrationDetails: "Rincian pendaftaran",
    subject: "Subjek",
    complaintNumber: "Nomor pengaduan",
    status: "Status",
    statusClosed: "Ditutup",
    statusInProgress: "Dalam proses",
    registered: "Terdaftar",
    registrationUnitLabel: "Pendaftaran",
    registeredAtLabel: "Tanggal pendaftaran",
    registeredByLabel: "Didaftarkan oleh",
    customer: "Wajib pajak",
    priority: "Prioritas",
    replayed: "Diputar ulang (idempoten)",
    category: "Kategori",
    awaitingApproval: "Menunggu persetujuan",
    escalationRejected: "Eskalasi ditolak",
    escalationCancelled: "Eskalasi dibatalkan",
    returnedToBranch: "Dikembalikan — lengkapi dokumen",
    hqScheduled: "Kedatangan dijadwalkan",
    intakeHistoryTitle: "Riwayat Pengaduan",
    intakeHistoryDescriptionLabel: "Deskripsi",
    intakeHistoryNoteLabel: "Catatan",
    intakeHistoryClosedNoteLabel: "Catatan ditutup",
    intakeEventLogDescription: "Urut waktu, satu baris per kejadian.",
    intakeEventLogEmpty: "Belum ada kejadian tercatat.",
    intakeEventLogUnavailable: "Log kejadian tidak dapat dimuat",
    intakeEventLogUnavailableDescription: "Muat ulang halaman.",
    intakeEventLogExpandAll: "Buka semua",
    intakeEventLogCollapseAll: "Tutup semua",
    intakeEventLogShowNote: "Lihat catatan",
    intakeEventLogHideNote: "Sembunyikan catatan",
    intakeEventNoteEmpty: "Tidak ada catatan",
    registered_: "Terdaftar",
    registeredLabel: "Terdaftar",
    tagEscalationRequested: "Eskalasi diajukan",
    tagBranchClosed: "Ditutup di cabang",
    tagHqAccepted: "Diterima Pusat",
    tagHqReturned: "Dikembalikan Pusat",
    tagHqScheduled: "Kedatangan dijadwalkan",
    tagCaseCreated: "Case dibuat",
    submitRegisterCase: "Daftarkan Case ini",
    submitCloseCase: "Selesaikan Case ini",
    submitEscalateCase: "Ajukan eskalasi Case ini",
    tagCaseWorkStarted: "Pengerjaan dimulai",
    tagCaseAssigned: "Case ditugaskan",
    tagCaseCancelled: "Case dibatalkan",
    tagCaseStatusChanged: "Status case diubah",
    tagCaseClosed: "Pengaduan ditutup",
    tagCaseResolved: "Case diselesaikan",
    tagHandlingContinued: "Melanjutkan penanganan pengaduan",
    tagHandlingTakenOver: "Mengambil alih penanganan pengaduan",
    tagEscalationReRequested: "Eskalasi diajukan ulang",
    tagHistoryOther: "Lainnya",
    escalationApprovedToast: "x",
    escalationApprovedToastDescription: "x",
    escalationRejectedToast: "x",
    escalationRejectedToastDescription: "x",
    escalationCancelledToast: "x",
    escalationCancelledToastDescription: "x",
    reRequestEscalationToast: "x",
    reRequestEscalationToastDescription: "x",
    hqAcceptScheduledToast: "x",
    hqAcceptScheduledToastDescription: "x",
    hqReturnedToast: "x",
    hqReturnedToastDescription: "x",
    hqScheduledToast: "x",
    hqScheduledToastDescription: "x",
    closedSuccess: "x",
    closedSuccessDescription: "x",
    escalateSuccess: "x",
    escalateSuccessDescription: "x",
    createdSuccess: "x",
    registeredDescription: "x",
    closedByActor: "Ditutup oleh {name}",
    priorityTag: "{value}",
    registerAnother: "Daftarkan lagi",
    backToComplaints: "Kembali ke Pengaduan",
    manageCases: "Tangani pengaduan",
    manageCasesHint: "Konfirmasi dulu.",
    manageCasesHintExisting: "Konfirmasi dulu.",
    penangananHandledBy: "Ditangani oleh {name}",
    handleConfirmTitle: "Tangani pengaduan",
    handleConfirmContinueBody: "Lanjutkan penanganan?",
    handleConfirmTakeoverBody: "Didaftarkan {name}. Ambil alih?",
    approveEscalation: "Setujui",
    rejectEscalation: "Tolak",
    cancelEscalation: "Batalkan eskalasi",
    reRequestEscalation: "Ajukan ulang eskalasi",
    hqAcceptAndSchedule: "Terima & jadwalkan",
    hqReturn: "Kembalikan",
    hqRescheduleArrival: "Jadwal ulang",
    hqScheduleArrival: "Jadwalkan kedatangan",
    approveEscalationTitle: "x",
    approveEscalationBody: "x",
    approveEscalationNoteLabel: "x",
    approveEscalationNoteHint: "x",
    approveEscalationPriorityLabel: "x",
    approveEscalationPriorityHint: "x",
    selectPriorityPlaceholder: "x",
    rejectEscalationTitle: "x",
    rejectEscalationBody: "x",
    rejectEscalationNoteLabel: "x",
    rejectEscalationNoteHint: "x",
    cancelEscalationTitle: "x",
    cancelEscalationBody: "x",
    cancelEscalationNoteLabel: "x",
    cancelEscalationNoteHint: "x",
    reRequestEscalationTitle: "x",
    reRequestEscalationBody: "x",
    reRequestEscalationReasonLabel: "x",
    reRequestEscalationReasonHint: "x",
    reRequestEscalationPriorityLabel: "x",
    reRequestEscalationPriorityHint: "x",
    hqAcceptAndScheduleTitle: "x",
    hqAcceptAndScheduleBody: "x",
    hqArrivalDateLabel: "x",
    hqArrivalTimeLabel: "x",
    hqAcceptScheduleNoteLabel: "x",
    hqAcceptScheduleNoteHint: "x",
    hqReturnTitle: "x",
    hqReturnBody: "x",
    hqReturnReasonLabel: "x",
    hqReturnNoteLabel: "x",
    hqReturnNoteHint: "x",
    hqReturnReason_MISSING_ATTACHMENT: "x",
    hqReturnReason_INCOMPLETE_CHRONOLOGY: "x",
    hqReturnReason_UNCLEAR_CUSTOMER_DATA: "x",
    hqReturnReason_WRONG_CATEGORY_OR_ROUTING: "x",
    hqReturnReason_ADDITIONAL_EVIDENCE_REQUIRED: "x",
    hqReturnReason_OTHER: "x",
    hqScheduleTitle: "x",
    hqScheduleBody: "x",
    hqArrivalNoteLabel: "x",
    hqArrivalNoteHint: "x",
    hqScheduleSave: "x",
    hqArrivalValue: "{date} {time}",
    hqArrivalSlotLabel: "{weekday}, {date} pukul {time}",
  },
};

function renderView(complaintId = "cmp-1") {
  return render(
    <NextIntlClientProvider locale="id" messages={messages}>
      <CmBatch1ConfirmationView complaintId={complaintId} />
    </NextIntlClientProvider>,
  );
}

function baseComplaint(
  overrides: Partial<CmBatch1ComplaintResponse> = {},
): CmBatch1ComplaintResponse {
  return {
    complaintId: "cmp-1",
    complaintNumber: "CMP-0001",
    status: "REGISTERED",
    customerId: "cust-1",
    customerDisplayName: "Budi Simanjuntak",
    customerNumber: "3200000000000021",
    caseCreated: false,
    replayed: false,
    subject: "Keluhan layanan",
    description: "",
    intakeNarrative: "Narasi keluhan",
    branchResolution: "Sudah diinfokan ke wajib pajak",
    owningUnitId: "branch-1",
    createdByName: "Ani",
    createdAt: "2026-08-10T01:00:00Z",
    ...overrides,
  };
}

beforeEach(() => {
  fetchCmBatch1Complaint.mockReset();
  fetchCmBatch1ComplaintHistory.mockReset();
  fetchBranches.mockReset();
  fetchCmBatch1ComplaintHistory.mockResolvedValue({ data: [] });
  fetchBranches.mockResolvedValue({
    data: [{ id: "branch-1", code: "JKT01", name: "Cabang Jakarta Selatan" }],
  });
  lastPenangananProps = null;
});

afterEach(() => {
  cleanup();
});

describe("CmBatch1ConfirmationView — page title matrix", () => {
  it("titles a branch close with the registering unit's name, not the word 'cabang'", async () => {
    fetchCmBatch1Complaint.mockResolvedValue({
      data: baseComplaint({ status: "CLOSED", intakeDisposition: "BRANCH_CLOSED" }),
    });
    renderView();
    await waitFor(() =>
      expect(
        screen.getByRole("heading", {
          name: "Pengaduan telah selesai dan ditutup oleh Cabang Jakarta Selatan",
        }),
      ).toBeInTheDocument(),
    );
  });

  it("titles an HQ close (status CLOSED, disposition not BRANCH_CLOSED) with Kantor Pusat", async () => {
    fetchCmBatch1Complaint.mockResolvedValue({
      data: baseComplaint({ status: "CLOSED", intakeDisposition: "ESCALATE_APPROVED" }),
    });
    renderView();
    await waitFor(() =>
      expect(
        screen.getByRole("heading", {
          name: "Pengaduan telah selesai dan ditutup oleh Kantor Pusat",
        }),
      ).toBeInTheDocument(),
    );
  });

  it("does not duplicate the closed title in a banner Alert", async () => {
    fetchCmBatch1Complaint.mockResolvedValue({
      data: baseComplaint({ status: "CLOSED", intakeDisposition: "BRANCH_CLOSED" }),
    });
    renderView();
    await waitFor(() => screen.getByRole("heading", { level: 1 }));
    expect(
      screen.getAllByText("Pengaduan telah selesai dan ditutup oleh Cabang Jakarta Selatan"),
    ).toHaveLength(1);
  });

  it("titles an open, claimed complaint with the handler's name and a neutral description", async () => {
    fetchCmBatch1Complaint.mockResolvedValue({ data: baseComplaint() });
    renderView();
    await waitFor(() => expect(lastPenangananProps).not.toBeNull());
    (
      lastPenangananProps!.onPenangananSnapshot as (s: unknown) => void
    )({
      loading: false,
      openCount: 1,
      totalCount: 1,
      handlingClaimedBy: "officer-2",
      handlingClaimedByName: "Budi",
    });
    await waitFor(() =>
      expect(
        screen.getByRole("heading", {
          name: "Pengaduan masih dalam penanganan (Budi)",
        }),
      ).toBeInTheDocument(),
    );
    expect(
      screen.getByText("Pengaduan sedang berjalan di unit penanganan."),
    ).toBeInTheDocument();
    expect(screen.queryByText("Ditangani oleh Budi")).not.toBeInTheDocument();
  });

  it("titles a scheduled HQ arrival as taxpayer visit schedule, not waiting for escalation", async () => {
    fetchCmBatch1Complaint.mockResolvedValue({
      data: baseComplaint({
        status: "IN_PROGRESS",
        intakeDisposition: "HQ_SCHEDULED",
        caseCreated: true,
        hqAcceptedAt: "2026-08-17T10:00:00Z",
        hqArrivalDate: "2026-08-20",
        hqArrivalTime: "09:30",
      }),
    });
    renderView();
    await waitFor(() =>
      expect(
        screen.getByRole("heading", { name: "Jadwal kedatangan wajib pajak" }),
      ).toBeInTheDocument(),
    );
    expect(screen.getAllByText("Kamis, 20 Agustus 2026 pukul 09.30").length).toBeGreaterThanOrEqual(
      1,
    );
    expect(screen.queryByText("Menunggu persetujuan.")).not.toBeInTheDocument();
    expect(lastPenangananProps?.hqArrivalDate).toBe("2026-08-20");
    expect(lastPenangananProps?.hqArrivalTime).toBe("09:30");
  });

  it("keeps the HQ-approved title and hides cabang escalate CTAs while a Case is still bound", async () => {
    fetchCmBatch1Complaint.mockResolvedValue({
      data: baseComplaint({
        status: "IN_PROGRESS",
        intakeDisposition: "ESCALATE_APPROVED",
        caseCreated: true,
      }),
    });
    renderView();
    await waitFor(() => expect(lastPenangananProps).not.toBeNull());
    expect(lastPenangananProps!.allowEscalate).toBe(false);
    expect(lastPenangananProps!.onRequestHqEscalation).toBeUndefined();
    (
      lastPenangananProps!.onPenangananSnapshot as (s: unknown) => void
    )({
      loading: false,
      openCount: 0,
      totalCount: 1,
      handlingClaimedBy: "officer-dewi",
      handlingClaimedByName: "Dewi Hidayat",
    });
    await waitFor(() =>
      expect(
        screen.getByRole("heading", { name: "Eskalasi disetujui" }),
      ).toBeInTheDocument(),
    );
    expect(
      screen.queryByRole("button", { name: "Ajukan ulang eskalasi" }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByText("Ditangani oleh Dewi Hidayat"),
    ).not.toBeInTheDocument();
  });

  it("keeps a single page-level re-request CTA after cancel, not a duplicate in Penanganan", async () => {
    fetchCmBatch1Complaint.mockResolvedValue({
      data: baseComplaint({
        status: "IN_PROGRESS",
        intakeDisposition: "ESCALATE_CANCELLED",
        caseCreated: true,
      }),
    });
    renderView();
    await waitFor(() =>
      expect(
        screen.getByRole("button", { name: "Ajukan ulang eskalasi" }),
      ).toBeInTheDocument(),
    );
    expect(lastPenangananProps!.allowEscalate).toBe(false);
    expect(lastPenangananProps!.onRequestHqEscalation).toBeUndefined();
  });

  it("titles an open, unclaimed complaint as registered", async () => {
    fetchCmBatch1Complaint.mockResolvedValue({ data: baseComplaint() });
    renderView();
    await waitFor(() => expect(lastPenangananProps).not.toBeNull());
    (
      lastPenangananProps!.onPenangananSnapshot as (s: unknown) => void
    )({
      loading: false,
      openCount: 0,
      totalCount: 0,
      handlingClaimedBy: null,
      handlingClaimedByName: null,
    });
    await waitFor(() =>
      expect(
        screen.getByRole("heading", { name: "Pengaduan terdaftar" }),
      ).toBeInTheDocument(),
    );
  });
});

describe("CmBatch1ConfirmationView — section layout", () => {
  it("renders no 'Rincian pendaftaran' section heading", async () => {
    fetchCmBatch1Complaint.mockResolvedValue({ data: baseComplaint() });
    renderView();
    await waitFor(() => screen.getByText("CMP-0001"));
    expect(screen.queryByText("Rincian pendaftaran")).not.toBeInTheDocument();
  });

  it("shows the subject, description and note in a content block", async () => {
    fetchCmBatch1Complaint.mockResolvedValue({ data: baseComplaint() });
    renderView();
    await waitFor(() => screen.getByText("Keluhan layanan"));
    expect(screen.getByText("Narasi keluhan")).toBeInTheDocument();
    expect(screen.getByText("Sudah diinfokan ke wajib pajak")).toBeInTheDocument();
    expect(screen.getByText("Catatan")).toBeInTheDocument();
    expect(
      screen.getByText("Budi Simanjuntak / 3200000000000021"),
    ).toBeInTheDocument();
  });

  it("labels the note as 'Catatan ditutup' once the complaint is closed", async () => {
    fetchCmBatch1Complaint.mockResolvedValue({
      data: baseComplaint({ status: "CLOSED", intakeDisposition: "BRANCH_CLOSED" }),
    });
    renderView();
    await waitFor(() => screen.getByText("Sudah diinfokan ke wajib pajak"));
    expect(screen.getByText("Catatan ditutup")).toBeInTheDocument();
    expect(screen.queryByText("Catatan")).not.toBeInTheDocument();
  });

  it("renders the attachments card before the Riwayat Pengaduan section", async () => {
    fetchCmBatch1Complaint.mockResolvedValue({ data: baseComplaint() });
    const { container } = renderView();
    await waitFor(() => screen.getByText("AttachmentsCard"));
    const html = container.innerHTML;
    expect(html.indexOf("AttachmentsCard")).toBeLessThan(
      html.indexOf("Riwayat Pengaduan"),
    );
  });

  it("renders the history section titled 'Riwayat Pengaduan'", async () => {
    fetchCmBatch1Complaint.mockResolvedValue({ data: baseComplaint() });
    renderView();
    await waitFor(() =>
      expect(screen.getByText("Riwayat Pengaduan")).toBeInTheDocument(),
    );
  });
});

describe("CmBatch1ConfirmationView — history event filter", () => {
  it("hides HANDLING_CONTINUED and HANDLING_TAKEN_OVER rows from this page's log", async () => {
    fetchCmBatch1Complaint.mockResolvedValue({ data: baseComplaint() });
    const history: CmBatch1IntakeHistoryEntry[] = [
      {
        entryId: "1",
        eventCode: "REGISTERED",
        eventType: "REGISTERED",
        occurredAt: "2026-08-10T01:00:00Z",
        actorName: "Ani",
      },
      {
        entryId: "2",
        eventCode: "HANDLING_TAKEN_OVER",
        eventType: "HANDLING_TAKEN_OVER",
        occurredAt: "2026-08-11T01:00:00Z",
        actorName: "Budi",
      },
      {
        entryId: "3",
        eventCode: "HANDLING_CONTINUED",
        eventType: "HANDLING_CONTINUED",
        occurredAt: "2026-08-12T01:00:00Z",
        actorName: "Budi",
      },
    ];
    fetchCmBatch1ComplaintHistory.mockResolvedValue({ data: history });
    renderView();
    await waitFor(() => screen.getByText("Riwayat Pengaduan"));
    expect(screen.getByText("1-1 dari 1")).toBeInTheDocument();
    expect(
      screen.queryByText("Melanjutkan penanganan pengaduan"),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByText("Mengambil alih penanganan pengaduan"),
    ).not.toBeInTheDocument();
  });

  it("shows the taxpayer visit slot on the HQ arrival history header, not the later complaint SoT", async () => {
    fetchCmBatch1Complaint.mockResolvedValue({
      data: baseComplaint({
        status: "IN_PROGRESS",
        intakeDisposition: "HQ_SCHEDULED",
        hqAcceptedAt: "2026-08-17T10:00:00Z",
        hqArrivalDate: "2026-08-21",
        hqArrivalTime: "14:00",
        hqArrivalNote: "Catatan terbaru",
      }),
    });
    fetchCmBatch1ComplaintHistory.mockResolvedValue({
      data: [
        {
          entryId: "h1",
          eventCode: "HQ_ARRIVAL_SCHEDULED",
          eventType: "HqArrivalScheduled",
          occurredAt: "2026-08-17T02:00:00Z",
          actorName: "Pusat",
          arrivalDate: "2026-08-20",
          arrivalTime: "09:30",
          note: "Bawa dokumen asli",
        },
      ] satisfies CmBatch1IntakeHistoryEntry[],
    });
    renderView();
    await waitFor(() =>
      expect(screen.getAllByText("Kedatangan dijadwalkan").length).toBeGreaterThan(
        0,
      ),
    );
    expect(
      screen.getByText("Kamis, 20 Agustus 2026 pukul 09.30"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Jumat, 21 Agustus 2026 pukul 14.00"),
    ).toBeInTheDocument();
    expect(screen.queryByText("Bawa dokumen asli")).not.toBeInTheDocument();
    expect(screen.queryByText("Catatan terbaru")).not.toBeInTheDocument();
    expect(screen.getByText("Lihat catatan")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Lihat catatan"));
    expect(screen.getByText("Bawa dokumen asli")).toBeInTheDocument();
    expect(screen.queryByText("Catatan terbaru")).not.toBeInTheDocument();
  });
});
