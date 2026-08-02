"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { ApiError, forgotPassword } from "@/lib/api";
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

export default function ForgotPasswordPage() {
  const router = useRouter();
  const { status } = useAuth();
  const t = useTranslations("auth");
  const tCommon = useTranslations("common");
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (status === "authenticated") {
      router.replace("/dashboard");
    }
  }, [status, router]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSuccess(null);
    const trimmed = email.trim();
    if (!trimmed || !trimmed.includes("@")) {
      setError(t("enterValidEmail"));
      return;
    }
    setSubmitting(true);
    try {
      const result = await forgotPassword(trimmed);
      setSuccess(result.message);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : t("unableToSubmit"),
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
                {t("forgotPasswordTitle")}
              </h1>
              <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                {t("forgotPasswordSubtitle")}
              </p>
            </div>

            <Input
              name="email"
              type="email"
              label={t("email")}
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            {error ? (
              <Alert tone="danger" title={t("requestFailed")} description={error} />
            ) : null}
            {success ? (
              <Alert tone="success" title={t("checkYourEmail")} description={success} />
            ) : null}

            <Button type="submit" fullWidth loading={submitting}>
              {submitting ? tCommon("sending") : t("sendResetLink")}
            </Button>

            <p className="text-center text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              <Link
                href="/login"
                className="text-ecmp-primary underline-offset-2 hover:underline focus-visible:outline-none focus-visible:ring-[length:var(--ecmp-focus-ring-width)] focus-visible:ring-ecmp-focus focus-visible:ring-offset-[length:var(--ecmp-focus-ring-offset)]"
              >
                {t("backToSignIn")}
              </Link>
            </p>
          </form>
        </CardBody>
      </Card>
    </AuthLayout>
  );
}
