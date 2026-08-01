"use client";

import type { ReactNode } from "react";
import { useCallback } from "react";
import { AuthProvider, useAuth } from "@/auth/AuthProvider";
import { LocaleProvider } from "@/shared/i18n";
import { GlobalLoadingBar } from "@/shared/ui/loading/GlobalLoadingBar";
import { updatePreferredLanguage } from "@/lib/api/users";
import type { AppLocale } from "@/i18n/config";
import { ToastProvider } from "./ToastProvider";

type Messages = Record<string, unknown>;

function LocaleAwareProviders({
  children,
  initialLocale,
  initialMessages,
}: {
  children: ReactNode;
  initialLocale: AppLocale;
  initialMessages: Messages;
}) {
  const { user, status, patchUser } = useAuth();

  const onLocalePersisted = useCallback(
    async (locale: AppLocale) => {
      if (status !== "authenticated") return;
      await updatePreferredLanguage(locale);
      patchUser({ preferredLanguage: locale });
    },
    [status, patchUser],
  );

  return (
    <LocaleProvider
      initialLocale={initialLocale}
      initialMessages={initialMessages}
      userPreferredLanguage={user?.preferredLanguage}
      onLocalePersisted={onLocalePersisted}
    >
      <ToastProvider>
        <GlobalLoadingBar />
        {children}
      </ToastProvider>
    </LocaleProvider>
  );
}

/**
 * Root client providers: Auth → Locale (next-intl) → Toast / loading.
 */
export function AppProviders({
  children,
  locale,
  messages,
}: {
  children: ReactNode;
  locale: AppLocale;
  messages: Messages;
}) {
  return (
    <AuthProvider>
      <LocaleAwareProviders initialLocale={locale} initialMessages={messages}>
        {children}
      </LocaleAwareProviders>
    </AuthProvider>
  );
}
