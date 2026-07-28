"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { ApiError, changePassword } from "@/lib/api";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
  PageContainer,
  PageHeader,
} from "@/shared/ui";

const MIN_LENGTH = 8;
const CHANGE_PASSWORD_PATH = "/profile/security/change-password";

export default function ChangePasswordPage() {
  const router = useRouter();
  const { user, logout } = useAuth();
  const t = useTranslations("profile");
  const tAuth = useTranslations("auth");
  const tCommon = useTranslations("common");
  const forced = Boolean(user?.forcePasswordChange);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    // Keep forced users on this page (RequireAuth also enforces).
    if (forced && typeof window !== "undefined") {
      if (window.location.pathname !== CHANGE_PASSWORD_PATH) {
        router.replace(CHANGE_PASSWORD_PATH);
      }
    }
  }, [forced, router]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    if (newPassword.length < MIN_LENGTH) {
      setError(t("newPasswordMin", { min: MIN_LENGTH }));
      return;
    }
    if (newPassword !== confirmPassword) {
      setError(t("newPasswordMismatch"));
      return;
    }
    if (newPassword === currentPassword) {
      setError(t("newPasswordSame"));
      return;
    }

    setSubmitting(true);
    try {
      const result = await changePassword({
        currentPassword,
        newPassword,
        confirmPassword,
      });
      setSuccess(result.message);
      // Refresh tokens are revoked server-side — re-authenticate.
      await logout();
      router.replace("/login");
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : t("unableToChange"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title={t("changePasswordTitle")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title"), href: "/profile" },
          { label: t("securityTitle"), href: "/profile/security" },
          { label: t("changePasswordTitle") },
        ]}
        description={
          forced ? t("changePasswordForced") : t("changePasswordOptional")
        }
      />

      {forced ? (
        <Alert
          tone="warning"
          title={t("passwordChangeRequired")}
          description={t("passwordChangeRequiredDescription")}
        />
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>{t("securityTitle")}</CardTitle>
          <CardDescription>
            {t("chooseStrongPassword", { min: MIN_LENGTH })}
          </CardDescription>
        </CardHeader>
        <CardBody>
          <form onSubmit={onSubmit} className="mx-auto max-w-md space-y-4">
            <Input
              name="currentPassword"
              type="password"
              label={t("currentPassword")}
              autoComplete="current-password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              required
            />
            <Input
              name="newPassword"
              type="password"
              label={tAuth("newPassword")}
              autoComplete="new-password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              minLength={MIN_LENGTH}
              maxLength={72}
            />
            <Input
              name="confirmPassword"
              type="password"
              label={t("confirmNewPassword")}
              autoComplete="new-password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength={MIN_LENGTH}
              maxLength={72}
            />

            {error ? (
              <Alert tone="danger" title={t("changeFailed")} description={error} />
            ) : null}
            {success ? (
              <Alert tone="success" title={tAuth("passwordUpdated")} description={success} />
            ) : null}

            <Button type="submit" loading={submitting}>
              {submitting ? tCommon("saving") : t("changePasswordAction")}
            </Button>
          </form>
        </CardBody>
      </Card>
    </PageContainer>
  );
}
