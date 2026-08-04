"use client";

import { FormEvent, useEffect, useMemo, useState, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  PASSWORD_MAX_LENGTH,
  PASSWORD_MIN_LENGTH,
  PasswordRequirements,
} from "@/features/auth";
import { ApiError, resetPassword } from "@/lib/api";
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
import { useToast } from "@/shared/providers";

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { status } = useAuth();
  const { pushSuccess } = useToast();
  const t = useTranslations("auth");
  const tCommon = useTranslations("common");
  const token = useMemo(
    () => searchParams.get("token")?.trim() ?? "",
    [searchParams],
  );

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (status === "authenticated") {
      router.replace("/dashboard");
    }
  }, [status, router]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

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
      pushSuccess(t("passwordUpdated"), result.message);
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
    return <Skeleton rows={4} />;
  }

  return (
    <form onSubmit={onSubmit} className="space-y-[var(--ecmp-form-gap)]">
      <IdentityBrand
        title={t("resetPasswordTitle")}
        subtitle={t("resetPasswordSubtitle")}
      />

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

      <PasswordRequirements password={password} />

      {error ? (
        <Alert tone="danger" title={t("resetFailed")} description={error} />
      ) : null}

      <Button
        type="submit"
        fullWidth
        loading={submitting}
        disabled={!token}
        className="min-h-[var(--ecmp-touch-min)]"
      >
        {submitting ? tCommon("saving") : t("resetPassword")}
      </Button>

      <p className="text-center text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
        <Link
          href="/login"
          className="min-h-[var(--ecmp-touch-min)] inline-flex items-center text-ecmp-primary underline-offset-2 transition-colors duration-[var(--ecmp-duration-normal)] ease-[var(--ecmp-ease-hover)] hover:underline focus-visible:outline-none focus-visible:ring-[length:var(--ecmp-focus-ring-width)] focus-visible:ring-ecmp-focus focus-visible:ring-offset-[length:var(--ecmp-focus-ring-offset)]"
        >
          {t("backToSignIn")}
        </Link>
      </p>
    </form>
  );
}

export default function ResetPasswordPage() {
  const t = useTranslations("auth");
  return (
    <AuthLayout toolbar={<LanguageSwitcher variant="compact" />}>
      <Card className="shadow-ecmp-raised">
        <CardBody className="p-[var(--ecmp-panel-gap)] md:p-[var(--ecmp-section-gap)]">
          <Suspense fallback={<Skeleton rows={4} aria-label={t("loading")} />}>
            <ResetPasswordForm />
          </Suspense>
        </CardBody>
      </Card>
    </AuthLayout>
  );
}
