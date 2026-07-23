"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { ApiError } from "@/lib/api";

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
      <main className="flex min-h-screen items-center justify-center px-4">
        <p className="text-sm text-[var(--muted)]">Checking session…</p>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <form
        onSubmit={onSubmit}
        className="w-full max-w-sm space-y-4 rounded-xl border border-white/10 bg-black/20 p-6"
      >
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-[var(--accent)]">
            ECMP
          </p>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight">Sign in</h1>
          <p className="mt-1 text-sm text-[var(--muted)]">
            Use your ECMP username or email.
          </p>
        </div>

        <label className="block space-y-1.5 text-sm">
          <span className="text-[var(--muted)]">Username or email</span>
          <input
            name="username"
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            className="w-full rounded-lg border border-white/15 bg-black/30 px-3 py-2 outline-none focus:border-[var(--accent)]"
          />
        </label>

        <label className="block space-y-1.5 text-sm">
          <span className="text-[var(--muted)]">Password</span>
          <input
            name="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full rounded-lg border border-white/15 bg-black/30 px-3 py-2 outline-none focus:border-[var(--accent)]"
          />
        </label>

        {error ? (
          <p className="text-sm text-red-300" role="alert">
            {error}
          </p>
        ) : null}

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-lg border border-white/15 bg-white/10 px-4 py-2 text-sm font-medium transition hover:bg-white/15 disabled:opacity-50"
        >
          {submitting ? "Signing in…" : "Sign in"}
        </button>
      </form>
    </main>
  );
}
