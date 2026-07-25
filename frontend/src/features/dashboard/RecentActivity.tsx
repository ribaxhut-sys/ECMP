import Link from "next/link";
import type { DashboardRecentActivityItem } from "@/lib/api/types";
import {
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Empty,
  Skeleton,
  Table,
  type TableColumn,
} from "@/shared/ui";

function formatWhen(value: string): string {
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

const columns: TableColumn<DashboardRecentActivityItem>[] = [
  {
    key: "eventType",
    header: "Event Type",
    cell: (row) => (
      <span className="font-mono text-[length:var(--ecmp-font-caption-size)]">
        {row.eventType}
      </span>
    ),
  },
  {
    key: "complaintNumber",
    header: "Complaint Number",
    cell: (row) => (
      <Link
        href={`/complaints?keyword=${encodeURIComponent(row.complaintNumber)}`}
        className="font-mono text-[length:var(--ecmp-font-caption-size)] text-ecmp-primary hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus"
      >
        {row.complaintNumber}
      </Link>
    ),
  },
  {
    key: "timestamp",
    header: "Timestamp",
    cell: (row) => (
      <span className="text-ecmp-text-secondary">{formatWhen(row.timestamp)}</span>
    ),
  },
  {
    key: "actor",
    header: "Actor",
    cell: (row) => <span>{row.actor}</span>,
  },
];

export function RecentActivity({
  rows,
  loading,
}: {
  rows: DashboardRecentActivityItem[] | null;
  loading: boolean;
}) {
  if (loading) {
    return (
      <Card data-testid="dashboard-recent-activity">
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardBody>
          <Skeleton rows={5} />
        </CardBody>
      </Card>
    );
  }

  if (!rows || rows.length === 0) {
    return (
      <Card data-testid="dashboard-recent-activity">
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardBody>
          <Empty
            title="No recent activity"
            description="Latest timeline events will appear here."
          />
        </CardBody>
      </Card>
    );
  }

  return (
    <Card data-testid="dashboard-recent-activity">
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
      </CardHeader>
      <CardBody>
        <Table
          columns={columns}
          rows={rows}
          getRowKey={(row, index) =>
            `${row.complaintNumber}-${row.eventType}-${row.timestamp}-${index}`
          }
          caption="Latest timeline events"
          emptyMessage="No recent activity."
        />
      </CardBody>
    </Card>
  );
}
