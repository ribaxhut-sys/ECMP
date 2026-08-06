/**
 * Shared component-test harness.
 *
 * Mirrors the client provider chain of `AppProviders` minus Auth (suites mock
 * `@/auth/AuthProvider` per file): real next-intl catalog + Toast context.
 * Locale is pinned to `en` so assertions read as English copy.
 */
import type { ReactElement, ReactNode } from "react";
import {
  render,
  type RenderOptions,
  type RenderResult,
} from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import { ToastProvider } from "@/shared/providers";
import enMessages from "../../messages/en.json";

export function TestProviders({ children }: { children: ReactNode }) {
  return (
    <NextIntlClientProvider
      locale="en"
      messages={enMessages}
      timeZone="Asia/Jakarta"
      now={new Date("2026-08-01T00:00:00Z")}
    >
      <ToastProvider>{children}</ToastProvider>
    </NextIntlClientProvider>
  );
}

export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, "wrapper">,
): RenderResult {
  return render(ui, { wrapper: TestProviders, ...options });
}
