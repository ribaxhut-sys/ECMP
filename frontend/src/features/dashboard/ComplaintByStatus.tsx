import type { StatusCount } from "@/lib/api/types";
import {
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Empty,
  Skeleton,
} from "@/shared/ui";

export function ComplaintByStatus({
  rows,
  loading,
}: {
  rows: StatusCount[] | null;
  loading: boolean;
}) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Complaint by Status</CardTitle>
        </CardHeader>
        <CardBody>
          <Skeleton rows={4} />
        </CardBody>
      </Card>
    );
  }

  const visible = (rows ?? []).filter((row) => row.count > 0);
  if (visible.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Complaint by Status</CardTitle>
        </CardHeader>
        <CardBody>
          <Empty
            title="No status data"
            description="No status breakdown available."
          />
        </CardBody>
      </Card>
    );
  }

  const max = Math.max(...visible.map((row) => row.count), 1);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Complaint by Status</CardTitle>
      </CardHeader>
      <CardBody>
        <ul className="space-y-3">
          {visible.map((row) => (
            <li key={row.status}>
              <div className="mb-1 flex items-center justify-between text-[length:var(--ecmp-font-body-size)]">
                <span>{row.status.replaceAll("_", " ")}</span>
                <span className="tabular-nums text-ecmp-text-secondary">
                  {row.count}
                </span>
              </div>
              <div className="h-2 overflow-hidden rounded-[var(--ecmp-radius-full)] bg-ecmp-secondary-muted">
                <div
                  className="h-full rounded-[var(--ecmp-radius-full)] bg-ecmp-primary"
                  style={{ width: `${(row.count / max) * 100}%` }}
                />
              </div>
            </li>
          ))}
        </ul>
      </CardBody>
    </Card>
  );
}
