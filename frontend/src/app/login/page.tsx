"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { MOCK_ACCOUNTS, mockEntryHref, readMockSession } from "@/auth/mockAuth";
import { isMockAuthEnabled, isShellUiBatch } from "@/shared/config/uiBatch";
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
  const { status, login, isMockSession } = useAuth();
  const t = useTranslations("auth");
  const tShell = useTranslations("shell");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const mockEnabled = isMockAuthEnabled();

  useEffect(() => {
    if (status !== "authenticated") return;
    if (isMockSession || isShellUiBatch()) {
      const session = readMockSession();
      router.replace(session ? mockEntryHref(session) : "/workspace");
      return;
    }
    // "/" is the post-login entry-point gate — Dashboard by default, or
    // /announcements first if the caller has an unread active announcement.
    router.replace("/");
  }, [status, router, isMockSession]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(username, password);
    } catch (err) {
      const mockMsg =
        err instanceof Error &&
        (err.message === "MOCK_USER_NOT_FOUND" ||
          err.message === "MOCK_PASSWORD_REQUIRED")
          ? tShell("mockLoginFailed")
          : null;
      setError(
        mockMsg ||
          resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError") ||
          t("loginFailed"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  function fillDemo(accountUsername: string) {
    setUsername(accountUsername);
    setPassword("mock");
    setError(null);
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
              subtitle={
                mockEnabled ? tShell("signInSubtitleMock") : t("signInSubtitle")
              }
            />

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

            <Button
              type="submit"
              fullWidth
              loading={submitting}
              className="min-h-[var(--ecmp-touch-min)]"
            >
              {submitting ? t("signingIn") : t("signIn")}
            </Button>

            {mockEnabled ? (
              <div className="space-y-2 border-t border-ecmp-border/70 pt-[var(--ecmp-form-gap)]">
                <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-muted">
                  {tShell("demoAccountsHint")}
                </p>
                <div className="flex flex-wrap gap-2">
                  {MOCK_ACCOUNTS.map((account) => (
                    <Button
                      key={account.username}
                      type="button"
                      variant="secondary"
                      size="sm"
                      onClick={() => fillDemo(account.username)}
                    >
                      {account.user.roles[0]}
                    </Button>
                  ))}
                </div>
              </div>
            ) : null}
          </form>
        </CardBody>
      </Card>
    </AuthLayout>
  );
}
