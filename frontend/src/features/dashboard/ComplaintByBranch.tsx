"use client";

import { useTranslations } from "next-intl";
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

export function ComplaintByBranch({
  rows,
  loading,
}: {
  rows: BranchCount[] | null;
  loading: boolean;
}) {
  const t = useTranslations("dashboard");
  const tComplaints = useTranslations("complaints");
  const tCommon = useTranslations("common");

  const columns: TableColumn<BranchCount>[] = [
    {
      key: "branch",
      header: tComplaints("branch"),
      cell: (row) => row.branchName ?? t("unknownBranch"),
    },
    {
      key: "code",
      header: t("branchCode"),
      cell: (row) => (
        <span className="text-ecmp-text-secondary">
          {row.branchCode ?? tCommon("emDash")}
        </span>
      ),
    },
    {
      key: "total",
      header: t("total"),
      headerClassName: "text-right",
      className: "text-right tabular-nums font-medium",
      cell: (row) => row.total,
    },
  ];

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t("byBranch")}</CardTitle>
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
          <CardTitle>{t("byBranch")}</CardTitle>
        </CardHeader>
        <CardBody>
          <Empty
            title={t("noBranchData")}
            description={t("noBranchDataDescription")}
          />
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("byBranch")}</CardTitle>
      </CardHeader>
      <CardBody>
        <Table
          columns={columns}
          rows={rows}
          getRowKey={(row, index) => row.branchId ?? `unassigned-${index}`}
          caption={t("byBranch")}
          emptyMessage={t("noBranchDataDescription")}
        />
      </CardBody>
    </Card>
  );
}
