/**
 * CaseStatusBadge + CaseSummaryCard smoke.
 */
import { cleanup, render, screen } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
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

const casesMessages = {
  type: "Jenis",
  priority: "Prioritas",
  unit: "Unit",
  customer: "Pelanggan",
  view: "Lihat Case",
};

function renderWithIntl(ui: React.ReactElement) {
  return render(
    <NextIntlClientProvider locale="id" messages={{ cases: casesMessages }}>
      {ui}
    </NextIntlClientProvider>,
  );
}

describe("CaseStatusBadge", () => {
  afterEach(() => cleanup());

  it("renders localized status text", () => {
    render(
      <NextIntlClientProvider
        locale="id"
        messages={{
          status: { IN_PROGRESS: "Sedang diproses" },
        }}
      >
        <CaseStatusBadge status="IN_PROGRESS" />
      </NextIntlClientProvider>,
    );
    expect(screen.getByText("Sedang diproses")).toBeInTheDocument();
  });
});

describe("CaseSummaryCard", () => {
  afterEach(() => cleanup());

  it("links to case detail", () => {
    renderWithIntl(<CaseSummaryCard caseData={sample} />);
    expect(screen.getByText("CASE-2026-000001")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /lihat case/i })).toHaveAttribute(
      "href",
      "/complaints/cm/cases/case-1",
    );
  });
});
