"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { PASSWORD_CHANGE_ROUTE } from "@/features/auth";
import { AuthLayout } from "@/shared/layouts";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Input,
  Loading,
} from "@/shared/ui";
import { LanguageSwitcher } from "@/shared/i18n";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";

export default function LoginPage() {
  const router = useRouter();
  const { status, login, user } = useAuth();
  const t = useTranslations("auth");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (status === "authenticated") {
      if (user?.forcePasswordChange) {
        router.replace(PASSWORD_CHANGE_ROUTE);
      } else {
        router.replace("/dashboard");
      }
    }
  }, [status, router, user?.forcePasswordChange]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(username, password);
      // AuthProvider updates user asynchronously via loadMe inside login.
      // Redirect is handled by the authenticated effect above after me loads.
    } catch (err) {
      setError(
        resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError") ||
          t("loginFailed"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (status === "loading" || status === "authenticated") {
    return (
      <AuthLayout>
        <Loading label={t("checkingSession")} />
      </AuthLayout>
    );
  }

  return (
    <AuthLayout>
      <div className="mb-3 flex justify-end">
        <LanguageSwitcher variant="compact" />
      </div>
      <Card>
        <CardBody>
          <form
            onSubmit={onSubmit}
            className="space-y-[var(--ecmp-form-gap)]"
          >
            <div className="space-y-2">
              <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-primary">
                {tCommon("appName")}
              </p>
              <h1 className="text-[length:var(--ecmp-font-page-title-size)] font-[number:var(--ecmp-font-page-title-weight)] leading-[var(--ecmp-font-page-title-line)] tracking-tight text-ecmp-text-primary">
                {t("signIn")}
              </h1>
              <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                {t("signInSubtitle")}
              </p>
            </div>

            <Input
              name="username"
              label={t("usernameOrEmail")}
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />

            <Input
              name="password"
              type="password"
              label={t("password")}
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            {error ? (
              <Alert tone="danger" title={t("signInFailed")} description={error} />
            ) : null}

            <Button type="submit" fullWidth loading={submitting}>
              {submitting ? t("signingIn") : t("signIn")}
            </Button>

            <p className="text-center text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              <Link
                href="/forgot-password"
                className="text-ecmp-primary underline-offset-2 hover:underline focus-visible:outline-none focus-visible:ring-[length:var(--ecmp-focus-ring-width)] focus-visible:ring-ecmp-focus focus-visible:ring-offset-[length:var(--ecmp-focus-ring-offset)]"
              >
                {t("forgotPassword")}
              </Link>
            </p>
          </form>
        </CardBody>
      </Card>
    </AuthLayout>
  );
}
