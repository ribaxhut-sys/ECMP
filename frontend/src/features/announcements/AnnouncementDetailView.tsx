"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { fetchAnnouncement, markAnnouncementRead } from "@/lib/api";
import type { Announcement } from "@/lib/api/types";
import { formatDateTime } from "@/i18n/formatting";
import { useLocaleContext } from "@/shared/i18n";
import {
  Card,
  CardBody,
  ErrorState,
  PageContainer,
  PageHeader,
  SectionHeader,
  Skeleton,
} from "@/shared/ui";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { mayManageAnnouncements } from "./announcementManageGate";
import { AnnouncementAttachmentList } from "./AnnouncementAttachmentList";
import {
  AnnouncementPriorityBadge,
  AnnouncementStatusBadge,
} from "./AnnouncementBadges";
import { AnnouncementManageActions } from "./AnnouncementManageActions";
import { useOrgUnitCode } from "./useOrgUnitCode";

/**
 * Detail view — reached from history (``/announcements``) or management
 * (``/announcements/manage`` via ``?from=manage``). Breadcrumb/back target
 * follows the source so readers are never sent to Pengelolaan.
 * Manage actions (edit/publish/unpublish/delete) only render for manage gate.
 */
export function AnnouncementDetailView({ id }: { id: string }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const t = useTranslations("announcements");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const { hasPermission, roles } = useAuth();
  const orgUnitCode = useOrgUnitCode();
  const { locale } = useLocaleContext();

  const canManage =
    orgUnitCode !== undefined &&
    mayManageAnnouncements({
      roles,
      hasPermission,
      orgUnitCode,
    });
  const fromManage =
    searchParams.get("from") === "manage" && canManage;
  const listHref = fromManage ? "/announcements/manage" : "/announcements";
  const listLabel = fromManage ? t("managementTitle") : t("historyTitle");

  const [announcement, setAnnouncement] = useState<Announcement | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchAnnouncement(id);
      setAnnouncement(res.data);
      // Opening the detail is what counts as "read" (§4, LOCKED) — never
      // the list. Best-effort: idempotent server-side, and a failure here
      // (e.g. this caller opened a Draft) has no user-visible consequence.
      markAnnouncementRead(id).catch(() => {});
    } catch (err) {
      setAnnouncement(null);
      setError(resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToLoad"));
    } finally {
      setLoading(false);
    }
  }, [id, t, tCommon, tErrors]);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <Skeleton rows={8} />
      </PageContainer>
    );
  }

  if (error || !announcement) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <ErrorState
          title={t("unableToLoad")}
          message={error ?? t("unableToLoad")}
          onRetry={() => void load()}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={announcement.title}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: listLabel, href: listHref },
          { label: announcement.referenceNumber },
        ]}
        meta={
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-medium tabular-nums text-ecmp-text-secondary">
              {announcement.referenceNumber}
            </span>
            <AnnouncementStatusBadge status={announcement.effectiveStatus} />
            <AnnouncementPriorityBadge priority={announcement.priority} />
            {announcement.publishedAt ? (
              <time
                dateTime={announcement.publishedAt}
                className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-muted"
              >
                {formatDateTime(announcement.publishedAt, locale)}
              </time>
            ) : null}
          </div>
        }
        actions={
          <button
            type="button"
            className="text-[length:var(--ecmp-font-body-small-size)] font-medium text-ecmp-primary underline-offset-2 hover:underline"
            onClick={() => router.push(listHref)}
          >
            {t("backToList")}
          </button>
        }
      />

      {fromManage ? (
        <AnnouncementManageActions
          announcement={announcement}
          onChanged={() => void load()}
        />
      ) : null}

      <Card>
        <CardBody className="space-y-[var(--ecmp-panel-gap)]">
          <SectionHeader title={t("fieldBodyLabel")} />
          <div className="whitespace-pre-wrap text-[length:var(--ecmp-font-body-size)] leading-relaxed text-ecmp-text-primary">
            {announcement.body}
          </div>
        </CardBody>
      </Card>

      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader title={t("attachmentsSectionTitle")} />
        <AnnouncementAttachmentList announcement={announcement} />
      </section>
    </PageContainer>
  );
}
