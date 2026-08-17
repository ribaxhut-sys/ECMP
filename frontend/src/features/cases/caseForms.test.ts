import { describe, expect, it } from "vitest";
import {
  emptyCreateCaseForm,
  emptyResolveCaseForm,
  emptyUpdateStatusForm,
  toAddCaseRequest,
  toCloseCaseRequest,
  toCreateCaseRequest,
  toResolveCaseRequest,
  toUpdateStatusRequest,
  validateCreateCaseForm,
  validateResolveCaseForm,
  validateUpdateStatusForm,
} from "./caseForms";
import {
  allowedStatusTargets,
  canClose,
  canOfferResolve,
  canResolve,
  caseStatusTone,
} from "./caseStatus";

describe("validateCreateCaseForm", () => {
  it("requires type, subject, description, priority", () => {
    const errors = validateCreateCaseForm(emptyCreateCaseForm());
    expect(errors.caseType).toBeTruthy();
    expect(errors.subject).toBeTruthy();
    expect(errors.description).toBeTruthy();
  });

  it("accepts minimally valid create values", () => {
    const errors = validateCreateCaseForm({
      ...emptyCreateCaseForm(),
      caseType: "SERVICE",
      subject: "Delay",
      description: "Shipment late",
      priority: "HIGH",
    });
    expect(errors).toEqual({});
  });
});

describe("toCreateCaseRequest / toAddCaseRequest", () => {
  it("maps destination unit null when empty", () => {
    const values = {
      ...emptyCreateCaseForm(),
      caseType: "BILLING",
      subject: "Charge",
      description: "Wrong fee",
      priority: "LOW",
      destinationUnitId: "  ",
    };
    expect(toCreateCaseRequest("c1", values).destinationUnitId).toBeNull();
    expect(toAddCaseRequest(values).destinationUnitId).toBeNull();
  });

  it("passes intake note and action on create", () => {
    const values = {
      ...emptyCreateCaseForm(),
      caseType: "BILLING",
      subject: "Charge",
      description: "Wrong fee",
      priority: "LOW",
    };
    expect(
      toCreateCaseRequest("c1", values, {
        note: "  Perlu Pusat  ",
        intakeAction: "escalate",
      }),
    ).toMatchObject({
      note: "Perlu Pusat",
      intakeAction: "escalate",
    });
  });
});

describe("validateUpdateStatusForm", () => {
  it("requires destination unit for ASSIGNED", () => {
    const errors = validateUpdateStatusForm({
      ...emptyUpdateStatusForm(),
      toStatus: "ASSIGNED",
    });
    expect(errors.destinationUnitId).toBeTruthy();
  });

  it("requires cancel reason and reason for CANCELLED", () => {
    const errors = validateUpdateStatusForm({
      ...emptyUpdateStatusForm(),
      toStatus: "CANCELLED",
    });
    expect(errors.cancelReason).toBeTruthy();
    expect(errors.reason).toBeTruthy();
  });
});

describe("toUpdateStatusRequest", () => {
  it("emits typed cancel payload", () => {
    expect(
      toUpdateStatusRequest({
        toStatus: "CANCELLED",
        destinationUnitId: "",
        cancelReason: "DUPLICATE",
        reason: "Same ticket",
      }),
    ).toEqual({
      toStatus: "CANCELLED",
      destinationUnitId: null,
      cancelReason: "DUPLICATE",
      reason: "Same ticket",
    });
  });
});

describe("validateResolveCaseForm", () => {
  it("requires comment for CLOSE (DEC-021)", () => {
    const errors = validateResolveCaseForm(emptyResolveCaseForm());
    expect(errors.comment).toBeTruthy();
    expect(Object.keys(errors)).toEqual(["comment"]);
  });

  it("requires rejection reason for REJECT", () => {
    const errors = validateResolveCaseForm({
      ...emptyResolveCaseForm(),
      intent: "REJECT",
      comment: "no",
    });
    expect(errors.rejectionReason).toBeTruthy();
  });

  it("skips field checks for ESCALATE intent", () => {
    expect(
      validateResolveCaseForm({
        ...emptyResolveCaseForm(),
        intent: "ESCALATE",
      }),
    ).toEqual({});
  });
});

describe("toResolveCaseRequest / toCloseCaseRequest", () => {
  it("maps CLOSE to ACCEPT with comment only", () => {
    expect(
      toResolveCaseRequest({
        intent: "CLOSE",
        comment: " ok ",
        rejectionReason: "",
      }),
    ).toEqual({
      action: "ACCEPT",
      comment: "ok",
    });
  });

  it("maps REJECT with reason", () => {
    expect(
      toResolveCaseRequest({
        intent: "REJECT",
        comment: " note ",
        rejectionReason: " incomplete ",
      }),
    ).toEqual({
      action: "REJECT",
      comment: "note",
      rejectionReason: "incomplete",
    });
  });

  it("maps empty close note to null", () => {
    expect(toCloseCaseRequest({ note: "  " })).toEqual({ note: null });
  });
});

describe("caseStatus helpers", () => {
  it("exposes Mode A PATCH targets", () => {
    expect(allowedStatusTargets("CREATED")).toEqual(
      expect.arrayContaining(["ASSIGNED", "CANCELLED"]),
    );
    expect(allowedStatusTargets("IN_PROGRESS")).toEqual(
      expect.arrayContaining(["ASSIGNED", "CANCELLED"]),
    );
    expect(allowedStatusTargets("RESOLVED")).toEqual([]);
  });

  it("gates resolve and close", () => {
    expect(canResolve("IN_PROGRESS")).toBe(true);
    expect(canResolve("ASSIGNED")).toBe(false);
    expect(canClose("RESOLVED")).toBe(true);
    expect(canClose("IN_PROGRESS")).toBe(false);
  });

  it("offers resolve CTA for active statuses", () => {
    expect(canOfferResolve("CREATED")).toBe(true);
    expect(canOfferResolve("ASSIGNED")).toBe(true);
    expect(canOfferResolve("IN_PROGRESS")).toBe(true);
    expect(canOfferResolve("RESOLVED")).toBe(false);
  });

  it("maps badge tones", () => {
    expect(caseStatusTone("RESOLVED")).toBe("success");
    expect(caseStatusTone("CANCELLED")).toBe("danger");
  });
});
