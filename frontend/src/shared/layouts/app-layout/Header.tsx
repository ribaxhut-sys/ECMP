"use client";

import { useRouter } from "next/navigation";
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

export function Header() {
  const router = useRouter();
  const { user, logout } = useAuth();
  const { toggle, open } = useSidebar();
  const displayName = user?.fullName ?? user?.username ?? "User";

  return (
    <header className="sticky top-0 z-30 flex h-[var(--ecmp-header-height)] items-center gap-3 border-b border-ecmp-border bg-ecmp-surface px-3 sm:px-4 lg:px-6">
      <Button
        variant="ghost"
        size="sm"
        className="!min-h-[44px] !min-w-[44px] px-0 lg:hidden"
        aria-label={open ? "Close menu" : "Open menu"}
        aria-expanded={open}
        aria-controls="mobile-sidebar"
        onClick={toggle}
      >
        <IconMenu />
      </Button>

      <div className="hidden min-w-0 flex-1 md:block md:max-w-md lg:max-w-lg">
        <label className="sr-only" htmlFor="global-search">
          Global search
        </label>
        <div className="relative">
          <IconSearch className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-ecmp-text-secondary" />
          <input
            id="global-search"
            name="global-search"
            type="search"
            placeholder="Search complaints, users…"
            aria-describedby="global-search-hint"
            // UI-only placeholder — no backend integration this sprint
            className="ecmp-touch w-full rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface py-2 pr-3 pl-10 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary placeholder:text-ecmp-text-secondary focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus"
          />
          <span id="global-search-hint" className="sr-only">
            Search is a visual placeholder and is not connected to a backend yet.
          </span>
        </div>
      </div>

      <div className="ml-auto flex items-center gap-1 sm:gap-2">
        <Button
          variant="ghost"
          size="sm"
          className="!min-h-[44px] !min-w-[44px] px-0 md:hidden"
          aria-label="Search (coming soon)"
          disabled
        >
          <IconSearch />
        </Button>

        <Button
          variant="ghost"
          size="sm"
          className="!min-h-[44px] !min-w-[44px] px-0"
          aria-label="Notifications (coming soon)"
          disabled
        >
          <IconBell />
        </Button>

        <Button
          variant="ghost"
          size="sm"
          className="!min-h-[44px] !min-w-[44px] px-0"
          aria-label="Theme switch (placeholder)"
          disabled
          title="Theme switch coming soon"
        >
          <IconTheme />
        </Button>

        <div className="hidden items-center gap-2 rounded-[var(--ecmp-radius-md)] border border-ecmp-border px-3 py-2 sm:flex">
          <IconUser className="size-4 text-ecmp-text-secondary" />
          <span className="max-w-[10rem] truncate text-[length:var(--ecmp-font-caption-size)] font-medium text-ecmp-text-primary">
            {displayName}
          </span>
        </div>

        <Button
          variant="outline"
          size="sm"
          leftIcon={<IconLogout className="size-4" />}
          aria-label="Sign out"
          onClick={() => {
            void logout().then(() => router.replace("/login"));
          }}
        >
          <span className="hidden sm:inline">Logout</span>
        </Button>
      </div>
    </header>
  );
}
