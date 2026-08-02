import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/shared/utils";

export interface CardProps extends HTMLAttributes<HTMLElement> {
  children: ReactNode;
  padding?: boolean;
  /** Adds hover elevation for clickable/navigable cards. */
  interactive?: boolean;
}

export function Card({
  className,
  children,
  padding = true,
  interactive = false,
  ...props
}: CardProps) {
  return (
    <section
      className={cn(
        "rounded-[var(--ecmp-radius-card)] border border-ecmp-border bg-ecmp-surface shadow-ecmp-raised",
        "transition-[box-shadow,border-color,transform] duration-[var(--ecmp-duration-normal)] ease-[var(--ecmp-ease-hover)]",
        interactive &&
          "cursor-pointer hover:border-ecmp-secondary hover:shadow-ecmp-hover",
        padding && "p-4 md:p-6",
        className,
      )}
      data-interactive={interactive || undefined}
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
        "mb-[var(--ecmp-card-gap)] flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between",
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
        "text-[length:var(--ecmp-font-card-title-size)] font-[number:var(--ecmp-font-card-title-weight)] leading-[var(--ecmp-font-card-title-line)] text-ecmp-text-primary",
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
        "mt-1 text-[length:var(--ecmp-font-body-small-size)] leading-[var(--ecmp-font-body-small-line)] text-ecmp-text-secondary",
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

export function CardFooter({
  className,
  children,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "mt-[var(--ecmp-card-gap)] flex flex-wrap items-center gap-2 border-t border-ecmp-border pt-[var(--ecmp-card-gap)]",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
