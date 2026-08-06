"use client";

import { useTranslations } from "next-intl";
import type { UserRef } from "@/lib/api";
import { cn } from "@/shared/utils";
import { Badge } from "@/shared/ui";
import { DirectoryAvatar } from "./DirectoryAvatar";
import { DirectoryRoleBadge } from "./DirectoryRoleBadge";
import { formatWhen } from "./directoryHelpers";

export function DirectoryPeopleList({
  rows,
  selectedId,
  unitLabelByBranchId,
  onSelect,
}: {
  rows: readonly UserRef[];
  selectedId: string | null;
  unitLabelByBranchId: ReadonlyMap<string, string>;
  onSelect: (user: UserRef) => void;
}) {
  const t = useTranslations("users");
  const tCommon = useTranslations("common");

  return (
    <div
      className="overflow-hidden rounded-[var(--ecmp-radius-card)] border border-ecmp-border bg-ecmp-surface"
      role="listbox"
      aria-label={t("directoryListLabel")}
      aria-activedescendant={selectedId ? `directory-person-${selectedId}` : undefined}
    >
      <div
        className={cn(
          "sticky top-0 z-[1] hidden border-b border-ecmp-border bg-ecmp-surface-sunken px-4 py-2.5 text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary md:grid",
          "md:grid-cols-[minmax(0,2.4fr)_minmax(0,1.4fr)_minmax(0,0.9fr)]",
        )}
      >
        <span>{t("personColumn")}</span>
        <span>
          {t("role")} / {t("unit")}
        </span>
        <span>{tCommon("status")}</span>
      </div>

      <ul className="divide-y divide-ecmp-border">
        {rows.map((row) => {
          const selected = row.id === selectedId;
          const updated = formatWhen(row.updatedAt);

          return (
            <li key={row.id} role="none">
              <div
                id={`directory-person-${row.id}`}
                role="option"
                aria-selected={selected}
                tabIndex={0}
                onClick={() => onSelect(row)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    onSelect(row);
                  }
                }}
                className={cn(
                  "grid cursor-pointer grid-cols-1 gap-3 border-l-[3px] border-l-transparent px-4 py-3.5 transition-[background-color,border-color] duration-[var(--ecmp-duration-normal)] ease-[var(--ecmp-ease-hover)]",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-ecmp-focus",
                  "hover:bg-ecmp-hover",
                  selected &&
                    "border-l-ecmp-primary bg-ecmp-primary-muted/50",
                  "md:grid-cols-[minmax(0,2.4fr)_minmax(0,1.4fr)_minmax(0,0.9fr)] md:items-center",
                )}
              >
                <div className="flex min-w-0 items-center gap-3">
                  <DirectoryAvatar
                    fullName={row.fullName}
                    username={row.username}
                    size="md"
                  />
                  <div className="min-w-0">
                    <p className="truncate text-[length:var(--ecmp-font-body-size)] font-[number:var(--ecmp-font-card-title-weight)] text-ecmp-text-primary">
                      {row.fullName}
                    </p>
                    <p className="truncate text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                      @{row.username}
                    </p>
                    {updated ? (
                      <p className="mt-0.5 truncate text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary md:hidden">
                        {t("lastUpdated")}: {updated}
                      </p>
                    ) : null}
                  </div>
                </div>

                <div className="min-w-0 space-y-1">
                  <DirectoryRoleBadge user={row} />
                  <p className="truncate text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                    <span className="md:hidden">{t("unit")}: </span>
                    {row.branchId
                      ? unitLabelByBranchId.get(row.branchId) ?? t("unitUnknown")
                      : t("locationHeadOffice")}
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  <Badge tone={row.isActive ? "success" : "neutral"}>
                    {row.isActive ? t("statusActive") : t("statusInactive")}
                  </Badge>
                  {updated ? (
                    <span className="hidden text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary lg:inline">
                      {updated}
                    </span>
                  ) : null}
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
