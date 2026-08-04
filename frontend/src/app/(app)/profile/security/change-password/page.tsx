"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  PASSWORD_CHANGE_ROUTE,
  PASSWORD_MAX_LENGTH,
  PASSWORD_MIN_LENGTH,
  PasswordRequirements,
} from "@/features/auth";
import { ApiError, changePassword } from "@/lib/api";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Input,
  PageContainer,
  PageHeader,
  SectionHeader,
} from "@/shared/ui";
import { useToast } from "@/shared/providers";

export default function ChangePasswordPage() {
  const router = useRouter();
  const { user, logout } = useAuth();
  const { pushSuccess } = useToast();
  const t = useTranslations("profile");
  const tAuth = useTranslations("auth");
  const tCommon = useTranslations("common");
  const forced = Boolean(user?.forcePasswordChange);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    // Keep forced users on this page (RequireAuth also enforces).
    if (forced && typeof window !== "undefined") {
      if (window.location.pathname !== PASSWORD_CHANGE_ROUTE) {
        router.replace(PASSWORD_CHANGE_ROUTE);
      }
    }
  }, [forced, router]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (newPassword.length < PASSWORD_MIN_LENGTH) {
      setError(t("newPasswordMin", { min: PASSWORD_MIN_LENGTH }));
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
      pushSuccess(tAuth("passwordUpdated"), result.message);
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
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        overline={t("overline")}
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

      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader
          title={t("passwordFormTitle")}
          description={t("chooseStrongPassword", { min: PASSWORD_MIN_LENGTH })}
        />
        <Card className="shadow-ecmp-raised">
          <CardBody>
            <form
              onSubmit={onSubmit}
              className="mx-auto w-full max-w-[var(--ecmp-form-max-width)] space-y-[var(--ecmp-form-gap)]"
            >
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
                minLength={PASSWORD_MIN_LENGTH}
                maxLength={PASSWORD_MAX_LENGTH}
              />
              <Input
                name="confirmPassword"
                type="password"
                label={t("confirmNewPassword")}
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={PASSWORD_MIN_LENGTH}
                maxLength={PASSWORD_MAX_LENGTH}
              />

              <PasswordRequirements password={newPassword} />

              {error ? (
                <Alert tone="danger" title={t("changeFailed")} description={error} />
              ) : null}

              <Button
                type="submit"
                loading={submitting}
                className="min-h-[var(--ecmp-touch-min)]"
              >
                {submitting ? tCommon("saving") : t("changePasswordAction")}
              </Button>
            </form>
          </CardBody>
        </Card>
      </section>
    </PageContainer>
  );
}
