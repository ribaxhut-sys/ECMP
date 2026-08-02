"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  IconBell,
  IconLogout,
  IconMenu,
  IconSearch,
  IconTheme,
  IconUser,
} from "@/shared/icons";
import { useSidebar } from "@/shared/hooks";
import { Button } from "@/shared/ui/button";
import { LanguageSwitcher } from "@/shared/i18n";
import { cn } from "@/shared/utils";

function SearchField({
  id,
  value,
  onChange,
  placeholder,
  label,
  autoFocus,
}: {
  id: string;
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
  label: string;
  autoFocus?: boolean;
}) {
  return (
    <>
      <label className="sr-only" htmlFor={id}>
        {label}
      </label>
      <div className="relative">
        <IconSearch className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-ecmp-muted" />
        <input
          id={id}
          name="keyword"
          type="search"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          maxLength={200}
          autoFocus={autoFocus}
          className={cn(
            "ecmp-touch w-full rounded-[var(--ecmp-radius-input)] border border-ecmp-border bg-ecmp-surface-sunken",
            "py-2 pr-3 pl-10 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-primary",
            "placeholder:text-ecmp-muted",
            "transition-[border-color,background-color,box-shadow] duration-[var(--ecmp-duration-fast)] ease-[var(--ecmp-ease-hover)]",
            "hover:border-ecmp-secondary hover:bg-ecmp-surface",
          )}
        />
      </div>
    </>
  );
}

export function Header() {
  const router = useRouter();
  const { user, logout, hasPermission } = useAuth();
  const { toggle, open } = useSidebar();
  const t = useTranslations("header");
  const tCommon = useTranslations("common");
  const displayName = user?.fullName ?? user?.username ?? tCommon("user");
  const canSearch = hasPermission("complaints:read");
  const [keyword, setKeyword] = useState("");
  const [mobileSearchOpen, setMobileSearchOpen] = useState(false);

  function submitSearch(event?: FormEvent): void {
    event?.preventDefault();
    if (!canSearch) return;
    const trimmed = keyword.trim();
    const query = trimmed
      ? `?keyword=${encodeURIComponent(trimmed)}`
      : "";
    router.push(`/complaints${query}`);
    setMobileSearchOpen(false);
  }

  return (
    <header
      className={cn(
        "relative sticky top-0 z-[var(--ecmp-z-sticky-header)]",
        "flex h-[var(--ecmp-header-height)] items-center gap-3",
        "border-b border-ecmp-border bg-ecmp-surface/95 px-[var(--ecmp-page-gutter)] shadow-ecmp-raised backdrop-blur-sm",
        "sm:px-6 lg:px-8",
      )}
    >
      <Button
        variant="ghost"
        size="sm"
        className="!min-h-[var(--ecmp-touch-min)] !min-w-[var(--ecmp-touch-min)] px-0 lg:hidden"
        aria-label={open ? tCommon("closeMenu") : tCommon("openMenu")}
        aria-expanded={open}
        aria-controls="mobile-sidebar"
        onClick={toggle}
      >
        <IconMenu />
      </Button>

      {canSearch ? (
        <form
          onSubmit={submitSearch}
          className="hidden min-w-0 flex-1 md:block md:max-w-md lg:max-w-lg"
          role="search"
        >
          <SearchField
            id="global-search"
            value={keyword}
            onChange={setKeyword}
            placeholder={t("searchPlaceholder")}
            label={t("searchComplaints")}
          />
        </form>
      ) : (
        <div className="hidden flex-1 md:block" />
      )}

      <div className="ml-auto flex items-center gap-1 sm:gap-2">
        {canSearch ? (
          <Button
            variant="ghost"
            size="sm"
            className="!min-h-[var(--ecmp-touch-min)] !min-w-[var(--ecmp-touch-min)] px-0 md:hidden"
            aria-label={mobileSearchOpen ? t("closeSearch") : t("searchComplaints")}
            aria-expanded={mobileSearchOpen}
            onClick={() => setMobileSearchOpen((prev) => !prev)}
          >
            <IconSearch />
          </Button>
        ) : null}

        <Button
          variant="ghost"
          size="sm"
          className="!min-h-[var(--ecmp-touch-min)] !min-w-[var(--ecmp-touch-min)] px-0"
          aria-label={t("notificationsSoon")}
          disabled
        >
          <IconBell />
        </Button>

        <Button
          variant="ghost"
          size="sm"
          className="!min-h-[var(--ecmp-touch-min)] !min-w-[var(--ecmp-touch-min)] px-0"
          aria-label={t("themeSoon")}
          disabled
          title={t("themeSoonTitle")}
        >
          <IconTheme />
        </Button>

        <LanguageSwitcher variant="compact" className="hidden sm:inline-flex" />

        <button
          type="button"
          className={cn(
            "hidden items-center gap-2 rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface-sunken px-3 py-2 sm:inline-flex",
            "text-left transition-[background-color,border-color] duration-[var(--ecmp-duration-fast)] ease-[var(--ecmp-ease-hover)]",
            "hover:border-ecmp-secondary hover:bg-ecmp-hover",
            "min-h-[var(--ecmp-touch-min)]",
          )}
          onClick={() => router.push("/profile")}
          title={t("openProfile")}
        >
          <span className="flex size-7 items-center justify-center rounded-full bg-ecmp-primary-muted text-ecmp-primary">
            <IconUser className="size-4" aria-hidden />
          </span>
          <span className="max-w-[10rem] truncate text-[length:var(--ecmp-font-body-small-size)] font-medium text-ecmp-text-primary">
            {displayName}
          </span>
        </button>

        <Button
          variant="outline"
          size="sm"
          leftIcon={<IconLogout className="size-4" />}
          aria-label={t("signOut")}
          onClick={() => {
            void logout().then(() => router.replace("/login"));
          }}
        >
          <span className="hidden sm:inline">{t("logout")}</span>
        </Button>
      </div>

      {canSearch && mobileSearchOpen ? (
        <form
          onSubmit={submitSearch}
          className={cn(
            "absolute inset-x-0 top-full z-[var(--ecmp-z-dropdown)] border-b border-ecmp-border",
            "bg-ecmp-surface px-[var(--ecmp-page-gutter)] py-3 shadow-ecmp-floating md:hidden",
          )}
          role="search"
        >
          <SearchField
            id="global-search-mobile"
            value={keyword}
            onChange={setKeyword}
            placeholder={t("searchPlaceholder")}
            label={t("searchComplaints")}
            autoFocus
          />
        </form>
      ) : null}
    </header>
  );
}
