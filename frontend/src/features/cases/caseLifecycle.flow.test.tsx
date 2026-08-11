/**
 * CAP-008 Mode A end-to-end flow (mocked API):
 * Create → Update Status → Resolve → Close.
 */
import { cleanup, fireEvent, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { CmCase } from "@/lib/api";
import { renderWithProviders } from "@/test/harness";

const createCmCase = vi.fn();
const updateCmCaseStatus = vi.fn();
const resolveCmCase = vi.fn();
const closeCmCase = vi.fn();
const fetchCmCase = vi.fn();
const hasPermission = vi.fn(() => true);
const noop = () => undefined;

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn() }),
  usePathname: () => "/complaints/cm/complaint-1/cases",
  useSearchParams: () => new URLSearchParams(),
}));

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

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({
    hasPermission,
    user: null,
  }),
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    createCmCase: (...args: unknown[]) => createCmCase(...args),
    addCmCase: vi.fn(),
    fetchCmCase: (...args: unknown[]) => fetchCmCase(...args),
    updateCmCaseStatus: (...args: unknown[]) => updateCmCaseStatus(...args),
    resolveCmCase: (...args: unknown[]) => resolveCmCase(...args),
    closeCmCase: (...args: unknown[]) => closeCmCase(...args),
  };
});

import { CreateCaseDialog } from "./CreateCaseDialog";
import { UpdateStatusDialog } from "./UpdateStatusDialog";
import { ResolveCaseDialog } from "./ResolveCaseDialog";
import { CloseCaseDialog } from "./CloseCaseDialog";
import { clearKnownCaseIds } from "./caseSessionRegistry";

const COMPLAINT_ID = "11111111-1111-1111-1111-111111111111";

function baseCase(overrides: Partial<CmCase> = {}): CmCase {
  return {
    caseId: "case-flow-1",
    caseNumber: "CASE-2026-000099",
    complaintId: COMPLAINT_ID,
    customerId: "cust-1",
    status: "CREATED",
    caseType: "SERVICE",
    subject: "Flow subject",
    description: "Flow description",
    priority: "MEDIUM",
    owningUnitId: null,
    slaCountdownActive: false,
    createdAt: "2026-08-01T00:00:00Z",
    createdBy: "user-1",
    ...overrides,
  };
}

function setFieldValue(label: RegExp, value: string) {
  const el = screen.getByLabelText(label);
  fireEvent.change(el, { target: { value } });
}

describe("CAP-008 case lifecycle flow", () => {
  afterEach(() => {
    cleanup();
    clearKnownCaseIds(COMPLAINT_ID);
  });

  beforeEach(() => {
    createCmCase.mockReset();
    updateCmCaseStatus.mockReset();
    resolveCmCase.mockReset();
    closeCmCase.mockReset();
    fetchCmCase.mockReset();
    hasPermission.mockImplementation(() => true);
    sessionStorage.clear();
  });

  it("Create → Update Status → Resolve → Close", async () => {
    const user = userEvent.setup();
    let current = baseCase({ status: "CREATED" });

    createCmCase.mockResolvedValue({ data: current });
    const onCreated = vi.fn();
    const { unmount } = renderWithProviders(
      <CreateCaseDialog
        open
        onClose={noop}
        complaintId={COMPLAINT_ID}
        mode="create"
        onCreated={onCreated}
      />,
    );

    setFieldValue(/case type/i, "SERVICE");
    setFieldValue(/^subject/i, "Flow subject");
    setFieldValue(/description/i, "Flow description");
    await user.click(screen.getByRole("button", { name: /^start branch work$/i }));

    await waitFor(() => expect(createCmCase).toHaveBeenCalled());
    expect(onCreated).toHaveBeenCalledWith(
      expect.objectContaining({ caseId: "case-flow-1", status: "CREATED" }),
    );

    unmount();
    current = baseCase({
      status: "ASSIGNED",
      owningUnitId: "unit-ops",
    });
    updateCmCaseStatus.mockResolvedValue({ data: current });
    const onUpdated = vi.fn();
    const statusRender = renderWithProviders(
      <UpdateStatusDialog
        open
        onClose={noop}
        caseData={baseCase({ status: "CREATED" })}
        onUpdated={onUpdated}
      />,
    );

    await user.selectOptions(screen.getByLabelText(/target status/i), "ASSIGNED");
    setFieldValue(/branch unit/i, "unit-ops");
    await user.click(screen.getByRole("button", { name: /update status/i }));

    await waitFor(() => expect(updateCmCaseStatus).toHaveBeenCalled());
    expect(updateCmCaseStatus).toHaveBeenCalledWith(
      "case-flow-1",
      expect.objectContaining({
        toStatus: "ASSIGNED",
        destinationUnitId: "unit-ops",
      }),
    );
    expect(onUpdated).toHaveBeenCalledWith(
      expect.objectContaining({ status: "ASSIGNED" }),
    );

    statusRender.unmount();
    current = baseCase({
      status: "IN_PROGRESS",
      owningUnitId: "unit-ops",
    });
    updateCmCaseStatus.mockResolvedValueOnce({ data: current });
    const progressRender = renderWithProviders(
      <UpdateStatusDialog
        open
        onClose={noop}
        caseData={baseCase({
          status: "ASSIGNED",
          owningUnitId: "unit-ops",
        })}
        onUpdated={vi.fn()}
      />,
    );
    await user.selectOptions(
      screen.getByLabelText(/target status/i),
      "IN_PROGRESS",
    );
    await user.click(screen.getByRole("button", { name: /update status/i }));
    await waitFor(() =>
      expect(updateCmCaseStatus).toHaveBeenLastCalledWith(
        "case-flow-1",
        expect.objectContaining({ toStatus: "IN_PROGRESS" }),
      ),
    );

    progressRender.unmount();
    current = baseCase({
      status: "RESOLVED",
      owningUnitId: "unit-ops",
      resolution: {
        resolutionId: "res-1",
        resolutionCode: "FIX",
        summary: "Fixed",
        status: "ACCEPTED",
        comment: "Done",
      },
    });
    resolveCmCase.mockResolvedValue({ data: current });
    const onResolved = vi.fn();
    const resolveRender = renderWithProviders(
      <ResolveCaseDialog
        open
        onClose={noop}
        caseId="case-flow-1"
        onResolved={onResolved}
      />,
    );

    setFieldValue(/comment/i, "Done");
    setFieldValue(/resolution code/i, "FIX");
    setFieldValue(/^summary/i, "Fixed");
    await user.click(
      screen.getByRole("button", { name: /submit resolution/i }),
    );

    await waitFor(() => expect(resolveCmCase).toHaveBeenCalled());
    expect(resolveCmCase).toHaveBeenCalledWith(
      "case-flow-1",
      expect.objectContaining({
        action: "ACCEPT",
        resolutionCode: "FIX",
        summary: "Fixed",
      }),
    );
    expect(onResolved).toHaveBeenCalledWith(
      expect.objectContaining({ status: "RESOLVED" }),
    );

    resolveRender.unmount();
    current = baseCase({
      status: "CLOSED",
      owningUnitId: "unit-ops",
      closedAt: "2026-08-01T12:00:00Z",
    });
    closeCmCase.mockResolvedValue({ data: current });
    const onClosed = vi.fn();
    renderWithProviders(
      <CloseCaseDialog
        open
        onClose={noop}
        caseId="case-flow-1"
        onClosed={onClosed}
      />,
    );

    await user.click(screen.getByRole("button", { name: /^close case$/i }));
    await waitFor(() => expect(closeCmCase).toHaveBeenCalled());
    expect(onClosed).toHaveBeenCalledWith(
      expect.objectContaining({ status: "CLOSED" }),
    );
  });
});
