import type { HTMLAttributes, ReactNode } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/shared/utils";
import { Button } from "@/shared/ui/button";

export interface PaginationProps extends HTMLAttributes<HTMLElement> {
  /** Summary text e.g. "Page 2 of 10" — parent formats. */
  summary?: ReactNode;
  pageSizeSlot?: ReactNode;
  /** Pre-translated — caller owns locale (`common.previous`). Falls back to a translated default if omitted. */
  previousLabel?: string;
  /** Pre-translated — caller owns locale (`common.next`). Falls back to a translated default if omitted. */
  nextLabel?: string;
  onPrevious?: () => void;
  onNext?: () => void;
  previousDisabled?: boolean;
  nextDisabled?: boolean;
  /** Optional page number buttons — parent decides which pages to show. */
  pages?: readonly {
    page: number;
    label?: string;
    current?: boolean;
    disabled?: boolean;
    onSelect?: () => void;
  }[];
}

/**
 * Presentational pagination chrome. Parent owns page state and fetch logic.
 */
export function Pagination({
  className,
  summary,
  pageSizeSlot,
  previousLabel,
  nextLabel,
  onPrevious,
  onNext,
  previousDisabled,
  nextDisabled,
  pages,
  ...props
}: PaginationProps) {
  const tCommon = useTranslations("common");
  return (
    <nav
      aria-label={tCommon("paginationNav")}
      className={cn(
        "flex flex-col gap-3 border-t border-ecmp-border pt-[var(--ecmp-panel-gap)] sm:flex-row sm:items-center sm:justify-between",
        className,
      )}
      {...props}
    >
      <div className="flex flex-wrap items-center gap-3 text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
        {summary}
        {pageSizeSlot}
      </div>
      <div className="flex flex-wrap items-center gap-1">
        <Button
          variant="outline"
          size="sm"
          onClick={onPrevious}
          disabled={previousDisabled || !onPrevious}
        >
          {previousLabel ?? tCommon("previous")}
        </Button>
        {pages?.map((item) => (
          <Button
            key={item.page}
            variant={item.current ? "secondary" : "ghost"}
            size="sm"
            aria-current={item.current ? "page" : undefined}
            disabled={item.disabled}
            onClick={item.onSelect}
            className="!min-w-10"
          >
            {item.label ?? item.page}
          </Button>
        ))}
        <Button
          variant="outline"
          size="sm"
          onClick={onNext}
          disabled={nextDisabled || !onNext}
        >
          {nextLabel ?? tCommon("next")}
        </Button>
      </div>
    </nav>
  );
}
