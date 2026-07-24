"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/auth/AuthProvider";
import { ApiError, fetchAttachment, type Attachment } from "@/lib/api";
import { Alert, Empty, Skeleton } from "@/shared/ui";
import { AttachmentCard } from "./AttachmentCard";

export interface AttachmentListProps {
  /** Preloaded metadata (preferred when already available). */
  attachments?: Attachment[];
  /**
   * Attachment UUIDs to load via API-324.
   * There is no list-by-object endpoint; parents must supply IDs.
   */
  attachmentIds?: string[];
  emptyTitle?: string;
  emptyDescription?: string;
}

function mapError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 404) return "One or more attachments were not found (404).";
    if (error.status === 403) return "You do not have permission to view attachments (403).";
    if (error.status === 500) return "Server error while loading attachments (500).";
    return error.message;
  }
  return "Failed to load attachments.";
}

export function AttachmentList({
  attachments: preloaded,
  attachmentIds,
  emptyTitle = "No attachments",
  emptyDescription = "Provide attachment IDs to load files for preview and download.",
}: AttachmentListProps) {
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
      setError(mapError(err));
    } finally {
      setLoading(false);
    }
  }, [canRead]);

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
      <Alert
        tone="warning"
        title="Permission required"
        description="attachment:read is required to view attachments."
      />
    );
  }

  if (loading) {
    return (
      <div className="space-y-3" data-testid="attachment-list-loading">
        <Skeleton className="h-36 w-full" />
        <Skeleton className="h-36 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        tone="danger"
        title="Could not load attachments"
        description={error}
        actionLabel="Retry"
        onAction={
          attachmentIds?.length
            ? () => void loadByIds(attachmentIds)
            : undefined
        }
      />
    );
  }

  if (items.length === 0) {
    return <Empty title={emptyTitle} description={emptyDescription} />;
  }

  return (
    <div
      className="grid grid-cols-1 gap-4 lg:grid-cols-2"
      data-testid="attachment-list"
    >
      {items.map((item) => (
        <AttachmentCard key={item.id} attachment={item} />
      ))}
    </div>
  );
}
