"use client";

import Link from "next/link";
import { Fragment } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/shared/utils";
import { IconChevronRight } from "@/shared/icons";

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

export interface BreadcrumbProps {
  items: readonly BreadcrumbItem[];
  className?: string;
}

export function Breadcrumb({ items, className }: BreadcrumbProps) {
  const t = useTranslations("common");

  if (items.length === 0) return null;

  return (
    <nav aria-label={t("breadcrumb")} className={cn("min-w-0", className)}>
      <ol className="flex flex-wrap items-center gap-1 text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          return (
            <Fragment key={`${item.label}-${index}`}>
              {index > 0 ? (
                <li aria-hidden="true" className="flex items-center">
                  <IconChevronRight className="size-4 text-ecmp-text-secondary" />
                </li>
              ) : null}
              <li className="min-w-0">
                {isLast || !item.href ? (
                  <span
                    aria-current={isLast ? "page" : undefined}
                    className={cn(
                      "truncate",
                      isLast && "font-medium text-ecmp-text-primary",
                    )}
                  >
                    {item.label}
                  </span>
                ) : (
                  <Link
                    href={item.href}
                    className="truncate rounded-[var(--ecmp-radius-sm)] hover:text-ecmp-primary focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus"
                  >
                    {item.label}
                  </Link>
                )}
              </li>
            </Fragment>
          );
        })}
      </ol>
    </nav>
  );
}
