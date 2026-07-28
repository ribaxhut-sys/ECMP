"use client";

import { FormEvent, Suspense, useMemo, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { PasswordStrengthMeter } from "@/features/auth";
import {
  PASSWORD_MAX_LENGTH,
  PASSWORD_MIN_LENGTH,
  resetTokenErrorMessage,
  validateNewPassword,
  validatePasswordConfirmation,
} from "@/features/auth/passwordPolicy";
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

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const token = useMemo(
    () => (searchParams.get("token") ?? "").trim(),
    [searchParams],
  );

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<{
    password?: string;
    confirmPassword?: string;
  }>({});
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const tokenMissing = !token;

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    const nextErrors: typeof fieldErrors = {};
    const passwordError = validateNewPassword(password);
    if (passwordError) nextErrors.password = passwordError;
    const confirmError = validatePasswordConfirmation(password, confirmPassword);
    if (confirmError) nextErrors.confirmPassword = confirmError;
    setFieldErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0 || tokenMissing) {
      if (tokenMissing) {
        setError("This reset link is invalid. Request a new one.");
      }
      return;
    }

    setSubmitting(true);
    try {
      const result = await resetPassword({
        token,
        password,
        confirmPassword,
      });
      setSuccess(result.message || "Password has been reset successfully.");
      setPassword("");
      setConfirmPassword("");
    } catch (err) {
      if (err instanceof ApiError) {
        const reason = err.details?.reason;
        setError(
          resetTokenErrorMessage(
            reason,
            err.message || "Invalid or expired reset token",
          ),
        );
      } else {
        setError(err instanceof Error ? err.message : "Reset failed");
      }
    } finally {
      setSubmitting(false);
    }
  }

  if (success) {
    return (
      <Card>
        <CardBody className="space-y-4">
          <Alert tone="success" title="Password reset" description={success} />
          <Link
            href="/login"
            className="inline-flex w-full items-center justify-center rounded-[var(--ecmp-radius-md)] bg-ecmp-primary px-4 py-3 text-center text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-primary-foreground"
          >
            Continue to sign in
          </Link>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardBody>
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <p className="text-[length:var(--ecmp-font-caption-size)] font-semibold uppercase tracking-[0.2em] text-ecmp-primary">
              ECMP
            </p>
            <h1 className="mt-2 text-[length:var(--ecmp-font-heading-size)] font-semibold tracking-tight text-ecmp-text-primary">
              Reset password
            </h1>
            <p className="mt-1 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              Choose a new password for your account.
            </p>
          </div>

          {tokenMissing ? (
            <Alert
              tone="danger"
              title="Invalid reset link"
              description="This reset link is missing or invalid. Request a new one from the forgot password page."
              actionLabel="Forgot password"
              onAction={() => {
                window.location.href = "/forgot-password";
              }}
            />
          ) : null}

          <Input
            name="password"
            type="password"
            label="New password"
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            error={fieldErrors.password}
            hint={`At least ${PASSWORD_MIN_LENGTH} characters (max ${PASSWORD_MAX_LENGTH}).`}
            required
            disabled={tokenMissing}
            maxLength={PASSWORD_MAX_LENGTH}
          />
          <PasswordStrengthMeter password={password} />

          <Input
            name="confirmPassword"
            type="password"
            label="Confirm password"
            autoComplete="new-password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            error={fieldErrors.confirmPassword}
            required
            disabled={tokenMissing}
            maxLength={PASSWORD_MAX_LENGTH}
          />

          {error ? (
            <Alert
              tone="danger"
              title="Unable to reset password"
              description={error}
              actionLabel="Request a new link"
              onAction={() => {
                window.location.href = "/forgot-password";
              }}
            />
          ) : null}

          <Button type="submit" fullWidth loading={submitting} disabled={tokenMissing}>
            {submitting ? "Saving…" : "Reset password"}
          </Button>

          <p className="text-center text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
            <Link
              href="/login"
              className="font-medium text-ecmp-primary underline-offset-2 hover:underline"
            >
              Back to sign in
            </Link>
          </p>
        </form>
      </CardBody>
    </Card>
  );
}

export default function ResetPasswordPage() {
  return (
    <AuthLayout>
      <Suspense fallback={<Loading label="Loading reset form…" />}>
        <ResetPasswordForm />
      </Suspense>
    </AuthLayout>
  );
}
