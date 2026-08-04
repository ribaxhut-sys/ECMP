"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { ApiError, forgotPassword } from "@/lib/api";
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

export default function ForgotPasswordPage() {
  const router = useRouter();
  const { status } = useAuth();
  const { pushSuccess } = useToast();
  const t = useTranslations("auth");
  const tCommon = useTranslations("common");
  const [email, setEmail] = useState("");
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
    const trimmed = email.trim();
    if (!trimmed || !trimmed.includes("@")) {
      setError(t("enterValidEmail"));
      return;
    }
    setSubmitting(true);
    try {
      const result = await forgotPassword(trimmed);
      pushSuccess(t("checkYourEmail"), result.message);
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
      <AuthLayout toolbar={<LanguageSwitcher variant="compact" />}>
        <Card className="shadow-ecmp-raised">
          <CardBody className="space-y-[var(--ecmp-panel-gap)] p-[var(--ecmp-panel-gap)]">
            <Skeleton rows={3} />
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
              title={t("forgotPasswordTitle")}
              subtitle={t("forgotPasswordSubtitle")}
            />

            <Input
              name="email"
              type="email"
              label={t("email")}
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              helper={t("forgotPasswordHelper")}
            />

            {error ? (
              <Alert tone="danger" title={t("requestFailed")} description={error} />
            ) : null}

            <Button
              type="submit"
              fullWidth
              loading={submitting}
              className="min-h-[var(--ecmp-touch-min)]"
            >
              {submitting ? tCommon("sending") : t("sendResetLink")}
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
        </CardBody>
      </Card>
    </AuthLayout>
  );
}
