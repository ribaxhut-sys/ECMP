"use client";

import { useState } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import type { CmBatch1ComplaintBrief } from "@/lib/api";
import { Alert, Badge, Button, Empty, Modal } from "@/shared/ui";
import { formatDateTime24 } from "@/shared/utils/datetime";

const PREVIEW_LIMIT = 3;

function briefId(row: CmBatch1ComplaintBrief, index: number): string {
  return row.complaintId?.trim() || `complaint-${index}`;
}

function rowLabel(row: CmBatch1ComplaintBrief, index: number): string {
  return row.complaintNumber?.trim() || briefId(row, index);
}

export interface ActiveComplaintsBannerProps {
  complaints: CmBatch1ComplaintBrief[];
  disabled?: boolean;
  linking?: boolean;
  /**
   * User-driven link to an existing active complaint (FR-003 link_existing).
   * Independent of duplicate score — officer decides the issue is the same.
   */
  onLinkExisting?: (payload: {
    survivingComplaintId: string;
    label: string;
  }) => void | Promise<void>;
}

/**
 * Inline warning when a locked taxpayer has open complaints (BR-010 / Taxpayer 360).
 * Shown above intake form fields so officers notice before submit.
 * Optional link action — tautkan tanpa menunggu skor duplikat ≥ 70.
 */
export function ActiveComplaintsBanner({
  complaints,
  disabled = false,
  linking = false,
  onLinkExisting,
}: ActiveComplaintsBannerProps) {
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const [showAll, setShowAll] = useState(false);
  const [pendingLink, setPendingLink] = useState<{
    survivingComplaintId: string;
    label: string;
  } | null>(null);

  if (complaints.length === 0) return null;

  const preview = complaints.slice(0, PREVIEW_LIMIT);
  const remaining = complaints.length - preview.length;
  const busy = disabled || linking;
  const canLink = typeof onLinkExisting === "function";

  function requestLink(row: CmBatch1ComplaintBrief, index: number): void {
    const survivingComplaintId = row.complaintId?.trim();
    if (!survivingComplaintId || !canLink || busy) return;
    setPendingLink({
      survivingComplaintId,
      label: rowLabel(row, index),
    });
  }

  async function confirmLink(): Promise<void> {
    if (!pendingLink || !onLinkExisting) return;
    const payload = pendingLink;
    setPendingLink(null);
    setShowAll(false);
    await onLinkExisting(payload);
  }

  function actionButtons(row: CmBatch1ComplaintBrief, index: number) {
    const id = briefId(row, index);
    const href = `/complaints/cm/${encodeURIComponent(id)}`;
    if (!row.complaintId) return null;
    return (
      <div className="flex shrink-0 flex-wrap items-center gap-2">
        <Link
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center rounded-[var(--ecmp-radius-button)] border border-ecmp-border bg-ecmp-surface px-3 py-1.5 text-[length:var(--ecmp-font-helper-size)] font-medium text-ecmp-primary underline-offset-2 hover:bg-ecmp-hover hover:underline"
        >
          {t("reviewCandidate")}
        </Link>
        {canLink ? (
          <Button
            type="button"
            variant="primary"
            size="sm"
            disabled={busy}
            loading={linking}
            onClick={() => requestLink(row, index)}
          >
            {t("activeComplaintsUseExisting")}
          </Button>
        ) : null}
      </div>
    );
  }

  return (
    <>
      <Alert
        tone="warning"
        title={t("activeComplaintsBannerTitle", { count: complaints.length })}
        description={
          <div className="space-y-3">
            <p>{t("activeComplaintsBannerDescription")}</p>
            {canLink ? (
              <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                {t("activeComplaintsLinkHint")}
              </p>
            ) : null}
            <ul className="space-y-2">
              {preview.map((row, index) => {
                const id = briefId(row, index);
                const number = rowLabel(row, index);
                const created = formatDateTime24(row.createdAt);
                return (
                  <li
                    key={id}
                    className="rounded-[var(--ecmp-radius-md)] border border-ecmp-warning-border/60 bg-ecmp-surface/80 p-3"
                  >
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                      <div className="min-w-0 space-y-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="font-mono text-[length:var(--ecmp-font-body-small-size)] font-medium text-ecmp-text-primary">
                            {number}
                          </span>
                          <Badge tone="info">{t("statusOpen")}</Badge>
                        </div>
                        {row.subject?.trim() ? (
                          <p className="text-ecmp-text-primary">{row.subject}</p>
                        ) : null}
                        {created ? (
                          <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                            {t("candidateCreatedAt", { date: created })}
                          </p>
                        ) : null}
                      </div>
                      {actionButtons(row, index)}
                    </div>
                  </li>
                );
              })}
            </ul>
            {remaining > 0 ? (
              <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                {t("activeComplaintsBannerMore", { count: remaining })}
              </p>
            ) : null}
          </div>
        }
        actions={
          complaints.length > PREVIEW_LIMIT ? (
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={busy}
              onClick={() => setShowAll(true)}
            >
              {t("activeComplaintsBannerViewAll")}
            </Button>
          ) : null
        }
      />

      {showAll ? (
        <Modal
          open
          onClose={() => (linking ? undefined : setShowAll(false))}
          title={t("customerHistoryActiveTitle")}
          size="lg"
          footer={
            <Button
              type="button"
              variant="outline"
              disabled={linking}
              onClick={() => setShowAll(false)}
            >
              {tCommon("closeDialog")}
            </Button>
          }
        >
          {complaints.length === 0 ? (
            <Empty
              title={t("customerHistoryEmpty")}
              description={t("customerHistoryHint")}
            />
          ) : (
            <ul className="max-h-80 space-y-2 overflow-auto">
              {complaints.map((row, index) => {
                const id = briefId(row, index);
                const number = rowLabel(row, index);
                const created = formatDateTime24(row.createdAt);
                return (
                  <li
                    key={id}
                    className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border p-3"
                  >
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                      <div className="min-w-0 space-y-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="font-mono text-[length:var(--ecmp-font-body-small-size)] font-medium">
                            {number}
                          </span>
                          <Badge tone="info">{t("statusOpen")}</Badge>
                        </div>
                        {row.subject?.trim() ? (
                          <p className="text-ecmp-text-primary">{row.subject}</p>
                        ) : null}
                        {created ? (
                          <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                            {t("candidateCreatedAt", { date: created })}
                          </p>
                        ) : null}
                      </div>
                      {actionButtons(row, index)}
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </Modal>
      ) : null}

      {pendingLink ? (
        <Modal
          open
          onClose={() => (linking ? undefined : setPendingLink(null))}
          title={t("activeComplaintsLinkConfirmTitle")}
          size="md"
          footer={
            <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
              <Button
                type="button"
                variant="outline"
                disabled={linking}
                onClick={() => setPendingLink(null)}
              >
                {tCommon("cancel")}
              </Button>
              <Button
                type="button"
                variant="primary"
                loading={linking}
                disabled={linking}
                onClick={() => void confirmLink()}
              >
                {t("activeComplaintsLinkConfirmAction")}
              </Button>
            </div>
          }
        >
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
            {t("activeComplaintsLinkConfirmBody", {
              label: pendingLink.label,
            })}
          </p>
        </Modal>
      ) : null}
    </>
  );
}
