import { describe, expect, it } from "vitest";
import {
  ADD_CASE_QUERY_MODE,
  MAX_CASES_PER_COMPLAINT,
  addCaseToComplaintHref,
  isAddCaseMode,
} from "./addCaseToComplaint";

describe("addCaseToComplaint", () => {
  it("builds the Mode A deep-link", () => {
    expect(addCaseToComplaintHref("5fb652ba-9b0d-4cfb-b6c1-1c9461545524")).toBe(
      `/complaints/new?mode=${ADD_CASE_QUERY_MODE}&complaintId=5fb652ba-9b0d-4cfb-b6c1-1c9461545524`,
    );
  });

  it("encodes special characters in complaintId", () => {
    expect(addCaseToComplaintHref("a/b")).toBe(
      `/complaints/new?mode=${ADD_CASE_QUERY_MODE}&complaintId=a%2Fb`,
    );
  });

  it("recognizes add-case mode case-insensitively", () => {
    expect(isAddCaseMode("add-case")).toBe(true);
    expect(isAddCaseMode("ADD-CASE")).toBe(true);
    expect(isAddCaseMode("create")).toBe(false);
    expect(isAddCaseMode(null)).toBe(false);
  });

  it("keeps the BQ-003 Case cap", () => {
    expect(MAX_CASES_PER_COMPLAINT).toBe(5);
  });
});
