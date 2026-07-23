import type { BranchCount } from "@/lib/api/types";
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

const columns: TableColumn<BranchCount>[] = [
  {
    key: "branch",
    header: "Branch",
    cell: (row) => row.branchName ?? "Unassigned",
  },
  {
    key: "code",
    header: "Code",
    cell: (row) => (
      <span className="text-ecmp-text-secondary">{row.branchCode ?? "—"}</span>
    ),
  },
  {
    key: "total",
    header: "Total",
    headerClassName: "text-right",
    className: "text-right tabular-nums font-medium",
    cell: (row) => row.total,
  },
];

export function ComplaintByBranch({
  rows,
  loading,
}: {
  rows: BranchCount[] | null;
  loading: boolean;
}) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Complaint by Branch</CardTitle>
        </CardHeader>
        <CardBody>
          <Skeleton rows={4} />
        </CardBody>
      </Card>
    );
  }

  if (!rows || rows.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Complaint by Branch</CardTitle>
        </CardHeader>
        <CardBody>
          <Empty
            title="No branch data"
            description="No branch activity yet."
          />
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Complaint by Branch</CardTitle>
      </CardHeader>
      <CardBody>
        <Table
          columns={columns}
          rows={rows}
          getRowKey={(row, index) => row.branchId ?? `unassigned-${index}`}
          caption="Complaints by branch"
          emptyMessage="No branch activity yet."
        />
      </CardBody>
    </Card>
  );
}
