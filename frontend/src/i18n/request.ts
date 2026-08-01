import { cookies } from "next/headers";
import { getRequestConfig } from "next-intl/server";
import {
  DEFAULT_LOCALE,
  LOCALE_COOKIE,
  isAppLocale,
  type AppLocale,
} from "./config";
import fallbackIdMessages from "../../messages/id.json";

type Messages = Record<string, unknown>;

async function loadMessages(locale: AppLocale) {
  try {
    return (await import(`../../messages/${locale}.json`)).default as Messages;
  } catch {
    return (await import(`../../messages/${DEFAULT_LOCALE}.json`))
      .default as Messages;
  }
}

function lookupMessage(
  messages: Messages,
  namespace: string | undefined,
  key: string,
): string | undefined {
  const parts = [
    ...(namespace ? namespace.split(".") : []),
    ...key.split("."),
  ].filter(Boolean);
  let node: unknown = messages;
  for (const part of parts) {
    if (!node || typeof node !== "object") return undefined;
    node = (node as Record<string, unknown>)[part];
  }
  return typeof node === "string" ? node : undefined;
}

export default getRequestConfig(async () => {
  const store = await cookies();
  const cookieLocale = store.get(LOCALE_COOKIE)?.value;

  // Indonesian-first: only cookie (user choice) overrides the default.
  const locale: AppLocale = isAppLocale(cookieLocale)
    ? cookieLocale
    : DEFAULT_LOCALE;

  const messages = await loadMessages(locale);

  return {
    locale,
    messages,
    // Never surface raw key paths in the UI (L10-09R).
    getMessageFallback: ({
      namespace,
      key,
    }: {
      namespace?: string;
      key: string;
    }) =>
      lookupMessage(messages, namespace, key) ??
      lookupMessage(fallbackIdMessages as Messages, namespace, key) ??
      "…",
  };
});
