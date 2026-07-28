"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { PasswordStrengthMeter } from "@/features/auth";
import {
  PASSWORD_MAX_LENGTH,
  PASSWORD_MIN_LENGTH,
  validateNewPassword,
  validatePasswordConfirmation,
} from "@/features/auth/passwordPolicy";
import { ApiError, changePassword } from "@/lib/api";
import { AuthLayout } from "@/shared/layouts";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Input,
  Loading,
} from "@/shared/ui";

export default function ChangePasswordPage() {
  const router = useRouter();
  const { status, user, refreshUser } = useAuth();
  const forced = Boolean(user?.forcePasswordChange);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<{
    currentPassword?: string;
    newPassword?: string;
    confirmPassword?: string;
  }>({});
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (status === "unauthenticated") {
      router.replace("/login");
    }
  }, [status, router]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    const nextErrors: typeof fieldErrors = {};
    if (!currentPassword) {
      nextErrors.currentPassword = "Current password is required";
    }
    const passwordError = validateNewPassword(newPassword);
    if (passwordError) nextErrors.newPassword = passwordError;
    const confirmError = validatePasswordConfirmation(
      newPassword,
      confirmPassword,
    );
    if (confirmError) nextErrors.confirmPassword = confirmError;
    if (currentPassword && newPassword && currentPassword === newPassword) {
      nextErrors.newPassword =
        "New password must be different from the current password";
    }
    setFieldErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    setSubmitting(true);
    try {
      const result = await changePassword({
        currentPassword,
        newPassword,
        confirmPassword,
      });
      setSuccess(result.message || "Password changed successfully.");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      await refreshUser();
      // After forced change, return to the application.
      router.replace("/dashboard");
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Unable to change password",
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (status === "loading" || status === "unauthenticated") {
    return (
      <AuthLayout>
        <Loading label="Checking session…" />
      </AuthLayout>
    );
  }

  return (
    <AuthLayout>
      <Card>
        <CardBody>
          <form onSubmit={onSubmit} className="space-y-4">
            <div>
              <p className="text-[length:var(--ecmp-font-caption-size)] font-semibold uppercase tracking-[0.2em] text-ecmp-primary">
                ECMP
              </p>
              <h1 className="mt-2 text-[length:var(--ecmp-font-heading-size)] font-semibold tracking-tight text-ecmp-text-primary">
                Change password
              </h1>
              <p className="mt-1 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                {forced
                  ? "Your administrator reset your password. You must set a new one before continuing."
                  : "Update your password. You will stay signed in after a successful change."}
              </p>
            </div>

            {forced ? (
              <Alert
                tone="warning"
                title="Password change required"
                description="Access to the rest of the application is blocked until you change your password."
              />
            ) : null}

            <Input
              name="currentPassword"
              type="password"
              label="Current password"
              autoComplete="current-password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              error={fieldErrors.currentPassword}
              required
              maxLength={PASSWORD_MAX_LENGTH}
            />

            <Input
              name="newPassword"
              type="password"
              label="New password"
              autoComplete="new-password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              error={fieldErrors.newPassword}
              hint={`At least ${PASSWORD_MIN_LENGTH} characters (max ${PASSWORD_MAX_LENGTH}).`}
              required
              maxLength={PASSWORD_MAX_LENGTH}
            />
            <PasswordStrengthMeter password={newPassword} />

            <Input
              name="confirmPassword"
              type="password"
              label="Confirm password"
              autoComplete="new-password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              error={fieldErrors.confirmPassword}
              required
              maxLength={PASSWORD_MAX_LENGTH}
            />

            {error ? (
              <Alert tone="danger" title="Unable to change password" description={error} />
            ) : null}

            {success ? (
              <Alert tone="success" title="Password updated" description={success} />
            ) : null}

            <Button type="submit" fullWidth loading={submitting}>
              {submitting ? "Saving…" : "Update password"}
            </Button>

            {!forced ? (
              <p className="text-center text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                <Link
                  href="/dashboard"
                  className="font-medium text-ecmp-primary underline-offset-2 hover:underline"
                >
                  Back to dashboard
                </Link>
              </p>
            ) : null}
          </form>
        </CardBody>
      </Card>
    </AuthLayout>
  );
}
