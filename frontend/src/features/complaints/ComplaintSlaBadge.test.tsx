/**
 * DEC-031 resolution-SLA badge — 30 calendar days.
 *
 * The badge must render only what the server sent. These tests pin the two
 * things most likely to go wrong quietly: warning being mistaken for a breach,
 * and an unmeasured complaint being given a guessed verdict.
 */
import { cleanup, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { renderWithProviders } from "@/test/harness";
import type { ComplaintSla } from "@/lib/api/types";
import { ComplaintSlaBadge } from "./ComplaintSlaBadge";

afterEach(cleanup);

function sla(overrides: Partial<ComplaintSla> = {}): ComplaintSla {
  return {
    status: "ON_TRACK",
    targetDays: 30,
    dueAt: "2026-02-01T00:00:00Z",
    elapsedDays: 1,
    remainingDays: 29,
    overdueDays: null,
    isWarning: false,
    ...overrides,
  };
}

function badge() {
  return screen.getByTestId("complaint-sla-badge");
}

describe("ComplaintSlaBadge", () => {
  it("renders nothing when the complaint is not measured", () => {
    const { container } = renderWithProviders(<ComplaintSlaBadge sla={null} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("shows remaining days while on track", () => {
    renderWithProviders(<ComplaintSlaBadge sla={sla()} />);
    expect(badge()).toHaveAttribute("data-sla-status", "ON_TRACK");
    expect(badge()).toHaveTextContent("29");
  });

  it("treats warning as a shade of on-track, not a breach", () => {
    // Past 80% of the target but still inside it — the promise is not broken.
    renderWithProviders(
      <ComplaintSlaBadge
        sla={sla({ isWarning: true, elapsedDays: 24, remainingDays: 6 })}
      />,
    );
    expect(badge()).toHaveAttribute("data-sla-status", "WARNING");
    expect(badge()).toHaveTextContent("6");
  });

  it("shows days over the target once overdue", () => {
    renderWithProviders(
      <ComplaintSlaBadge
        sla={sla({
          status: "OVERDUE",
          elapsedDays: 45,
          remainingDays: null,
          overdueDays: 15,
        })}
      />,
    );
    expect(badge()).toHaveAttribute("data-sla-status", "OVERDUE");
    expect(badge()).toHaveTextContent("15");
  });

  it("reports a settled complaint by how long it actually took", () => {
    renderWithProviders(
      <ComplaintSlaBadge
        sla={sla({
          status: "MET",
          elapsedDays: 10,
          remainingDays: null,
        })}
      />,
    );
    expect(badge()).toHaveAttribute("data-sla-status", "MET");
    expect(badge()).toHaveTextContent("10");
  });

  it("marks a late closure as missed", () => {
    renderWithProviders(
      <ComplaintSlaBadge
        sla={sla({
          status: "MISSED",
          elapsedDays: 45,
          remainingDays: null,
          overdueDays: 15,
        })}
      />,
    );
    expect(badge()).toHaveAttribute("data-sla-status", "MISSED");
  });

  it("carries the full target in the tooltip so a short label cannot mislead", () => {
    renderWithProviders(
      <ComplaintSlaBadge
        sla={sla({ status: "OVERDUE", elapsedDays: 35, overdueDays: 5 })}
      />,
    );
    // "lewat 5 hari" must not be readable as "the target is 5 days".
    expect(badge().getAttribute("title")).toContain("30");
  });
});
