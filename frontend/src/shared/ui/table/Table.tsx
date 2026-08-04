"use client";

import type {
  HTMLAttributes,
  ReactNode,
  TdHTMLAttributes,
  ThHTMLAttributes,
} from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/shared/utils";
import { Empty, type EmptyActionConfig } from "@/shared/ui/empty";
import { TableSkeleton } from "@/shared/ui/loading";

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
  emptyPrimaryAction?: ReactNode | EmptyActionConfig;
  emptySecondaryAction?: ReactNode | EmptyActionConfig;
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
  /** Optional sticky toolbar above the table (search / density / refresh / selection). */
  toolbar?: ReactNode;
}

export function Table<T>({
  columns,
  rows,
  getRowKey,
  caption,
  emptyMessage,
  emptyTitle,
  emptyAction,
  emptyPrimaryAction,
  emptySecondaryAction,
  loading = false,
  density = "comfortable",
  stickyHeader = true,
  selectedKeys,
  onRowClick,
  skeletonRows = 5,
  toolbar,
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
      <div className={cn("w-full space-y-3", className)} {...props}>
        {toolbar}
        <TableSkeleton rows={skeletonRows} columns={Math.min(columns.length, 5)} />
      </div>
    );
  }

  if (rows.length === 0) {
    const primary = emptyPrimaryAction ?? emptyAction;

    return (
      <div className={cn("w-full space-y-3", className)} {...props}>
        {toolbar}
        <Empty
          title={emptyTitle}
          description={emptyMessage ?? t("empty")}
          primaryAction={primary}
          secondaryAction={emptySecondaryAction}
        />
      </div>
    );
  }

  return (
    <div className={cn("w-full min-w-0 space-y-3", className)} {...props}>
      {toolbar}
      {/* Desktop / tablet table */}
      <div className="hidden max-w-full overflow-x-auto rounded-[var(--ecmp-radius-table)] border border-ecmp-border/80 bg-ecmp-surface shadow-ecmp-raised md:block">
        <table className="min-w-full text-left text-[length:var(--ecmp-font-body-size)]">
          {caption ? <caption className="sr-only">{caption}</caption> : null}
          <thead
            className={cn(
              "border-b border-ecmp-border/80 bg-ecmp-surface-sunken/90 text-ecmp-text-secondary backdrop-blur-sm",
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
                    "border-b border-ecmp-border/50 align-middle last:border-0",
                    "transition-[background-color,box-shadow] duration-[var(--ecmp-duration-fast)] ease-[var(--ecmp-ease-hover)]",
                    "hover:bg-ecmp-hover/90",
                    selected && "bg-ecmp-selected/80",
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
                "rounded-[var(--ecmp-radius-card)] border border-ecmp-border/80 bg-ecmp-surface p-4 shadow-ecmp-raised",
                "transition-[box-shadow,background-color,transform] duration-[var(--ecmp-duration-fast)] ease-[var(--ecmp-ease-hover)]",
                selected && "border-ecmp-primary/40 bg-ecmp-selected",
                onRowClick &&
                  "cursor-pointer hover:-translate-y-[2px] hover:shadow-ecmp-hover motion-reduce:hover:translate-y-0",
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
        "px-4 text-[length:var(--ecmp-font-overline-size)] font-semibold uppercase tracking-[0.04em] first:pl-5 last:pr-5",
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
    <td className={cn("px-4 first:pl-5 last:pr-5", className)} {...props}>
      {children}
    </td>
  );
}
