"use client";

import { useTranslations } from "next-intl";
import { Button } from "@/shared/ui/button";
import type { TableDensity } from "@/shared/ui/table";
import { cn } from "@/shared/utils";

export interface DensityToggleProps {
  value: TableDensity;
  onChange: (next: TableDensity) => void;
  comfortableLabel?: string;
  compactLabel?: string;
  className?: string;
}

/**
 * Segmented comfortable/compact control for workspace tables.
 * Visual density only — does not change fetched data.
 */
export function DensityToggle({
  value,
  onChange,
  comfortableLabel,
  compactLabel,
  className,
}: DensityToggleProps) {
  const t = useTranslations("table");
  const comfortable = comfortableLabel ?? t("densityComfortable");
  const compact = compactLabel ?? t("densityCompact");

  return (
    <div
      className={cn(
        "flex gap-1 rounded-[var(--ecmp-radius-md)] border border-ecmp-border p-0.5",
        className,
      )}
      role="group"
      aria-label={t("densityLabel")}
    >
      <Button
        type="button"
        size="sm"
        variant={value === "comfortable" ? "secondary" : "ghost"}
        aria-pressed={value === "comfortable"}
        onClick={() => onChange("comfortable")}
        className="!h-9 !min-h-9 px-2.5 text-[length:var(--ecmp-font-helper-size)]"
      >
        {comfortable}
      </Button>
      <Button
        type="button"
        size="sm"
        variant={value === "compact" ? "secondary" : "ghost"}
        aria-pressed={value === "compact"}
        onClick={() => onChange("compact")}
        className="!h-9 !min-h-9 px-2.5 text-[length:var(--ecmp-font-helper-size)]"
      >
        {compact}
      </Button>
    </div>
  );
}
