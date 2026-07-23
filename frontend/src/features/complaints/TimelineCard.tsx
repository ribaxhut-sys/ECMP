"use client";

import { useCallback, useEffect, useState } from "react";
import { ApiError, fetchComplaintTimeline } from "@/lib/api";
import type { TimelineEntry } from "@/lib/api/types";
import {
  Alert,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Empty,
  Skeleton,
} from "@/shared/ui";
import { cn } from "@/shared/utils";

/** UI activity kinds (mapped from API TimelineEvent + metadata). */
export type TimelineActivityType =
  | "CREATED"
  | "ASSIGNED"
  | "STATUS_CHANGED"
  | "PRIORITY_CHANGED"
  | "OTHER";

function formatWhen(value: string | null | undefined): string {
  if (!value) return "—";
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function activityType(entry: TimelineEntry): TimelineActivityType {
  const changeType =
    typeof entry.metadata?.changeType === "string"
      ? entry.metadata.changeType
      : null;

  if (changeType === "PRIORITY_CHANGED") return "PRIORITY_CHANGED";
  if (changeType === "STATUS_CHANGED" && entry.eventType === "complaint.updated") {
    return "STATUS_CHANGED";
  }

  switch (entry.eventType) {
    case "complaint.created":
      return "CREATED";
    case "complaint.assigned":
    case "complaint.reassigned":
      return "ASSIGNED";
    case "complaint.updated":
      if (entry.fromStatus && entry.toStatus && entry.fromStatus !== entry.toStatus) {
        return "STATUS_CHANGED";
      }
      return "OTHER";
    case "complaint.resolved":
    case "complaint.closed":
    case "complaint.escalated":
      return "STATUS_CHANGED";
    default:
      return "OTHER";
  }
}

function activityIcon(type: TimelineActivityType): string {
  switch (type) {
    case "CREATED":
      return "+";
    case "ASSIGNED":
      return "👤";
    case "STATUS_CHANGED":
      return "⇄";
    case "PRIORITY_CHANGED":
      return "!";
    default:
      return "•";
  }
}

function activityMessage(entry: TimelineEntry): string {
  const summary = entry.summary?.trim();
  if (summary) return summary;
  switch (activityType(entry)) {
    case "CREATED":
      return "Complaint created";
    case "ASSIGNED":
      return "Complaint assigned";
    case "PRIORITY_CHANGED":
      return "Priority changed";
    case "STATUS_CHANGED":
      return "Status changed";
    default:
      return "Activity";
  }
}

export function TimelineCard({
  complaintId,
  refreshKey = 0,
}: {
  complaintId: string;
  refreshKey?: number;
}) {
  const [entries, setEntries] = useState<TimelineEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchComplaintTimeline(complaintId);
      // API returns newest-first; keep that order for the UI.
      setEntries(res.data);
    } catch (err) {
      setEntries([]);
      setError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Unable to load timeline.",
      );
    } finally {
      setLoading(false);
    }
  }, [complaintId]);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Timeline</CardTitle>
      </CardHeader>
      <CardBody>
        {loading ? (
          <Skeleton rows={4} />
        ) : error ? (
          <Alert
            tone="danger"
            title="Could not load timeline"
            description={error}
            actionLabel="Retry"
            onAction={() => void load()}
          />
        ) : entries.length === 0 ? (
          <Empty title="Timeline" description="No activity yet." />
        ) : (
          <ol className="space-y-0" aria-label="Complaint activity timeline">
            {entries.map((entry, index) => {
              const type = activityType(entry);
              const isLast = index === entries.length - 1;
              return (
                <li key={entry.id} className="relative flex gap-3 pb-5 last:pb-0">
                  {!isLast ? (
                    <span
                      aria-hidden="true"
                      className="absolute left-[15px] top-8 bottom-0 w-px bg-ecmp-border"
                    />
                  ) : null}
                  <span
                    aria-hidden="true"
                    className={cn(
                      "relative z-[1] flex size-8 shrink-0 items-center justify-center rounded-full border border-ecmp-border bg-ecmp-surface text-sm font-semibold text-ecmp-text-primary",
                    )}
                    title={type}
                  >
                    {activityIcon(type)}
                  </span>
                  <div className="min-w-0 flex-1 space-y-1 border-b border-ecmp-border pb-5 last:border-b-0 last:pb-0">
                    <p className="text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary">
                      {activityMessage(entry)}
                    </p>
                    <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                      {entry.actorName?.trim() || "System"}
                    </p>
                    <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                      <time dateTime={entry.eventAt || entry.createdAt}>
                        {formatWhen(entry.eventAt || entry.createdAt)}
                      </time>
                    </p>
                  </div>
                </li>
              );
            })}
          </ol>
        )}
      </CardBody>
    </Card>
  );
}
