"use client";

import { useTranslations } from "next-intl";
import type { UserRef } from "@/lib/api";
import { cn } from "@/shared/utils";
import { Badge, Button, type TableDensity } from "@/shared/ui";
import { DirectoryAvatar } from "./DirectoryAvatar";
import { DirectoryLocationBadge } from "./DirectoryLocationBadge";
import { DirectoryRoleBadge } from "./DirectoryRoleBadge";
import { formatBranch, formatWhen } from "./directoryHelpers";

export function DirectoryPeopleList({
  rows,
  selectedId,
  density,
  showEmail,
  canReset,
  currentUserId,
  onSelect,
  onResetPassword,
}: {
  rows: readonly UserRef[];
  selectedId: string | null;
  density: TableDensity;
  showEmail: boolean;
  canReset: boolean;
  currentUserId: string | null | undefined;
  onSelect: (user: UserRef) => void;
  onResetPassword: (user: UserRef) => void;
}) {
  const t = useTranslations("users");
  const tCommon = useTranslations("common");
  const compact = density === "compact";

  return (
    <div
      className="overflow-hidden rounded-[var(--ecmp-radius-card)] border border-ecmp-border bg-ecmp-surface"
      role="listbox"
      aria-label={t("directoryListLabel")}
      aria-activedescendant={selectedId ? `directory-person-${selectedId}` : undefined}
    >
      <div
        className={cn(
          "sticky top-0 z-[1] hidden border-b border-ecmp-border bg-ecmp-surface-sunken px-4 text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary md:grid",
          showEmail
            ? "md:grid-cols-[minmax(0,2.2fr)_minmax(0,1.2fr)_minmax(0,1fr)_minmax(0,0.9fr)_minmax(0,1fr)_auto]"
            : "md:grid-cols-[minmax(0,2.4fr)_minmax(0,1fr)_minmax(0,1fr)_minmax(0,0.9fr)_minmax(0,1fr)_auto]",
          compact ? "py-2" : "py-2.5",
        )}
      >
        <span>{t("personColumn")}</span>
        {showEmail ? <span>{t("email")}</span> : null}
        <span>{t("role")}</span>
        <span>{t("branch")}</span>
        <span>{tCommon("status")}</span>
        <span className="text-right">{tCommon("actions")}</span>
      </div>

      <ul className="divide-y divide-ecmp-border">
        {rows.map((row) => {
          const selected = row.id === selectedId;
          const updated = formatWhen(row.updatedAt);
          const isSelf = row.id === currentUserId;

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
                  "grid cursor-pointer grid-cols-1 gap-3 border-l-[3px] border-l-transparent px-4 transition-[background-color,border-color] duration-[var(--ecmp-duration-normal)] ease-[var(--ecmp-ease-hover)]",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-ecmp-focus",
                  "hover:bg-ecmp-hover",
                  selected &&
                    "border-l-ecmp-primary bg-ecmp-primary-muted/50",
                  compact ? "py-2.5" : "py-3.5",
                  showEmail
                    ? "md:grid-cols-[minmax(0,2.2fr)_minmax(0,1.2fr)_minmax(0,1fr)_minmax(0,0.9fr)_minmax(0,1fr)_auto] md:items-center"
                    : "md:grid-cols-[minmax(0,2.4fr)_minmax(0,1fr)_minmax(0,1fr)_minmax(0,0.9fr)_minmax(0,1fr)_auto] md:items-center",
                )}
              >
                <div className="flex min-w-0 items-center gap-3">
                  <DirectoryAvatar
                    fullName={row.fullName}
                    username={row.username}
                    size={compact ? "sm" : "md"}
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

                {showEmail ? (
                  <p className="truncate text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                    <span className="md:hidden">{t("email")}: </span>
                    {row.email}
                  </p>
                ) : null}

                <div>
                  <DirectoryRoleBadge user={row} />
                </div>

                <div className="flex min-w-0 flex-wrap items-center gap-1.5 text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                  <span className="md:hidden">{t("branch")}: </span>
                  <DirectoryLocationBadge user={row} />
                  <span className="truncate">
                    {formatBranch(row.branchId, t("noDepartment"))}
                  </span>
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

                <div
                  className="flex justify-start md:justify-end"
                  onClick={(event) => event.stopPropagation()}
                  onKeyDown={(event) => event.stopPropagation()}
                >
                  {canReset ? (
                    <Button
                      variant="outline"
                      size="sm"
                      className="min-h-[var(--ecmp-touch-min)] min-w-[var(--ecmp-touch-min)]"
                      disabled={!row.isActive || isSelf}
                      title={
                        isSelf
                          ? t("resetOwnPasswordHint")
                          : row.isActive
                            ? t("resetPasswordHint")
                            : t("inactiveResetHint")
                      }
                      onClick={() => onResetPassword(row)}
                    >
                      {t("resetPassword")}
                    </Button>
                  ) : (
                    <span className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                      {tCommon("emDash")}
                    </span>
                  )}
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
