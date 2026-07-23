export function Panel({
  title,
  children,
  action,
}: {
  title: string;
  children: React.ReactNode;
  action?: React.ReactNode;
}) {
  return (
    <section className="rounded-xl border border-white/10 bg-white/[0.04] p-5 shadow-[0_8px_30px_rgba(0,0,0,0.18)] backdrop-blur-sm">
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--muted)]">
          {title}
        </h2>
        {action}
      </div>
      {children}
    </section>
  );
}

export function LoadingBlock({ rows = 3 }: { rows?: number }) {
  return (
    <div className="space-y-3" aria-busy="true" aria-label="Loading">
      {Array.from({ length: rows }).map((_, index) => (
        <div
          key={index}
          className="h-10 animate-pulse rounded-lg bg-white/10"
        />
      ))}
    </div>
  );
}

export function EmptyBlock({ message }: { message: string }) {
  return (
    <p className="rounded-lg border border-dashed border-white/15 px-4 py-8 text-center text-sm text-[var(--muted)]">
      {message}
    </p>
  );
}

export function ErrorBanner({
  message,
  code,
  onRetry,
}: {
  message: string;
  code?: string;
  onRetry?: () => void;
}) {
  return (
    <div
      role="alert"
      className="rounded-xl border border-rose-400/40 bg-rose-500/10 px-5 py-4 text-rose-100"
    >
      <p className="font-medium">Unable to load dashboard</p>
      <p className="mt-1 text-sm opacity-90">
        {message}
        {code ? ` (${code})` : ""}
      </p>
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="mt-3 rounded-lg bg-white/10 px-3 py-1.5 text-sm font-medium transition hover:bg-white/20"
        >
          Retry
        </button>
      ) : null}
    </div>
  );
}

export function StatusBadge({ status }: { status: string }) {
  return (
    <span className="inline-flex rounded-md bg-white/10 px-2 py-0.5 text-xs font-medium tracking-wide text-[var(--ink)]">
      {status.replaceAll("_", " ")}
    </span>
  );
}

export function PriorityBadge({ priority }: { priority: string }) {
  const tone =
    priority === "CRITICAL"
      ? "bg-rose-500/20 text-rose-100"
      : priority === "HIGH"
        ? "bg-amber-500/20 text-amber-100"
        : priority === "MEDIUM"
          ? "bg-sky-500/20 text-sky-100"
          : "bg-white/10 text-[var(--muted)]";
  return (
    <span className={`inline-flex rounded-md px-2 py-0.5 text-xs font-medium ${tone}`}>
      {priority}
    </span>
  );
}
