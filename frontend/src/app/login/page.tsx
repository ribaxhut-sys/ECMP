"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { PASSWORD_CHANGE_ROUTE } from "@/features/auth";
import { AuthLayout, IdentityBrand } from "@/shared/layouts";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Input,
  Skeleton,
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
      <AuthLayout toolbar={<LanguageSwitcher variant="compact" />}>
        <Card className="shadow-ecmp-raised">
          <CardBody className="space-y-[var(--ecmp-panel-gap)] p-[var(--ecmp-panel-gap)]">
            <Skeleton rows={4} />
          </CardBody>
        </Card>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout toolbar={<LanguageSwitcher variant="compact" />}>
      <Card className="shadow-ecmp-raised">
        <CardBody className="p-[var(--ecmp-panel-gap)] md:p-[var(--ecmp-section-gap)]">
          <form
            onSubmit={onSubmit}
            className="space-y-[var(--ecmp-form-gap)]"
          >
            <IdentityBrand
              title={t("signIn")}
              subtitle={t("signInSubtitle")}
            />

            <Input
              name="username"
              label={t("usernameOrEmail")}
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />

            <div className="space-y-2">
              <Input
                name="password"
                type="password"
                label={t("password")}
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <div className="flex justify-end">
                <Link
                  href="/forgot-password"
                  className="min-h-[var(--ecmp-touch-min)] inline-flex items-center text-[length:var(--ecmp-font-helper-size)] text-ecmp-primary underline-offset-2 transition-colors duration-[var(--ecmp-duration-normal)] ease-[var(--ecmp-ease-hover)] hover:underline focus-visible:outline-none focus-visible:ring-[length:var(--ecmp-focus-ring-width)] focus-visible:ring-ecmp-focus focus-visible:ring-offset-[length:var(--ecmp-focus-ring-offset)]"
                >
                  {t("forgotPassword")}
                </Link>
              </div>
            </div>

            {error ? (
              <Alert tone="danger" title={t("signInFailed")} description={error} />
            ) : null}

            <Button
              type="submit"
              fullWidth
              loading={submitting}
              className="min-h-[var(--ecmp-touch-min)]"
            >
              {submitting ? t("signingIn") : t("signIn")}
            </Button>
          </form>
        </CardBody>
      </Card>
    </AuthLayout>
  );
}
