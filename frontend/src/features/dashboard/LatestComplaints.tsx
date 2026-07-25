import Link from "next/link";
import type { Complaint } from "@/lib/api/types";
import {
  Badge,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Empty,
  Skeleton,
  Table,
  type BadgeTone,
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

function priorityTone(priority: string): BadgeTone {
  switch (priority) {
    case "CRITICAL":
      return "danger";
    case "HIGH":
      return "warning";
    case "MEDIUM":
      return "info";
    default:
      return "neutral";
  }
}

const columns: TableColumn<Complaint>[] = [
  {
    key: "number",
    header: "Number",
    cell: (row) => (
      <Link
        href={`/complaints/${row.id}`}
        className="font-mono text-[length:var(--ecmp-font-caption-size)] text-ecmp-primary hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus"
      >
        {row.complaintNumber}
      </Link>
    ),
  },
  {
    key: "subject",
    header: "Subject",
    cell: (row) => <span className="line-clamp-2">{row.subject}</span>,
  },
  {
    key: "status",
    header: "Status",
    cell: (row) => (
      <Badge tone="neutral">{row.status.replaceAll("_", " ")}</Badge>
    ),
  },
  {
    key: "priority",
    header: "Priority",
    cell: (row) => (
      <Badge tone={priorityTone(row.priority)}>{row.priority}</Badge>
    ),
  },
  {
    key: "created",
    header: "Created",
    cell: (row) => (
      <span className="text-ecmp-text-secondary">{formatWhen(row.createdAt)}</span>
    ),
  },
];

export function LatestComplaints({
  rows,
  loading,
}: {
  rows: Complaint[] | null;
  loading: boolean;
}) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Latest Complaints</CardTitle>
        </CardHeader>
        <CardBody>
          <Skeleton rows={5} />
        </CardBody>
      </Card>
    );
  }

  if (!rows || rows.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Latest Complaints</CardTitle>
        </CardHeader>
        <CardBody>
          <Empty
            title="No complaints"
            description="No complaints found."
          />
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Latest Complaints</CardTitle>
      </CardHeader>
      <CardBody>
        <Table
          columns={columns}
          rows={rows}
          getRowKey={(row) => row.id}
          caption="Latest complaints"
          emptyMessage="No complaints found."
        />
      </CardBody>
    </Card>
  );
}
