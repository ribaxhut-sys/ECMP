"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { ApiError, fetchAttachment, type Attachment } from "@/lib/api";
import { Empty, ErrorState, Skeleton, type EmptyActionConfig } from "@/shared/ui";
import { AttachmentCard } from "./AttachmentCard";

export interface AttachmentListProps {
  /** Preloaded metadata (preferred when already available). */
  attachments?: Attachment[];
  /**
   * Attachment IDs to load when the parent already knows them.
   */
  attachmentIds?: string[];
  emptyTitle?: string;
  emptyDescription?: string;
  emptyPrimaryAction?: EmptyActionConfig;
}

function mapError(error: unknown, t: (key: string) => string): string {
  if (error instanceof ApiError) {
    if (error.status === 404) return t("someNotFound404");
    if (error.status === 403) return t("noReadPermission403");
    if (error.status === 500) return t("serverErrorLoading500");
    return error.message;
  }
  return t("failedToLoad");
}

export function AttachmentList({
  attachments: preloaded,
  attachmentIds,
  emptyTitle = undefined,
  emptyDescription = undefined,
  emptyPrimaryAction,
}: AttachmentListProps) {
  const router = useRouter();
  const t = useTranslations("attachments");
  const tCommon = useTranslations("common");
  const { hasPermission } = useAuth();
  const canRead = hasPermission("attachment:read") || hasPermission("*");

  const [items, setItems] = useState<Attachment[]>(preloaded ?? []);
  const [loading, setLoading] = useState(Boolean(attachmentIds?.length) && !preloaded);
  const [error, setError] = useState<string | null>(null);

  const loadByIds = useCallback(async (ids: string[]) => {
    if (!canRead) {
      setItems([]);
      setLoading(false);
      setError(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const unique = [...new Set(ids.map((id) => id.trim()).filter(Boolean))];
      const results = await Promise.all(
        unique.map(async (id) => {
          const res = await fetchAttachment(id);
          return res.data;
        }),
      );
      setItems(results);
    } catch (err) {
      setItems([]);
      setError(mapError(err, t));
    } finally {
      setLoading(false);
    }
  }, [canRead, t]);

  const idsKey = (attachmentIds ?? []).join(",");

  useEffect(() => {
    if (preloaded) {
      setItems(preloaded);
      setLoading(false);
      setError(null);
      return;
    }
    if (idsKey) {
      void loadByIds(idsKey.split(",").filter(Boolean));
      return;
    }
    setItems([]);
    setLoading(false);
    setError(null);
  }, [preloaded, idsKey, loadByIds]);

  if (!canRead) {
    return (
      <Empty
        title={t("permissionRequired")}
        description={t("readPermissionRequiredDescription")}
        primaryAction={{
          label: tCommon("goHome"),
          onClick: () => router.push("/dashboard"),
        }}
      />
    );
  }

  if (loading) {
    return (
      <div data-testid="attachment-list-loading">
        <Skeleton rows={6} />
      </div>
    );
  }

  if (error) {
    return (
      <ErrorState
        title={t("couldNotLoad")}
        message={error}
        onRetry={
          attachmentIds?.length
            ? () => void loadByIds(attachmentIds)
            : undefined
        }
      />
    );
  }

  if (items.length === 0) {
    return (
      <Empty
        title={emptyTitle ?? t("noItems")}
        description={emptyDescription ?? t("noItemsDescription")}
        primaryAction={
          emptyPrimaryAction ??
          (attachmentIds?.length
            ? {
                label: t("refreshAttachments"),
                onClick: () => void loadByIds(attachmentIds),
              }
            : {
                label: tCommon("goToComplaints"),
                onClick: () => router.push("/complaints"),
              })
        }
      />
    );
  }

  return (
    <div
      className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] lg:grid-cols-2"
      data-testid="attachment-list"
    >
      {items.map((item) => (
        <AttachmentCard key={item.id} attachment={item} />
      ))}
    </div>
  );
}
