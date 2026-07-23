"use client";

import type { ReactNode } from "react";
import { SidebarProvider } from "@/shared/hooks";
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
  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full overflow-x-hidden bg-ecmp-background">
        <Sidebar />
        <div className="flex min-w-0 flex-1 flex-col">
          <Header />
          <main id="main-content" className="min-w-0 flex-1">
            {children}
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
