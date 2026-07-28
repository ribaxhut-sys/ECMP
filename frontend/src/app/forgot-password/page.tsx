"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { ApiError, forgotPassword } from "@/lib/api";
import { AuthLayout } from "@/shared/layouts";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Input,
} from "@/shared/ui";

const GENERIC_SUCCESS =
  "If the account exists, a reset link has been sent.";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSuccess(null);
    setSubmitting(true);
    try {
      const result = await forgotPassword(email.trim());
      setSuccess(result.message || GENERIC_SUCCESS);
    } catch (err) {
      // Still show opaque success for network/server ambiguity when possible;
      // only surface validation/format errors that do not enumerate accounts.
      if (err instanceof ApiError && err.status === 400) {
        setError(err.message);
      } else {
        setSuccess(GENERIC_SUCCESS);
      }
    } finally {
      setSubmitting(false);
    }
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
                Forgot password
              </h1>
              <p className="mt-1 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                Enter your email and we will send a reset link if an account
                exists.
              </p>
            </div>

            <Input
              name="email"
              type="email"
              label="Email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            {error ? (
              <Alert tone="danger" title="Unable to submit" description={error} />
            ) : null}

            {success ? (
              <Alert tone="success" title="Request received" description={success} />
            ) : null}

            <Button type="submit" fullWidth loading={submitting}>
              {submitting ? "Sending…" : "Send reset link"}
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
    </AuthLayout>
  );
}
