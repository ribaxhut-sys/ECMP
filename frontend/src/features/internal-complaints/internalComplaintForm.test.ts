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
});
