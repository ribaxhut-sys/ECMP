import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/shared/utils";
import { Badge, type BadgeTone } from "@/shared/ui/badge";

export interface TimelineItem {
  id: string;
  time?: ReactNode;
  title: ReactNode;
  description?: ReactNode;
  status?: string;
  statusTone?: BadgeTone;
  actor?: ReactNode;
  icon?: ReactNode;
}

export interface TimelineProps extends HTMLAttributes<HTMLOListElement> {
  items: readonly TimelineItem[];
}

/**
 * Presentational activity timeline. No event fetching or domain logic.
 */
export function Timeline({ items, className, ...props }: TimelineProps) {
  if (items.length === 0) return null;

  return (
    <ol className={cn("relative space-y-0", className)} {...props}>
      {items.map((item, index) => {
        const isLast = index === items.length - 1;
        return (
          <li key={item.id} className="relative flex gap-3 pb-6 last:pb-0">
            {!isLast ? (
              <span
                aria-hidden
                className="absolute left-[15px] top-8 bottom-0 w-px bg-ecmp-border"
              />
            ) : null}
            <div className="relative z-[1] flex size-8 shrink-0 items-center justify-center rounded-full border border-ecmp-border bg-ecmp-surface text-ecmp-text-secondary shadow-ecmp-raised">
              {item.icon ?? (
                <span className="size-2 rounded-full bg-ecmp-primary" aria-hidden />
              )}
            </div>
            <div className="min-w-0 flex-1 pt-0.5">
              <div className="flex flex-wrap items-center gap-2">
                <p className="text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary">
                  {item.title}
                </p>
                {item.status ? (
                  <Badge tone={item.statusTone ?? "neutral"}>{item.status}</Badge>
                ) : null}
              </div>
              {(item.time || item.actor) && (
                <p className="mt-0.5 text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                  {[item.time, item.actor].filter(Boolean).map((part, i) => (
                    <span key={i}>
                      {i > 0 ? " · " : null}
                      {part}
                    </span>
                  ))}
                </p>
              )}
              {item.description ? (
                <div className="mt-2 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-primary/90">
                  {item.description}
                </div>
              ) : null}
            </div>
          </li>
        );
      })}
    </ol>
  );
}
