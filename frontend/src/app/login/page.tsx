"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { ApiError } from "@/lib/api";
import { AuthLayout } from "@/shared/layouts";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Input,
  Loading,
} from "@/shared/ui";

export default function LoginPage() {
  const router = useRouter();
  const { status, login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
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
    setSubmitting(true);
    try {
      await login(username, password);
      router.replace("/dashboard");
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Login failed";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  if (status === "loading" || status === "authenticated") {
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
                Sign in
              </h1>
              <p className="mt-1 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                Use your ECMP username or email.
              </p>
            </div>

            <Input
              name="username"
              label="Username or email"
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />

            <Input
              name="password"
              type="password"
              label="Password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            {error ? (
              <Alert tone="danger" title="Sign in failed" description={error} />
            ) : null}

            <Button type="submit" fullWidth loading={submitting}>
              {submitting ? "Signing in…" : "Sign in"}
            </Button>
          </form>
        </CardBody>
      </Card>
    </AuthLayout>
  );
}
