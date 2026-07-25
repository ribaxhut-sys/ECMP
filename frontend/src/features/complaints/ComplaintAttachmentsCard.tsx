"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  fetchComplaintAttachments,
  uploadAttachment,
  type Attachment,
} from "@/lib/api";
import { AttachmentList } from "@/features/attachments";
import {
  Alert,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Input,
  Skeleton,
} from "@/shared/ui";

export function ComplaintAttachmentsCard({
  complaintId,
  refreshKey = 0,
  allowUpload = false,
}: {
  complaintId: string;
  refreshKey?: number;
  allowUpload?: boolean;
}) {
  const { hasPermission } = useAuth();
  const canRead = hasPermission("attachment:read") || hasPermission("*");
  const canCreate =
    allowUpload &&
    (hasPermission("attachment:create") || hasPermission("*"));

  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  const load = useCallback(async () => {
    if (!canRead) {
      setAttachments([]);
      setLoading(false);
      setError(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetchComplaintAttachments(complaintId);
      setAttachments(res.data);
    } catch (err) {
      setAttachments([]);
      setError(
        err instanceof ApiError
          ? err.message
          : "Unable to load attachments.",
      );
    } finally {
      setLoading(false);
    }
  }, [canRead, complaintId]);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  async function onUpload(
    event: React.ChangeEvent<HTMLInputElement>,
  ): Promise<void> {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file || !canCreate) return;

    setUploading(true);
    setUploadError(null);
    try {
      await uploadAttachment("Complaint", complaintId, file);
      await load();
    } catch (err) {
      setUploadError(
        err instanceof ApiError
          ? err.message
          : "Unable to upload attachment.",
      );
    } finally {
      setUploading(false);
    }
  }

  return (
    <Card>
      <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <CardTitle>Attachments</CardTitle>
        {canCreate ? (
          <div className="flex flex-col gap-1 sm:items-end">
            <Input
              type="file"
              name="attachment"
              label="Upload file"
              aria-label="Upload attachment"
              disabled={uploading}
              onChange={(e) => void onUpload(e)}
              className="max-w-xs"
            />
            {uploading ? (
              <span className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                Uploading…
              </span>
            ) : null}
          </div>
        ) : null}
      </CardHeader>
      <CardBody className="space-y-4">
        {!canRead ? (
          <Alert
            tone="warning"
            title="Attachments unavailable"
            description="Your account does not have attachment:read permission."
          />
        ) : null}

        {uploadError ? (
          <Alert
            tone="danger"
            title="Upload failed"
            description={uploadError}
          />
        ) : null}

        {error ? (
          <Alert
            tone="danger"
            title="Could not load attachments"
            description={error}
            actionLabel="Retry"
            onAction={() => void load()}
          />
        ) : null}

        {canRead && !error && loading ? <Skeleton rows={3} /> : null}

        {canRead && !error && !loading ? (
          <AttachmentList
            attachments={attachments}
            emptyTitle="No attachments"
            emptyDescription="No files are linked to this complaint yet."
          />
        ) : null}
      </CardBody>
    </Card>
  );
}
