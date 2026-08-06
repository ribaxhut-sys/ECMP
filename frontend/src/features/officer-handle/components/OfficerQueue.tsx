"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import {
  Empty,
  PageHeader,
  Select,
  type SelectOption,
} from "@/shared/ui";
import { WorkspaceLayout } from "@/shared/layouts/shell";
import { getShellBatchOverlineKey, isBatchAtLeast } from "@/shared/config/uiBatch";
import { useAssignmentRepository } from "@/features/supervisor-assign/mock/useAssignmentRepository";
import {
  hasEscalationContextRequest,
  hasRejectContinuity,
  hasReopenContinuity,
} from "@/features/supervisor-assign/mock/assignmentRepository";
import type { MockComplaintStatus } from "@/features/supervisor-assign/mock/assignmentRepository";
import { OfficerQueueCard } from "./OfficerQueueCard";

type StatusFilter = "ALL" | "ASSIGNED" | "IN_PROGRESS" | "REOPENED";

/**
 * SCR-Q-01 — Officer Assigned Queue (Batch B2).
 * Population: ASSIGNED + IN_PROGRESS + REOPENED. Sorted by SLA remaining.
 * R2-B1: rejected → SCR-WS-06 · R2-B2: reopened → SCR-WS-07.
 * R2-B3: escalation context request → SCR-WS-08.
 */
export function OfficerQueue() {
  const t = useTranslations("officerHandle");
  const tShell = useTranslations("shell");
  const router = useRouter();
  const { officerAssigned } = useAssignmentRepository();
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("ALL");
  const continuityEnabled = isBatchAtLeast("R2B1");
  const reopenEnabled = isBatchAtLeast("R2B2");
  const escalationEnabled = isBatchAtLeast("R2B3");

  const filtered = useMemo(() => {
    if (statusFilter === "ALL") return officerAssigned;
    return officerAssigned.filter(
      (c) => c.status === (statusFilter as MockComplaintStatus),
    );
  }, [officerAssigned, statusFilter]);

  const filterOptions: SelectOption[] = [
    { value: "ALL", label: t("filterAll") },
    { value: "ASSIGNED", label: t("status.ASSIGNED") },
    { value: "IN_PROGRESS", label: t("status.IN_PROGRESS") },
    ...(reopenEnabled
      ? [{ value: "REOPENED", label: t("status.REOPENED") }]
      : []),
  ];

  function openHandling(id: string): void {
    const complaint = officerAssigned.find((c) => c.id === id);
    if (
      reopenEnabled &&
      complaint &&
      hasReopenContinuity(complaint)
    ) {
      router.push(`/queue/reopened/${id}`);
      return;
    }
    if (
      continuityEnabled &&
      complaint &&
      hasRejectContinuity(complaint)
    ) {
      router.push(`/queue/resubmit/${id}`);
      return;
    }
    if (
      escalationEnabled &&
      complaint &&
      hasEscalationContextRequest(complaint)
    ) {
      router.push(`/queue/escalation-context/${id}`);
      return;
    }
    router.push(`/queue/handle/${id}`);
  }

  return (
    <WorkspaceLayout
      toolbar={
        <PageHeader
          overline={tShell(getShellBatchOverlineKey())}
          title={t("queueTitle")}
          description={t("queueDescription")}
          breadcrumbs={[
            { label: tShell("homeCrumb"), href: "/queue" },
            { label: t("queueTitle") },
          ]}
          actions={
            <Select
              id="b2-status-filter"
              name="statusFilter"
              label={t("filterStatus")}
              options={filterOptions}
              value={statusFilter}
              onChange={(event) =>
                setStatusFilter(event.target.value as StatusFilter)
              }
              className="min-w-[12rem]"
            />
          }
        />
      }
    >
      <section aria-labelledby="b2-assigned-heading" className="space-y-3">
        <div className="flex items-baseline justify-between gap-3">
          <h2
            id="b2-assigned-heading"
            className="text-[length:var(--ecmp-font-section-size)] font-semibold text-ecmp-text-primary"
          >
            {t("assignedList")}
          </h2>
          <span className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
            {t("assignedCount", { count: filtered.length })}
          </span>
        </div>

        {filtered.length === 0 ? (
          <Empty
            title={t("emptyTitle")}
            description={t("emptyDescription")}
          />
        ) : (
          <ul className="space-y-3">
            {filtered.map((complaint) => (
              <li key={complaint.id}>
                <OfficerQueueCard
                  complaint={complaint}
                  onOpen={openHandling}
                />
              </li>
            ))}
          </ul>
        )}
      </section>
    </WorkspaceLayout>
  );
}
