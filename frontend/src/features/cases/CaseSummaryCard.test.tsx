/**
 * CaseStatusBadge + CaseSummaryCard smoke.
 */
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { CmCase } from "@/lib/api";
import { CaseStatusBadge } from "./CaseStatusBadge";
import { CaseSummaryCard } from "./CaseSummaryCard";

vi.mock("next/link", () => ({
  default: ({
    href,
    children,
    ...props
  }: {
    href: string;
    children: React.ReactNode;
  }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

const sample: CmCase = {
  caseId: "case-1",
  caseNumber: "CASE-2026-000001",
  complaintId: "complaint-1",
  customerId: "cust-1",
  status: "CREATED",
  caseType: "SERVICE",
  subject: "Late delivery",
  description: "Package delayed",
  priority: "HIGH",
  slaCountdownActive: false,
  createdAt: "2026-08-01T00:00:00Z",
  createdBy: "user-1",
};

describe("CaseStatusBadge", () => {
  afterEach(() => cleanup());

  it("renders status text", () => {
    render(<CaseStatusBadge status="IN_PROGRESS" />);
    expect(screen.getByText("IN_PROGRESS")).toBeInTheDocument();
  });
});

describe("CaseSummaryCard", () => {
  afterEach(() => cleanup());

  it("links to case detail", () => {
    render(<CaseSummaryCard caseData={sample} />);
    expect(screen.getByText("CASE-2026-000001")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /view case/i })).toHaveAttribute(
      "href",
      "/complaints/cm/cases/case-1",
    );
  });
});
