"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { fetchActiveAnnouncements } from "@/lib/api";
import type { Announcement } from "@/lib/api/types";
import { isInternalComplaintsUiEnabled } from "@/shared/config/internalComplaintsUi";
import { IconChevronRight, IconComplaints } from "@/shared/icons";
import {
  APP_NAV_ITEMS,
  isNavItemVisible,
} from "@/shared/layouts/app-layout/nav";
import {
  Card,
  CardBody,
  Empty,
  ErrorState,
  PageContainer,
  PageHeader,
  SectionHeader,
  Skeleton,
} from "@/shared/ui";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { cn } from "@/shared/utils";
import { AnnouncementCard } from "./AnnouncementCard";
import { selectLandingAnnouncements } from "./announcements";

/** Sumber tunggal yang sama dengan gate sidebar & `/complaints` layout. */
const TAXPAYER_NAV_ITEM = APP_NAV_ITEMS.find((item) => item.id === "complaints")!;
const INTERNAL_NAV_ITEM = APP_NAV_ITEMS.find(
  (item) => item.id === "internalComplaints",
)!;

function QuickAccessCard({
  href,
  title,
  description,
}: {
  href: string;
  title: string;
  description: string;
}) {
  return (
    <Link
      href={href}
      className={cn(
        "group block rounded-[var(--ecmp-radius-card)]",
        "focus-visible:outline-none focus-visible:ring-[length:var(--ecmp-focus-ring-width)] focus-visible:ring-ecmp-focus",
      )}
    >
      <Card interactive className="h-full">
        <CardBody className="flex items-start gap-3">
          <span className="rounded-[var(--ecmp-radius-md)] bg-ecmp-primary-muted p-2 text-ecmp-primary">
            <IconComplaints className="size-5" aria-hidden />
          </span>
          <span className="min-w-0 flex-1">
            <span className="block text-[length:var(--ecmp-font-card-title-size)] font-[number:var(--ecmp-font-card-title-weight)] tracking-tight text-ecmp-text-primary">
              {title}
            </span>
            <span className="mt-1 block text-[length:var(--ecmp-font-body-small-size)] leading-relaxed text-ecmp-text-secondary">
              {description}
            </span>
          </span>
          <IconChevronRight
            aria-hidden
            className="mt-1 size-5 shrink-0 text-ecmp-muted transition-transform duration-[var(--ecmp-duration-fast)] group-hover:translate-x-0.5 group-hover:text-ecmp-primary motion-reduce:transition-none"
          />
        </CardBody>
      </Card>
    </Link>
  );
}

/**
 * Landing Page modul Pengaduan — halaman pertama setelah masuk.
 * Pengumuman adalah konten utama; Akses Cepat hanya entry point ke domain
 * pengaduan yang sudah ada (routing, permission, dan workflow tidak diubah).
 */
export function ComplaintsLandingView() {
  const t = useTranslations("landing");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const { hasPermission } = useAuth();

  const showTaxpayer = isNavItemVisible(TAXPAYER_NAV_ITEM, hasPermission);
  const showInternal =
    isInternalComplaintsUiEnabled() &&
    isNavItemVisible(INTERNAL_NAV_ITEM, hasPermission);

  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const res = await fetchActiveAnnouncements();
      setAnnouncements(res.data);
    } catch (err) {
      setAnnouncements([]);
      setLoadError(
        resolveApiErrorMessage(err, tErrors, tCommon) ||
          t("announcementsLoadFailed"),
      );
    } finally {
      setLoading(false);
    }
  }, [t, tCommon, tErrors]);

  useEffect(() => {
    void load();
  }, [load]);

  const { featured, rest } = useMemo(
    () => selectLandingAnnouncements(announcements),
    [announcements],
  );

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader title={t("title")} description={t("description")} />

      <section
        aria-labelledby="landing-announcements"
        className="space-y-[var(--ecmp-panel-gap)]"
      >
        <SectionHeader
          id="landing-announcements"
          title={t("announcementsTitle")}
          description={t("announcementsDescription")}
        />

        {loading ? (
          <Card>
            <CardBody>
              <Skeleton rows={3} />
            </CardBody>
          </Card>
        ) : loadError ? (
          <ErrorState
            title={t("announcementsLoadFailed")}
            message={loadError}
            onRetry={() => void load()}
          />
        ) : featured ? (
          <div className="space-y-[var(--ecmp-panel-gap)]">
            <AnnouncementCard announcement={featured} featured />
            {rest.length > 0 ? (
              <div className="grid gap-[var(--ecmp-panel-gap)] md:grid-cols-2">
                {rest.map((announcement) => (
                  <AnnouncementCard
                    key={announcement.id}
                    announcement={announcement}
                  />
                ))}
              </div>
            ) : null}
          </div>
        ) : (
          <Card>
            <CardBody>
              <Empty
                title={t("announcementsEmpty")}
                description={t("announcementsEmptyDescription")}
              />
            </CardBody>
          </Card>
        )}
      </section>

      {showTaxpayer || showInternal ? (
        <section
          aria-labelledby="landing-quick-access"
          className="space-y-[var(--ecmp-panel-gap)]"
        >
          <SectionHeader
            id="landing-quick-access"
            title={t("quickAccessTitle")}
            description={t("quickAccessDescription")}
          />
          <div className="grid gap-[var(--ecmp-panel-gap)] md:grid-cols-2">
            {showTaxpayer ? (
              <QuickAccessCard
                href={TAXPAYER_NAV_ITEM.href}
                title={t("quickAccessTaxpayer")}
                description={t("quickAccessTaxpayerDescription")}
              />
            ) : null}
            {showInternal ? (
              <QuickAccessCard
                href={INTERNAL_NAV_ITEM.href}
                title={t("quickAccessInternal")}
                description={t("quickAccessInternalDescription")}
              />
            ) : null}
          </div>
        </section>
      ) : null}
    </PageContainer>
  );
}
