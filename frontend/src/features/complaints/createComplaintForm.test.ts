import { describe, expect, it } from "vitest";
import {
  composeCmBatch1Description,
  createEmptyComplaintForm,
  defaultReportedAtLocal,
  newCmBatch1IdempotencyKey,
  newCmBatch1StagingToken,
  parseCmBatch1Description,
  toCmBatch1CreateRequest,
  validateCmBatch1CreateForm,
  validateCreateComplaintForm,
} from "./createComplaintForm";

const VALID_UUID = "11111111-1111-1111-1111-111111111111";

describe("defaultReportedAtLocal", () => {
  it("formats a fixed date as datetime-local", () => {
    const value = defaultReportedAtLocal(new Date("2026-07-30T15:04:00"));
    expect(value).toBe("2026-07-30T15:04");
  });
});

describe("composeCmBatch1Description", () => {
  it("appends resolution when present", () => {
    expect(composeCmBatch1Description("Laporan", "Sudah diganti")).toBe(
      "Laporan\n\n---\nPenyelesaian:\nSudah diganti",
    );
  });

  it("appends escalation reason when escalating", () => {
    const composed = composeCmBatch1Description("Laporan", "Butuh pusat", {
      escalate: true,
    });
    expect(composed).toContain("Alasan eskalasi:\nButuh pusat");
    expect(composed).toContain("Ajuan eskalasi:");
    expect(composed).not.toContain("Penyelesaian:");
  });
});

describe("parseCmBatch1Description", () => {
  it("parses narrative and escalation reason", () => {
    const parsed = parseCmBatch1Description(
      "Keluhan mesin\n\n---\nAlasan eskalasi:\nPerlu parameter Pusat\n\n---\nAjuan eskalasi:\nMenunggu\n\n---\nCatatan Supervisor:\nLanjut ke Pusat\n\n---\nBatalkan Eskalasi:\nPelanggan setuju cabang",
    );
    expect(parsed.narrative).toBe("Keluhan mesin");
    expect(parsed.escalationReason).toBe("Perlu parameter Pusat");
    expect(parsed.branchResolution).toBeNull();
    expect(parsed.supervisorNote).toBe("Lanjut ke Pusat");
    expect(parsed.cancellationNote).toBe("Pelanggan setuju cabang");
  });

  it("parses legacy Batal Eskalasi section", () => {
    const parsed = parseCmBatch1Description(
      "Keluhan\n\n---\nBatal Eskalasi:\nAlasan lama",
    );
    expect(parsed.cancellationNote).toBe("Alasan lama");
  });
});

describe("validateCreateComplaintForm", () => {
  it("requires customer, subject, description, priority, and branch", () => {
    const errors = validateCreateComplaintForm(createEmptyComplaintForm());
    expect(errors.customerId).toBeTruthy();
    expect(errors.subject).toBeTruthy();
    expect(errors.description).toBeTruthy();
    expect(errors.priority).toBeTruthy();
    expect(errors.branchId).toBeTruthy();
  });

  it("accepts a minimally valid form", () => {
    const errors = validateCreateComplaintForm({
      ...createEmptyComplaintForm({ branchId: VALID_UUID }),
      customerId: VALID_UUID,
      customerName: "Ada",
      subject: "Printer offline",
      description: "Cannot print invoices",
      priority: "HIGH",
    });
    expect(errors).toEqual({});
  });

  it("rejects non-UUID customer id", () => {
    const errors = validateCreateComplaintForm({
      ...createEmptyComplaintForm({ branchId: VALID_UUID }),
      customerId: "not-a-uuid",
      customerName: "Ada",
      subject: "Printer offline",
      description: "Cannot print invoices",
      priority: "HIGH",
    });
    expect(errors.customerId).toBe("customerIdInvalid");
  });

  it("rejects subject and description over catalog limits", () => {
    const errors = validateCreateComplaintForm({
      ...createEmptyComplaintForm({ branchId: VALID_UUID }),
      customerId: VALID_UUID,
      customerName: "Ada",
      subject: "x".repeat(201),
      description: "y".repeat(5001),
      priority: "MEDIUM",
    });
    expect(errors.subject).toBe("subjectMax");
    expect(errors.description).toBe("descriptionMax");
  });
});

describe("validateCmBatch1CreateForm", () => {
  it("requires customer, subject, and description (category defaults to GENERAL)", () => {
    const errors = validateCmBatch1CreateForm(createEmptyComplaintForm());
    expect(errors.customerId).toBeTruthy();
    expect(errors.subject).toBeTruthy();
    expect(errors.description).toBeTruthy();
    expect(errors.category).toBeUndefined();
    expect(errors.channel).toBeUndefined();
  });

  it("rejects empty channel when cleared", () => {
    const errors = validateCmBatch1CreateForm({
      ...createEmptyComplaintForm(),
      channel: "",
    });
    expect(errors.channel).toBe("channelRequired");
  });

  it("accepts opaque customer id (not UUID-only)", () => {
    const errors = validateCmBatch1CreateForm({
      ...createEmptyComplaintForm(),
      customerId: "CUST-LAB-001",
      customerName: "Ada",
      subject: "Printer offline",
      description: "Cannot print invoices",
      category: "SERVICE",
      channel: "BRANCH",
    });
    expect(errors).toEqual({});
  });

  it("maps to API-500 body without priority unless escalate", () => {
    const body = toCmBatch1CreateRequest({
      ...createEmptyComplaintForm({ branchId: VALID_UUID }),
      customerId: "CUST-LAB-001",
      customerName: "Ada",
      subject: "Printer offline",
      description: "Cannot print invoices",
      resolution: "Replaced toner",
      category: "SERVICE",
      channel: "CALL",
      priority: "HIGH",
    });
    expect(body).toEqual({
      customerId: "CUST-LAB-001",
      category: "SERVICE",
      channel: "CALL",
      subject: "Printer offline",
      description:
        "Cannot print invoices\n\n---\nPenyelesaian:\nReplaced toner",
      recordingUnitId: VALID_UUID,
    });
    expect(body.priority).toBeUndefined();
  });

  it("prefers recordingUnitCode over branchId UUID for recordingUnitId", () => {
    const body = toCmBatch1CreateRequest(
      {
        ...createEmptyComplaintForm({ branchId: VALID_UUID }),
        customerId: "CUST-1",
        category: "BILLING",
        channel: "BRANCH",
        subject: "Subject",
        description: "Narrative",
        resolution: "Resolved at branch",
      },
      { closeAtBranch: true, recordingUnitCode: "UPPPD-TANAH-ABANG" },
    );
    expect(body.recordingUnitId).toBe("UPPPD-TANAH-ABANG");
  });

  it("includes priority when escalating", () => {
    const body = toCmBatch1CreateRequest(
      {
        ...createEmptyComplaintForm({ branchId: VALID_UUID }),
        customerId: "CUST-LAB-001",
        customerName: "Ada",
        subject: "Printer offline",
        description: "Cannot print",
        resolution: "Butuh konfigurasi Pusat",
        category: "SERVICE",
        channel: "CALL",
        priority: "HIGH",
      },
      { escalate: true },
    );
    expect(body.priority).toBe("HIGH");
    expect(body.description).toContain("Alasan eskalasi:");
    expect(body.description).toContain("Butuh konfigurasi Pusat");
    expect(body.description).toContain("Ajuan eskalasi:");
    expect(body.intakeDisposition).toBe("ESCALATE_PENDING_APPROVAL");
  });

  it("defaults category to GENERAL when empty", () => {
    const body = toCmBatch1CreateRequest({
      ...createEmptyComplaintForm(),
      customerId: "CUST-1",
      customerName: "Ada",
      subject: "S",
      description: "D",
      category: "",
      channel: "BRANCH",
    });
    expect(body.category).toBe("GENERAL");
  });

  it("includes stagingToken when provided (FR-004 bind on create)", () => {
    const body = toCmBatch1CreateRequest(
      {
        ...createEmptyComplaintForm(),
        customerId: "CUST-LAB-001",
        customerName: "Ada",
        subject: "Printer offline",
        description: "Cannot print invoices",
        category: "SERVICE",
        channel: "CALL",
      },
      { stagingToken: "STG-abc123" },
    );
    expect(body.stagingToken).toBe("STG-abc123");
  });

  it("maps escalate flag into description with alasan eskalasi", () => {
    const body = toCmBatch1CreateRequest(
      {
        ...createEmptyComplaintForm(),
        customerId: "CUST-LAB-001",
        customerName: "Ada",
        subject: "Printer offline",
        description: "Cannot print",
        resolution: "Cabang tidak punya akses parameter",
        category: "SERVICE",
        channel: "CALL",
      },
      { escalate: true },
    );
    expect(body.description).toContain("Alasan eskalasi:");
    expect(body.description).toContain("Ajuan eskalasi:");
    expect(body.intakeDisposition).toBe("ESCALATE_PENDING_APPROVAL");
  });

  it("sets BRANCH_CLOSED disposition when closing at branch", () => {
    const body = toCmBatch1CreateRequest(
      {
        ...createEmptyComplaintForm(),
        customerId: "CUST-LAB-001",
        customerName: "Ada",
        subject: "Printer offline",
        description: "Cannot print",
        resolution: "Toner diganti",
        category: "SERVICE",
        channel: "CALL",
      },
      { closeAtBranch: true },
    );
    expect(body.intakeDisposition).toBe("BRANCH_CLOSED");
    expect(body.description).toContain("Penyelesaian:");
  });
});

describe("newCmBatch1IdempotencyKey", () => {
  it("returns a non-empty key", () => {
    expect(newCmBatch1IdempotencyKey().length).toBeGreaterThan(8);
  });
});

describe("newCmBatch1StagingToken", () => {
  it("returns STG-prefixed token", () => {
    const token = newCmBatch1StagingToken();
    expect(token.startsWith("STG-")).toBe(true);
    expect(token.length).toBeGreaterThan(8);
  });
});
