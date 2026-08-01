"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  PASSWORD_MAX_LENGTH,
  PASSWORD_MIN_LENGTH,
} from "@/features/auth";
import { ApiError, resetPassword } from "@/lib/api";
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

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { status } = useAuth();
  const t = useTranslations("auth");
  const tCommon = useTranslations("common");
  const token = useMemo(() => searchParams.get("token")?.trim() ?? "", [searchParams]);

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
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

    if (!token) {
      setError(t("tokenMissing"));
      return;
    }
    if (password.length < PASSWORD_MIN_LENGTH) {
      setError(t("passwordMinLength", { min: PASSWORD_MIN_LENGTH }));
      return;
    }
    if (password !== confirmPassword) {
      setError(t("passwordMismatch"));
      return;
    }

    setSubmitting(true);
    try {
      const result = await resetPassword({
        token,
        password,
        confirmPassword,
      });
      setSuccess(result.message);
      setTimeout(() => router.replace("/login"), 1500);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : t("unableToReset"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (status === "loading" || status === "authenticated") {
    return <Loading label={t("checkingSession")} />;
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div className="mb-1 flex justify-end">
        <LanguageSwitcher variant="compact" />
      </div>
      <div>
        <p className="text-[length:var(--ecmp-font-caption-size)] font-semibold uppercase tracking-[0.2em] text-ecmp-primary">
          {tCommon("appName")}
        </p>
        <h1 className="mt-2 text-[length:var(--ecmp-font-heading-size)] font-semibold tracking-tight text-ecmp-text-primary">
          {t("resetPasswordTitle")}
        </h1>
        <p className="mt-1 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
          {t("resetPasswordSubtitle")}
        </p>
      </div>

      {!token ? (
        <Alert
          tone="danger"
          title={t("invalidLink")}
          description={t("invalidLinkDescription")}
        />
      ) : null}

      <Input
        name="password"
        type="password"
        label={t("newPassword")}
        autoComplete="new-password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        minLength={PASSWORD_MIN_LENGTH}
        maxLength={PASSWORD_MAX_LENGTH}
      />
      <Input
        name="confirmPassword"
        type="password"
        label={t("confirmPassword")}
        autoComplete="new-password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        required
        minLength={PASSWORD_MIN_LENGTH}
        maxLength={PASSWORD_MAX_LENGTH}
      />


      {error ? (
        <Alert tone="danger" title={t("resetFailed")} description={error} />
      ) : null}
      {success ? (
        <Alert tone="success" title={t("passwordUpdated")} description={success} />
      ) : null}

      <Button type="submit" fullWidth loading={submitting} disabled={!token}>
        {submitting ? tCommon("saving") : t("resetPassword")}
      </Button>

      <p className="text-center text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
        <Link href="/login" className="text-ecmp-primary underline-offset-2 hover:underline">
          {t("backToSignIn")}
        </Link>
      </p>
    </form>
  );
}

export default function ResetPasswordPage() {
  const t = useTranslations("auth");
  return (
    <AuthLayout>
      <Card>
        <CardBody>
          <Suspense fallback={<Loading label={t("loading")} />}>
            <ResetPasswordForm />
          </Suspense>
        </CardBody>
      </Card>
    </AuthLayout>
  );
}
