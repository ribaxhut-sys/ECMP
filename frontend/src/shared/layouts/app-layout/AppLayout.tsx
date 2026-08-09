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
 */
export function AppLayout({ children }: AppLayoutProps) {
  const tCommon = useTranslations("common");
  const pathname = usePathname();

  return (
    <SidebarProvider>
      <NavPreferenceProvider>
        <div className="flex min-h-screen w-full overflow-x-hidden bg-ecmp-background">
          <a
            href="#main-content"
            className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[var(--ecmp-z-loading)] focus:rounded-[var(--ecmp-radius-md)] focus:bg-ecmp-surface focus:px-3 focus:py-2 focus:text-ecmp-text-primary focus:shadow-ecmp-floating"
          >
            {tCommon("skipToContent")}
          </a>
          <Sidebar />
          <div className="flex min-w-0 flex-1 flex-col bg-ecmp-background">
            <Header />
            <main
              id="main-content"
              className="min-w-0 flex-1 bg-ecmp-background"
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
