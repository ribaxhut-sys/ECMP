"use client";

import type { ReactNode } from "react";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { SidebarProvider } from "@/shared/hooks";
import { NavPreferenceProvider } from "@/shared/navigation";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

export interface AppLayoutProps {
  children: ReactNode;
}

/**
 * Enterprise shell: Header + Sidebar + Content.
 * Desktop: persistent sidebar. Mobile/tablet: drawer navigation.
 *
 * Viewport-locked shell (`h-dvh` + overflow hidden): only `<main>` scrolls.
 * Document-level scroll previously dragged the sidebar with the page, and
 * `overflow-x-hidden` on the outer flex broke `position: sticky`.
 */
export function AppLayout({ children }: AppLayoutProps) {
  const tCommon = useTranslations("common");
  const pathname = usePathname();

  return (
    <SidebarProvider>
      <NavPreferenceProvider>
        <div className="relative flex h-dvh w-full overflow-hidden overscroll-none bg-ecmp-background">
          <a
            href="#main-content"
            className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[var(--ecmp-z-loading)] focus:rounded-[var(--ecmp-radius-md)] focus:bg-ecmp-surface focus:px-3 focus:py-2 focus:text-ecmp-text-primary focus:shadow-ecmp-floating"
          >
            {tCommon("skipToContent")}
          </a>
          <Sidebar />
          <div className="relative flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden bg-ecmp-background">
            <Header />
            <main
              id="main-content"
              className="relative min-h-0 min-w-0 flex-1 overflow-auto overscroll-contain bg-ecmp-background"
              tabIndex={-1}
            >
              <div
                key={pathname}
                className="animate-[ecmp-content-fade_var(--ecmp-duration-normal)_var(--ecmp-ease-enter)] motion-reduce:animate-none"
              >
                {children}
              </div>
            </main>
          </div>
        </div>
      </NavPreferenceProvider>
    </SidebarProvider>
  );
}
