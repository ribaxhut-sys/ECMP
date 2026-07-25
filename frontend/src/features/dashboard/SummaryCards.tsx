import type { DashboardHeader } from "@/lib/api/types";
import {
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Empty,
  Skeleton,
} from "@/shared/ui";

export function SummaryCards({
  header,
  loading,
}: {
  header: DashboardHeader | null;
  loading: boolean;
}) {
  if (loading) {
    return (
      <Card data-testid="dashboard-header-cards">
        <CardHeader>
          <CardTitle>Summary</CardTitle>
        </CardHeader>
        <CardBody>
          <Skeleton rows={2} />
        </CardBody>
      </Card>
    );
  }

  if (!header) {
    return (
      <Card data-testid="dashboard-header-cards">
        <CardHeader>
          <CardTitle>Summary</CardTitle>
        </CardHeader>
        <CardBody>
          <Empty
            title="No summary yet"
            description="Header metrics will appear once complaints are registered."
          />
        </CardBody>
      </Card>
    );
  }

  const cards = [
    { label: "Total Complaints", value: header.totalComplaints },
    { label: "Open Complaints", value: header.openComplaints },
    { label: "Closed Complaints", value: header.closedComplaints },
  ];

  return (
    <Card data-testid="dashboard-header-cards">
      <CardHeader>
        <CardTitle>Summary</CardTitle>
      </CardHeader>
      <CardBody>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          {cards.map((card) => (
            <div
              key={card.label}
              className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-background px-4 py-4"
            >
              <p className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary">
                {card.label}
              </p>
              <p className="mt-2 text-[length:var(--ecmp-font-heading-size)] font-semibold tabular-nums text-ecmp-text-primary">
                {card.value}
              </p>
            </div>
          ))}
        </div>
      </CardBody>
    </Card>
  );
}
