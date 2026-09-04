/**
 * API-507 Batch-1 staged upload FormData wiring (no network).
 */
import { beforeEach, describe, expect, it, vi } from "vitest";

const apiRequest = vi.fn();

vi.mock("./client", () => ({
  apiRequest: (...args: unknown[]) => apiRequest(...args),
}));

describe("uploadCmBatch1Attachment", () => {
  beforeEach(() => {
    apiRequest.mockReset();
    apiRequest.mockResolvedValue({
      data: {
        attachmentId: "att-1",
        platformAttachmentId: "plat-1",
        status: "STAGED",
        classification: "customer_evidence",
        stagingToken: "STG-test",
        originalName: "evidence.pdf",
        mimeType: "application/pdf",
        sizeBytes: 12,
        checksumSha256: "abc",
        createdAt: "2026-07-31T00:00:00Z",
      },
    });
  });

  it("posts multipart to /api/v1/attachments with Batch-1 fields", async () => {
    const { uploadCmBatch1Attachment } = await import("./cmBatch1");
    const file = new File(["hello"], "evidence.pdf", {
      type: "application/pdf",
    });

    await uploadCmBatch1Attachment({
      file,
      classification: "customer_evidence",
      stagingToken: "STG-test",
    });

    expect(apiRequest).toHaveBeenCalledTimes(1);
    const [path, options] = apiRequest.mock.calls[0] as [
      string,
      { method: string; body: FormData },
    ];
    expect(path).toBe("/api/v1/attachments");
    expect(options.method).toBe("POST");
    expect(options.body).toBeInstanceOf(FormData);
    expect(options.body.get("classification")).toBe("customer_evidence");
    expect(options.body.get("stagingToken")).toBe("STG-test");
    expect(options.body.get("file")).toBeInstanceOf(File);
    expect(options.body.get("aggregateType")).toBeNull();
    expect(options.body.get("caseId")).toBeNull();
  });

  it("sends caseId when pinning a bound upload to a Case", async () => {
    const { uploadCmBatch1Attachment } = await import("./cmBatch1");
    const file = new File(["hello"], "case1.pdf", { type: "application/pdf" });
    await uploadCmBatch1Attachment({
      file,
      classification: "customer_evidence",
      complaintId: "11111111-1111-1111-1111-111111111111",
      caseId: "22222222-2222-2222-2222-222222222222",
    });
    const [, options] = apiRequest.mock.calls[0] as [
      string,
      { method: string; body: FormData },
    ];
    expect(options.body.get("complaintId")).toBe(
      "11111111-1111-1111-1111-111111111111",
    );
    expect(options.body.get("caseId")).toBe(
      "22222222-2222-2222-2222-222222222222",
    );
  });

  it("voids via DELETE with reason query (API-512)", async () => {
    apiRequest.mockResolvedValue({
      data: {
        attachmentId: "att-1",
        platformAttachmentId: "plat-1",
        status: "VOID",
        classification: "customer_evidence",
        originalName: "evidence.pdf",
        mimeType: "application/pdf",
        sizeBytes: 12,
        checksumSha256: "abc",
        voidReason: "uat_cleanup",
        createdAt: "2026-07-31T00:00:00Z",
      },
    });
    const { voidCmBatch1Attachment } = await import("./cmBatch1");
    await voidCmBatch1Attachment("att-1", "uat_cleanup");
    expect(apiRequest).toHaveBeenCalledWith(
      "/api/v1/attachments/att-1?reason=uat_cleanup",
      { method: "DELETE" },
    );
  });

  it("lists Aggregate complaint attachments (API-509)", async () => {
    apiRequest.mockResolvedValue({ data: [], meta: { page: 1, pageSize: 100, totalItems: 0 } });
    const { fetchCmBatch1ComplaintAttachments } = await import("./cmBatch1");
    await fetchCmBatch1ComplaintAttachments("11111111-1111-1111-1111-111111111111");
    expect(apiRequest).toHaveBeenCalledWith(
      "/api/v1/cm/complaints/11111111-1111-1111-1111-111111111111/attachments?page=1&pageSize=100",
    );
  });
});
