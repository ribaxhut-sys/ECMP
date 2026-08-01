"use client";

import type { HTMLAttributes, ReactNode, TdHTMLAttributes, ThHTMLAttributes } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/shared/utils";

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
}

export interface TableProps<T> extends HTMLAttributes<HTMLDivElement> {
  columns: readonly TableColumn<T>[];
  rows: readonly T[];
  getRowKey: (row: T, index: number) => string;
  caption?: string;
  emptyMessage?: string;
}

export function Table<T>({
  columns,
  rows,
  getRowKey,
  caption,
  emptyMessage,
  className,
  ...props
}: TableProps<T>) {
  const t = useTranslations("table");

  if (rows.length === 0) {
    return (
      <p className="rounded-[var(--ecmp-radius-md)] border border-dashed border-ecmp-border px-4 py-8 text-center text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
        {emptyMessage ?? t("empty")}
      </p>
    );
  }

  return (
    <div className={cn("w-full", className)} {...props}>
      {/* Desktop / tablet table */}
      <div className="hidden md:block">
        <table className="min-w-full text-left text-[length:var(--ecmp-font-body-size)]">
          {caption ? <caption className="sr-only">{caption}</caption> : null}
          <thead className="border-b border-ecmp-border text-ecmp-text-secondary">
            <tr>
              {columns.map((column) => (
                <Th
                  key={column.key}
                  className={column.headerClassName}
                >
                  {column.header}
                </Th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr
                key={getRowKey(row, index)}
                className="border-b border-ecmp-border/70 align-top last:border-0"
              >
                {columns.map((column) => (
                  <Td key={column.key} className={column.className}>
                    {column.cell(row)}
                  </Td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile stacked cards — avoids horizontal scroll */}
      <ul className="flex flex-col gap-3 md:hidden" aria-label={caption}>
        {rows.map((row, index) => (
          <li
            key={getRowKey(row, index)}
            className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface p-4 shadow-ecmp-sm"
          >
            <dl className="space-y-3">
              {columns
                .filter((column) => !column.hideOnMobile)
                .map((column) => (
                  <div key={column.key}>
                    <dt className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary">
                      {column.mobileLabel ?? column.header}
                    </dt>
                    <dd className="mt-1 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                      {column.cell(row)}
                    </dd>
                  </div>
                ))}
            </dl>
          </li>
        ))}
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
      className={cn("py-3 pr-4 font-medium last:pr-0", className)}
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
    <td className={cn("py-3 pr-4 last:pr-0", className)} {...props}>
      {children}
    </td>
  );
}
