import { beforeEach, describe, expect, it, vi } from "vitest";
import { createEmptyComplaintForm } from "./createComplaintForm";

const createCmCase = vi.fn();
const escalateCmCaseToPusat = vi.fn();
const closeCmCase = vi.fn();
const recordCmCaseAcceptance = vi.fn();
const resolveCmCase = vi.fn();
const updateCmCaseStatus = vi.fn();

vi.mock("@/lib/api/cmCase", () => ({
  createCmCase: (...args: unknown[]) => createCmCase(...args),
  escalateCmCaseToPusat: (...args: unknown[]) => escalateCmCaseToPusat(...args),
  closeCmCase: (...args: unknown[]) => closeCmCase(...args),
  recordCmCaseAcceptance: (...args: unknown[]) =>
    recordCmCaseAcceptance(...args),
  resolveCmCase: (...args: unknown[]) => resolveCmCase(...args),
  updateCmCaseStatus: (...args: unknown[]) => updateCmCaseStatus(...args),
}));

import { createIntakeCasesForRegisteredComplaint } from "./intakeCaseDrafts";

describe("createIntakeCasesForRegisteredComplaint — escalate-to-Pusat", () => {
  beforeEach(() => {
    createCmCase.mockReset();
    escalateCmCaseToPusat.mockReset();
    closeCmCase.mockReset();
    recordCmCaseAcceptance.mockReset();
    resolveCmCase.mockReset();
    updateCmCaseStatus.mockReset();
    createCmCase.mockResolvedValue({
      data: { caseId: "case-1", status: "CREATED", owningUnitId: "JKT01" },
    });
    escalateCmCaseToPusat.mockResolvedValue({
      data: { caseId: "case-1", escalatedToPusat: true },
    });
  });

  it("calls API-520 on the created Case when action is escalate", async () => {
    const values = {
      ...createEmptyComplaintForm({ channel: "BRANCH" }),
      subject: "Mesin error",
      description: "Uraian case 1",
      priority: "HIGH" as const,
      resolution: "Tidak dapat diselesaikan di cabang.",
    };
    await createIntakeCasesForRegisteredComplaint({
      complaintId: "cmp-1",
      values,
      extraDrafts: [],
      destinationUnitId: "JKT01",
      rows: [
        {
          id: "primary",
          n: 1,
          subject: values.subject,
          description: values.description,
          priority: "HIGH",
          note: "Tidak dapat diselesaikan di cabang.",
          action: "escalate",
        },
      ],
    });
    expect(createCmCase).toHaveBeenCalledTimes(1);
    expect(escalateCmCaseToPusat).toHaveBeenCalledWith("case-1", {
      reason: "Tidak dapat diselesaikan di cabang.",
    });
  });

  it("does not call API-520 when the Case is only registered", async () => {
    const values = {
      ...createEmptyComplaintForm({ channel: "BRANCH" }),
      subject: "Mesin error",
      description: "Uraian case 1",
      resolution: "Sudah diinfokan.",
    };
    await createIntakeCasesForRegisteredComplaint({
      complaintId: "cmp-1",
      values,
      extraDrafts: [],
      destinationUnitId: "JKT01",
      rows: [
        {
          id: "primary",
          n: 1,
          subject: values.subject,
          description: values.description,
          priority: "MEDIUM",
          note: "Sudah diinfokan.",
          action: "register",
        },
      ],
    });
    expect(createCmCase).toHaveBeenCalledTimes(1);
    expect(escalateCmCaseToPusat).not.toHaveBeenCalled();
  });
});
