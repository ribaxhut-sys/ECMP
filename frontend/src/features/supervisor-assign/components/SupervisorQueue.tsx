"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import {
  Empty,
  PageHeader,
  Skeleton,
} from "@/shared/ui";
import { WorkspaceLayout } from "@/shared/layouts/shell";
import {
  getShellBatchOverlineKey,
  isBatchAtLeast,
} from "@/shared/config/uiBatch";
import { useAssignmentRepository } from "../mock/useAssignmentRepository";
import { AssignmentCard } from "./AssignmentCard";
import { PendingReviewCard } from "@/features/approval-review";
import { PendingReopenCard } from "@/features/reopen-approval";
import {
  EscalationCountBanner,
  EscalationQueueCard,
  SlaRiskQueueCard,
} from "./PriorityQueueCards";

/**
 * SCR-Q-02 — Supervisor Queue.
 * B1+: Unassigned.
 * B5+: Pending approval (preserved).
 * B6+: Escalation (stub until R2-B3) → SLA at-risk → … → Unassigned (fixed priority).
 * R2B2+: Pending reopen approval.
 * R2B3+: Escalation opens SCR-WS-11.
 */
export function SupervisorQueue() {
  const t = useTranslations("supervisorAssign");
  const tPriority = useTranslations("supervisorQueuePriority");
  const tReview = useTranslations("approvalReview");
  const tReopen = useTranslations("reopenApproval");
  const tShell = useTranslations("shell");
  const router = useRouter();
  const { unassigned, pendingReview, pendingReopen, newEscalations, slaAtRisk } =
    useAssignmentRepository();
  const showPending = isBatchAtLeast("B5");
  const showPriority = isBatchAtLeast("B6");
  const showReopenPending = isBatchAtLeast("R2B2");
  const showEscalationAction = isBatchAtLeast("R2B3");

  function openAssignment(id: string): void {
    router.push(`/queue/assign/${id}`);
  }

  function openReview(id: string): void {
    router.push(`/queue/review/${id}`);
  }

  function openReopenReview(id: string): void {
    router.push(`/queue/reopen-review/${id}`);
  }

  function openEscalation(id: string): void {
    router.push(`/queue/escalation/${id}`);
  }

  const description = showPriority
    ? tPriority("queueDescription")
    : showPending
      ? t("queueDescriptionB5")
      : t("queueDescription");

  return (
    <WorkspaceLayout
      toolbar={
        <PageHeader
          overline={tShell(getShellBatchOverlineKey())}
          title={t("queueTitle")}
          description={description}
          breadcrumbs={[
            { label: tShell("homeCrumb"), href: "/queue" },
            { label: t("queueTitle") },
          ]}
        />
      }
    >
      <div className="space-y-8">
        {showPriority ? (
          <EscalationCountBanner count={newEscalations.length} />
        ) : null}

        {showPriority ? (
          <section
            aria-labelledby="b6-escalation-heading"
            className="space-y-3"
          >
            <div className="flex items-baseline justify-between gap-3">
              <h2
                id="b6-escalation-heading"
                className="text-[length:var(--ecmp-font-section-size)] font-semibold text-ecmp-text-primary"
              >
                {tPriority("escalationSegment")}
              </h2>
              <span className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                {tPriority("segmentCount", { count: newEscalations.length })}
              </span>
            </div>
            {newEscalations.length === 0 ? (
              <Empty
                title={tPriority("emptyEscalationTitle")}
                description={tPriority("emptyEscalationDescription")}
              />
            ) : (
              <ul className="space-y-3">
                {newEscalations.map((complaint) => (
                  <li key={complaint.id}>
                    <EscalationQueueCard
                      complaint={complaint}
                      onOpen={
                        showEscalationAction ? openEscalation : undefined
                      }
                    />
                  </li>
                ))}
              </ul>
            )}
          </section>
        ) : null}

        {showPriority ? (
          <section aria-labelledby="b6-sla-heading" className="space-y-3">
            <div className="flex items-baseline justify-between gap-3">
              <h2
                id="b6-sla-heading"
                className="text-[length:var(--ecmp-font-section-size)] font-semibold text-ecmp-text-primary"
              >
                {tPriority("slaSegment")}
              </h2>
              <span className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                {tPriority("segmentCount", { count: slaAtRisk.length })}
              </span>
            </div>
            {slaAtRisk.length === 0 ? (
              <Empty
                title={tPriority("emptySlaTitle")}
                description={tPriority("emptySlaDescription")}
              />
            ) : (
              <ul className="space-y-3">
                {slaAtRisk.map((complaint) => (
                  <li key={complaint.id}>
                    <SlaRiskQueueCard complaint={complaint} />
                  </li>
                ))}
              </ul>
            )}
          </section>
        ) : null}

        {showReopenPending ? (
          <section aria-labelledby="r2b2-reopen-heading" className="space-y-3">
            <div className="flex items-baseline justify-between gap-3">
              <h2
                id="r2b2-reopen-heading"
                className="text-[length:var(--ecmp-font-section-size)] font-semibold text-ecmp-text-primary"
              >
                {tReopen("pendingSegment")}
              </h2>
              <span className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                {tReopen("pendingCount", { count: pendingReopen.length })}
              </span>
            </div>
            {pendingReopen.length === 0 ? (
              <Empty
                title={tReopen("emptyPendingTitle")}
                description={tReopen("emptyPendingDescription")}
              />
            ) : (
              <ul className="space-y-3">
                {pendingReopen.map((complaint) => (
                  <li key={complaint.id}>
                    <PendingReopenCard
                      complaint={complaint}
                      onOpen={openReopenReview}
                    />
                  </li>
                ))}
              </ul>
            )}
          </section>
        ) : null}

        {showPending ? (
          <section aria-labelledby="b5-pending-heading" className="space-y-3">
            <div className="flex items-baseline justify-between gap-3">
              <h2
                id="b5-pending-heading"
                className="text-[length:var(--ecmp-font-section-size)] font-semibold text-ecmp-text-primary"
              >
                {tReview("pendingSegment")}
              </h2>
              <span className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                {tReview("pendingCount", { count: pendingReview.length })}
              </span>
            </div>

            {pendingReview.length === 0 ? (
              <Empty
                title={tReview("emptyPendingTitle")}
                description={tReview("emptyPendingDescription")}
              />
            ) : (
              <ul className="space-y-3">
                {pendingReview.map((complaint) => (
                  <li key={complaint.id}>
                    <PendingReviewCard
                      complaint={complaint}
                      onOpen={openReview}
                    />
                  </li>
                ))}
              </ul>
            )}
          </section>
        ) : null}

        <section aria-labelledby="b1-unassigned-heading" className="space-y-3">
          <div className="flex items-baseline justify-between gap-3">
            <h2
              id="b1-unassigned-heading"
              className="text-[length:var(--ecmp-font-section-size)] font-semibold text-ecmp-text-primary"
            >
              {t("unassignedSegment")}
            </h2>
            <span className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
              {t("unassignedCount", { count: unassigned.length })}
            </span>
          </div>

          {unassigned.length === 0 ? (
            <Empty
              title={t("emptyUnassignedTitle")}
              description={t("emptyUnassignedDescription")}
            />
          ) : (
            <ul className="space-y-3">
              {unassigned.map((complaint) => (
                <li key={complaint.id}>
                  <AssignmentCard
                    complaint={complaint}
                    onOpen={openAssignment}
                  />
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </WorkspaceLayout>
  );
}

/** SSR-safe skeleton while client store hydrates (optional). */
export function SupervisorQueueSkeleton() {
  return (
    <WorkspaceLayout>
      <Skeleton rows={4} />
    </WorkspaceLayout>
  );
}
