"use client";

import type {
  HTMLAttributes,
  ReactNode,
  TdHTMLAttributes,
  ThHTMLAttributes,
} from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/shared/utils";
import { Empty } from "@/shared/ui/empty";
import { Skeleton } from "@/shared/ui/loading";

export type TableDensity = "comfortable" | "compact";

export interface TableColumn<T> {
  key: string;
  header: string;
  className?: string;
  headerClassName?: string;
  /** Cell renderer for desktop table. */
  cell: (row: T) => ReactNode;
  /** Optional label shown above the value in mobile stacked cards. Defaults to header. */
  mobileLabel?: string;
  /** Hide this column on mobile stacked cards. */
  hideOnMobile?: boolean;
  /** Hint for status/badge/action column alignment. */
  slot?: "status" | "badge" | "action" | "default";
}

export interface TableProps<T> extends HTMLAttributes<HTMLDivElement> {
  columns: readonly TableColumn<T>[];
  rows: readonly T[];
  getRowKey: (row: T, index: number) => string;
  caption?: string;
  emptyMessage?: string;
  emptyTitle?: string;
  emptyAction?: ReactNode;
  loading?: boolean;
  density?: TableDensity;
  /** Sticky table header (desktop). */
  stickyHeader?: boolean;
  /**
   * Presentation-only row selection highlight.
   * Pass a Set of row keys — no selection logic inside Table.
   */
  selectedKeys?: ReadonlySet<string>;
  onRowClick?: (row: T, index: number) => void;
  skeletonRows?: number;
}

export function Table<T>({
  columns,
  rows,
  getRowKey,
  caption,
  emptyMessage,
  emptyTitle,
  emptyAction,
  loading = false,
  density = "comfortable",
  stickyHeader = true,
  selectedKeys,
  onRowClick,
  skeletonRows = 5,
  className,
  ...props
}: TableProps<T>) {
  const t = useTranslations("table");
  const cellY =
    density === "compact"
      ? "py-[var(--ecmp-density-compact-cell-y)]"
      : "py-[var(--ecmp-density-comfortable-cell-y)]";

  if (loading) {
    return (
      <div className={cn("w-full", className)} {...props}>
        <Skeleton rows={skeletonRows} className="md:hidden" />
        <div className="hidden overflow-hidden rounded-[var(--ecmp-radius-table)] border border-ecmp-border md:block">
          <Skeleton rows={skeletonRows} className="p-4" />
        </div>
      </div>
    );
  }

  if (rows.length === 0) {
    return (
      <Empty
        title={emptyTitle}
        description={emptyMessage ?? t("empty")}
        action={emptyAction}
        className={className}
      />
    );
  }

  return (
    <div className={cn("w-full min-w-0", className)} {...props}>
      {/* Desktop / tablet table */}
      <div className="hidden max-w-full overflow-x-auto rounded-[var(--ecmp-radius-table)] border border-ecmp-border bg-ecmp-surface shadow-ecmp-raised md:block">
        <table className="min-w-full text-left text-[length:var(--ecmp-font-body-size)]">
          {caption ? <caption className="sr-only">{caption}</caption> : null}
          <thead
            className={cn(
              "border-b border-ecmp-border bg-ecmp-surface-sunken text-ecmp-text-secondary",
              stickyHeader && "sticky top-0 z-[var(--ecmp-z-sticky-header)]",
            )}
          >
            <tr>
              {columns.map((column) => (
                <Th
                  key={column.key}
                  className={cn(
                    cellY,
                    column.slot === "action" && "text-right",
                    column.headerClassName,
                  )}
                >
                  {column.header}
                </Th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => {
              const key = getRowKey(row, index);
              const selected = selectedKeys?.has(key);
              return (
                <tr
                  key={key}
                  data-selected={selected || undefined}
                  onClick={onRowClick ? () => onRowClick(row, index) : undefined}
                  className={cn(
                    "border-b border-ecmp-border/70 align-middle last:border-0",
                    "transition-colors duration-[var(--ecmp-duration-fast)] ease-[var(--ecmp-ease-hover)]",
                    "hover:bg-ecmp-hover",
                    selected && "bg-ecmp-selected",
                    onRowClick && "cursor-pointer",
                  )}
                >
                  {columns.map((column) => (
                    <Td
                      key={column.key}
                      className={cn(
                        cellY,
                        column.slot === "action" && "text-right",
                        column.className,
                      )}
                    >
                      {column.cell(row)}
                    </Td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Mobile stacked cards — avoids horizontal scroll */}
      <ul className="flex flex-col gap-3 md:hidden" aria-label={caption}>
        {rows.map((row, index) => {
          const key = getRowKey(row, index);
          const selected = selectedKeys?.has(key);
          return (
            <li
              key={key}
              data-selected={selected || undefined}
              onClick={onRowClick ? () => onRowClick(row, index) : undefined}
              className={cn(
                "rounded-[var(--ecmp-radius-card)] border border-ecmp-border bg-ecmp-surface p-4 shadow-ecmp-raised",
                "transition-[box-shadow,background-color] duration-[var(--ecmp-duration-fast)] ease-[var(--ecmp-ease-hover)]",
                selected && "border-ecmp-primary bg-ecmp-selected",
                onRowClick && "cursor-pointer hover:shadow-ecmp-hover",
              )}
            >
              <dl className="space-y-3">
                {columns
                  .filter((column) => !column.hideOnMobile)
                  .map((column) => (
                    <div key={column.key}>
                      <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                        {column.mobileLabel ?? column.header}
                      </dt>
                      <dd className="mt-1 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                        {column.cell(row)}
                      </dd>
                    </div>
                  ))}
              </dl>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export function Th({
  className,
  children,
  ...props
}: ThHTMLAttributes<HTMLTableCellElement>) {
  return (
    <th
      className={cn(
        "px-4 font-medium first:pl-4 last:pr-4",
        className,
      )}
      {...props}
    >
      {children}
    </th>
  );
}

export function Td({
  className,
  children,
  ...props
}: TdHTMLAttributes<HTMLTableCellElement>) {
  return (
    <td className={cn("px-4 first:pl-4 last:pr-4", className)} {...props}>
      {children}
    </td>
  );
}
