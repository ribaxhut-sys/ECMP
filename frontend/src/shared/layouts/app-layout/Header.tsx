"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  identityInitials,
  primaryRoleLabel,
} from "@/features/auth/identityHelpers";
import { isShellUiBatch } from "@/shared/config/uiBatch";
import { IconLogout, IconMenu, IconSearch } from "@/shared/icons";
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
  shortcutLabel,
  autoFocus,
  showShortcut = false,
}: {
  id: string;
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
  label: string;
  shortcutLabel: string;
  autoFocus?: boolean;
  showShortcut?: boolean;
}) {
  return (
    <>
      <label className="sr-only" htmlFor={id}>
        {label}
      </label>
      <div className="relative">
        <IconSearch className="pointer-events-none absolute top-1/2 left-3.5 size-5 -translate-y-1/2 text-ecmp-muted" />
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
            "ecmp-touch w-full border border-ecmp-border/80 bg-ecmp-surface",
            "rounded-[var(--ecmp-radius-search)] py-2.5 pl-11",
            showShortcut ? "pr-20" : "pr-3.5",
            "text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-primary shadow-[var(--ecmp-shadow-search)]",
            "placeholder:text-ecmp-muted",
            "transition-[border-color,background-color,box-shadow] duration-[var(--ecmp-duration-fast)] ease-[var(--ecmp-ease-hover)]",
            "hover:border-ecmp-border hover:bg-ecmp-surface",
            "focus-visible:border-ecmp-primary/40 focus-visible:shadow-[var(--ecmp-shadow-search)]",
            "focus-visible:outline-none focus-visible:ring-[length:var(--ecmp-focus-ring-width)] focus-visible:ring-ecmp-focus",
          )}
        />
        {showShortcut ? (
          <kbd
            className={cn(
              "pointer-events-none absolute top-1/2 right-3 hidden -translate-y-1/2 sm:inline-flex",
              "items-center rounded-[var(--ecmp-radius-sm)] border border-ecmp-border bg-ecmp-surface-sunken px-1.5 py-0.5",
              "text-[length:var(--ecmp-font-caption-size)] font-medium tracking-wide text-ecmp-muted",
            )}
            aria-hidden
          >
            {shortcutLabel}
          </kbd>
        ) : null}
      </div>
    </>
  );
}

function ProfileChip({
  displayName,
  roleLabel,
  onlineLabel,
  profileLabel,
  onOpenProfile,
}: {
  displayName: string;
  roleLabel: string;
  onlineLabel: string;
  profileLabel: string;
  onOpenProfile: () => void;
}) {
  const initials = identityInitials(displayName, "U");

  return (
    <button
      type="button"
      className={cn(
        "inline-flex min-h-[var(--ecmp-touch-min)] items-center gap-2.5 rounded-[var(--ecmp-radius-lg)] px-2 py-1.5",
        "text-left transition-[background-color,transform] duration-[var(--ecmp-duration-fast)] ease-[var(--ecmp-ease-hover)]",
        "hover:bg-ecmp-hover active:scale-[0.98]",
        "focus-visible:outline-none focus-visible:ring-[length:var(--ecmp-focus-ring-width)] focus-visible:ring-ecmp-focus",
      )}
      onClick={onOpenProfile}
      title={profileLabel}
      aria-label={profileLabel}
    >
      <span className="relative shrink-0">
        <span
          aria-hidden
          className={cn(
            "flex size-9 items-center justify-center rounded-full",
            "bg-ecmp-primary-muted font-semibold tracking-wide text-ecmp-primary",
            "ring-1 ring-inset ring-ecmp-primary/15",
            "text-[length:var(--ecmp-font-overline-size)]",
          )}
        >
          {initials}
        </span>
        <span
          className="absolute right-0 bottom-0 size-2.5 rounded-full border-2 border-ecmp-surface bg-ecmp-success"
          title={onlineLabel}
          aria-hidden
        />
        <span className="sr-only">{onlineLabel}</span>
      </span>
      <span className="hidden min-w-0 flex-col sm:flex">
        <span className="max-w-[9rem] truncate text-[length:var(--ecmp-font-body-small-size)] font-medium text-ecmp-text-primary">
          {displayName}
        </span>
        <span className="max-w-[9rem] truncate text-[length:var(--ecmp-font-caption-size)] text-ecmp-muted">
          {roleLabel}
        </span>
      </span>
    </button>
  );
}

export function Header() {
  const router = useRouter();
  const {
    user,
    logout,
    hasPermission,
    isMockSession,
    mockPersona,
    officerWorkMode,
    setOfficerWorkMode,
  } = useAuth();
  const { toggle, open } = useSidebar();
  const t = useTranslations("header");
  const tShell = useTranslations("shell");
  const tCommon = useTranslations("common");
  const displayName = user?.fullName ?? user?.username ?? tCommon("user");
  const roleLabel = primaryRoleLabel(user, t("roleFallback"));
  const batchB0 = isShellUiBatch() || isMockSession;
  /** B0: no complaint search (out of scope). */
  const canSearch = !batchB0 && hasPermission("complaints:read");
  const [keyword, setKeyword] = useState("");
  const [mobileSearchOpen, setMobileSearchOpen] = useState(false);

  function switchOfficerMode(mode: "intake" | "handling"): void {
    setOfficerWorkMode(mode);
    router.push(mode === "intake" ? "/workspace" : "/queue");
  }

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

  useEffect(() => {
    if (!canSearch) return;

    function onKeyDown(event: KeyboardEvent): void {
      if (!(event.ctrlKey || event.metaKey) || event.key.toLowerCase() !== "k") {
        return;
      }
      event.preventDefault();

      const target = event.target;
      if (
        target instanceof HTMLElement &&
        (target.id === "global-search" || target.id === "global-search-mobile")
      ) {
        target.focus();
        if (target instanceof HTMLInputElement) {
          target.select();
        }
        return;
      }

      const desktop = window.matchMedia("(min-width: 768px)").matches;
      if (desktop) {
        const input = document.getElementById("global-search");
        input?.focus();
        if (input instanceof HTMLInputElement) {
          input.select();
        }
        return;
      }
      setMobileSearchOpen(true);
      window.requestAnimationFrame(() => {
        const mobile = document.getElementById("global-search-mobile");
        mobile?.focus();
        if (mobile instanceof HTMLInputElement) {
          mobile.select();
        }
      });
    }

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [canSearch]);

  return (
    <header
      className={cn(
        "relative sticky top-0 z-[var(--ecmp-z-sticky-header)]",
        "flex h-[var(--ecmp-header-height)] items-center gap-3",
        "border-b border-ecmp-border/80 bg-ecmp-surface/90 px-[var(--ecmp-page-gutter)] backdrop-blur-md",
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
          className="absolute left-1/2 top-1/2 hidden w-full max-w-[28rem] -translate-x-1/2 -translate-y-1/2 px-4 md:block"
          role="search"
        >
          <SearchField
            id="global-search"
            value={keyword}
            onChange={setKeyword}
            placeholder={t("searchPlaceholder")}
            label={t("searchComplaints")}
            shortcutLabel={t("searchShortcut")}
            showShortcut
          />
        </form>
      ) : null}

      <div className="ml-auto flex items-center gap-1 sm:gap-1.5">
        {batchB0 && mockPersona === "complaint_officer" ? (
          <div
            className="mr-1 hidden items-center gap-1 rounded-[var(--ecmp-radius-md)] border border-ecmp-border/80 p-0.5 sm:flex"
            role="group"
            aria-label={tShell("workModeLabel")}
          >
            <Button
              type="button"
              variant={officerWorkMode === "intake" ? "secondary" : "ghost"}
              size="sm"
              className="!min-h-8 px-2 text-[length:var(--ecmp-font-caption-size)]"
              aria-pressed={officerWorkMode === "intake"}
              onClick={() => switchOfficerMode("intake")}
            >
              {tShell("modeIntake")}
            </Button>
            <Button
              type="button"
              variant={officerWorkMode === "handling" ? "secondary" : "ghost"}
              size="sm"
              className="!min-h-8 px-2 text-[length:var(--ecmp-font-caption-size)]"
              aria-pressed={officerWorkMode === "handling"}
              onClick={() => switchOfficerMode("handling")}
            >
              {tShell("modeHandling")}
            </Button>
          </div>
        ) : null}

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

        <LanguageSwitcher variant="compact" className="hidden sm:inline-flex" />

        <ProfileChip
          displayName={displayName}
          roleLabel={roleLabel}
          onlineLabel={t("online")}
          profileLabel={t("openProfile")}
          onOpenProfile={() => router.push("/profile")}
        />

        <Button
          variant="ghost"
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
            "bg-ecmp-surface/95 px-[var(--ecmp-page-gutter)] py-3 shadow-ecmp-floating backdrop-blur-md md:hidden",
          )}
          role="search"
        >
          <SearchField
            id="global-search-mobile"
            value={keyword}
            onChange={setKeyword}
            placeholder={t("searchPlaceholder")}
            label={t("searchComplaints")}
            shortcutLabel={t("searchShortcut")}
            showShortcut={false}
            autoFocus
          />
        </form>
      ) : null}
    </header>
  );
}
