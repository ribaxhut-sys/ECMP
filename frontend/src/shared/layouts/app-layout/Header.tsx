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
    <header className="relative sticky top-0 z-30 flex h-[var(--ecmp-header-height)] items-center gap-3 border-b border-ecmp-border bg-ecmp-surface px-3 sm:px-4 lg:px-6">
      <Button
        variant="ghost"
        size="sm"
        className="!min-h-[44px] !min-w-[44px] px-0 lg:hidden"
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
          <label className="sr-only" htmlFor="global-search">
            {t("searchComplaints")}
          </label>
          <div className="relative">
            <IconSearch className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-ecmp-text-secondary" />
            <input
              id="global-search"
              name="keyword"
              type="search"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder={t("searchPlaceholder")}
              maxLength={200}
              className="ecmp-touch w-full rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface py-2 pr-3 pl-10 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary placeholder:text-ecmp-text-secondary focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus"
            />
          </div>
        </form>
      ) : (
        <div className="hidden flex-1 md:block" />
      )}

      <div className="ml-auto flex items-center gap-1 sm:gap-2">
        {canSearch ? (
          <>
            <Button
              variant="ghost"
              size="sm"
              className="!min-h-[44px] !min-w-[44px] px-0 md:hidden"
              aria-label={mobileSearchOpen ? t("closeSearch") : t("searchComplaints")}
              aria-expanded={mobileSearchOpen}
              onClick={() => setMobileSearchOpen((prev) => !prev)}
            >
              <IconSearch />
            </Button>
          </>
        ) : null}

        <Button
          variant="ghost"
          size="sm"
          className="!min-h-[44px] !min-w-[44px] px-0"
          aria-label={t("notificationsSoon")}
          disabled
        >
          <IconBell />
        </Button>

        <Button
          variant="ghost"
          size="sm"
          className="!min-h-[44px] !min-w-[44px] px-0"
          aria-label={t("themeSoon")}
          disabled
          title={t("themeSoonTitle")}
        >
          <IconTheme />
        </Button>

        <LanguageSwitcher variant="compact" className="hidden sm:inline-flex" />

        <div className="hidden items-center gap-2 rounded-[var(--ecmp-radius-md)] border border-ecmp-border px-3 py-2 sm:flex">
          <IconUser className="size-4 text-ecmp-text-secondary" />
          <button
            type="button"
            className="max-w-[10rem] truncate text-left text-[length:var(--ecmp-font-caption-size)] font-medium text-ecmp-text-primary hover:underline"
            onClick={() => router.push("/profile")}
            title={t("openProfile")}
          >
            {displayName}
          </button>
        </div>

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
          className="absolute inset-x-0 top-full border-b border-ecmp-border bg-ecmp-surface px-3 py-3 md:hidden"
          role="search"
        >
          <label className="sr-only" htmlFor="global-search-mobile">
            {t("searchComplaints")}
          </label>
          <div className="relative">
            <IconSearch className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-ecmp-text-secondary" />
            <input
              id="global-search-mobile"
              name="keyword"
              type="search"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder={t("searchPlaceholder")}
              maxLength={200}
              autoFocus
              className="ecmp-touch w-full rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface py-2 pr-3 pl-10 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary placeholder:text-ecmp-text-secondary focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus"
            />
          </div>
        </form>
      ) : null}
    </header>
  );
}
