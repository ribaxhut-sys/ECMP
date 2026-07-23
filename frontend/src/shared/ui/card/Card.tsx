import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/shared/utils";

export interface CardProps extends HTMLAttributes<HTMLElement> {
  children: ReactNode;
  padding?: boolean;
}

export function Card({
  className,
  children,
  padding = true,
  ...props
}: CardProps) {
  return (
    <section
      className={cn(
        "rounded-[var(--ecmp-radius-lg)] border border-ecmp-border bg-ecmp-surface shadow-ecmp-sm",
        padding && "p-4 md:p-6",
        className,
      )}
      {...props}
    >
      {children}
    </section>
  );
}

export function CardHeader({
  className,
  children,
  action,
  ...props
}: HTMLAttributes<HTMLDivElement> & { action?: ReactNode }) {
  return (
    <div
      className={cn(
        "mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between",
        className,
      )}
      {...props}
    >
      <div className="min-w-0">{children}</div>
      {action ? <div className="shrink-0">{action}</div> : null}
    </div>
  );
}

export function CardTitle({
  className,
  children,
  ...props
}: HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h2
      className={cn(
        "text-[length:var(--ecmp-font-title-size)] font-[number:var(--ecmp-font-title-weight)] text-ecmp-text-primary",
        className,
      )}
      {...props}
    >
      {children}
    </h2>
  );
}

export function CardDescription({
  className,
  children,
  ...props
}: HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p
      className={cn(
        "mt-1 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary",
        className,
      )}
      {...props}
    >
      {children}
    </p>
  );
}

export function CardBody({
  className,
  children,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("min-w-0", className)} {...props}>
      {children}
    </div>
  );
}
