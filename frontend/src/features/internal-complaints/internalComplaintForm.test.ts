import { describe, expect, it } from "vitest";
import {
  defaultInternalComplaintForm,
  isInternalComplaintFormValid,
  validateInternalComplaintForm,
} from "./internalComplaintForm";

describe("internalComplaintForm", () => {
  it("requires title, category, description", () => {
    const errors = validateInternalComplaintForm(defaultInternalComplaintForm());
    expect(errors.title).toBe("titleRequiredError");
    expect(errors.category).toBe("categoryRequiredError");
    expect(errors.description).toBe("descriptionRequiredError");
    expect(isInternalComplaintFormValid(errors)).toBe(false);
  });

  it("passes when required fields are set", () => {
    const values = {
      ...defaultInternalComplaintForm(),
      title: "Issue",
      category: "OPERATIONAL" as const,
      description: "Details",
    };
    const errors = validateInternalComplaintForm(values);
    expect(errors).toEqual({});
    expect(isInternalComplaintFormValid(errors)).toBe(true);
  });

  it("requires a reason when a Pusat Agent (no complaints:assign) picks a destination", () => {
    const values = {
      ...defaultInternalComplaintForm(),
      title: "Issue",
      category: "OPERATIONAL" as const,
      description: "Details",
      destinationUnitId: "UPPPD-GAMBIR",
    };
    const errors = validateInternalComplaintForm(values, {
      canAssign: false,
      requireRequestReason: true,
    });
    expect(errors.requestReason).toBe("requestReasonRequiredError");
    expect(isInternalComplaintFormValid(errors)).toBe(false);
  });

  it("does not require a reason for a branch Agent sending to Pusat", () => {
    const values = {
      ...defaultInternalComplaintForm(),
      title: "Issue",
      category: "OPERATIONAL" as const,
      description: "Details",
      destinationUnitId: "PUSAT",
    };
    const errors = validateInternalComplaintForm(values, {
      canAssign: false,
      requireRequestReason: false,
    });
    expect(errors.requestReason).toBeUndefined();
    expect(isInternalComplaintFormValid(errors)).toBe(true);
  });

  it("does not require a reason for Supervisor/Manager (complaints:assign)", () => {
    const values = {
      ...defaultInternalComplaintForm(),
      title: "Issue",
      category: "OPERATIONAL" as const,
      description: "Details",
      destinationUnitId: "PUSAT",
    };
    const errors = validateInternalComplaintForm(values, { canAssign: true });
    expect(errors.requestReason).toBeUndefined();
    expect(isInternalComplaintFormValid(errors)).toBe(true);
  });

  it("does not require a reason when no destination is chosen, even without assign", () => {
    const values = {
      ...defaultInternalComplaintForm(),
      title: "Issue",
      category: "OPERATIONAL" as const,
      description: "Details",
    };
    const errors = validateInternalComplaintForm(values, { canAssign: false });
    expect(errors.requestReason).toBeUndefined();
  });

  it("rejects an unmatched related-complaint search", () => {
    const values = {
      ...defaultInternalComplaintForm(),
      title: "Issue",
      category: "OPERATIONAL" as const,
      description: "Details",
      relatedComplaintId: "bukan nomor",
    };
    const errors = validateInternalComplaintForm(values, {
      relatedUnresolved: true,
    });
    expect(errors.relatedComplaintId).toBe("relatedComplaintNotFoundError");
  });
});
