import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/shared/utils";

export interface FormFieldProps extends Omit<HTMLAttributes<HTMLDivElement>, "children"> {
  /** Control id — used for label `htmlFor` and helper/error ids. */
  id: string;
  label?: string;
  /** Secondary line under the label (before the control). */
  description?: string;
  /** Helper text below the control (alias: `hint`). */
  helper?: string;
  /** @deprecated Prefer `helper` — kept for Input/Select/Textarea API. */
  hint?: string;
  error?: string;
  required?: boolean;
  disabled?: boolean;
  loading?: boolean;
  children: ReactNode;
}

export function formFieldDescribedBy(
  id: string,
  options: {
    description?: string;
    helper?: string;
    hint?: string;
    error?: string;
  },
): string | undefined {
  const helperText = options.helper ?? options.hint;
  const ids = [
    options.error ? `${id}-error` : null,
    !options.error && helperText ? `${id}-hint` : null,
    options.description ? `${id}-desc` : null,
  ].filter(Boolean);
  return ids.length > 0 ? ids.join(" ") : undefined;
}

/**
 * Unified label / description / helper / error chrome for form controls.
 * Presentation only — no validation logic.
 */
export function FormField({
  id,
  label,
  description,
  helper,
  hint,
  error,
  required,
  disabled,
  loading,
  className,
  children,
  ...props
}: FormFieldProps) {
  const helperText = helper ?? hint;
  const hintId = !error && helperText ? `${id}-hint` : undefined;
  const errorId = error ? `${id}-error` : undefined;
  const descId = description ? `${id}-desc` : undefined;

  return (
    <div
      className={cn(
        "flex w-full flex-col gap-[var(--ecmp-space-8)]",
        disabled && "opacity-70",
        className,
      )}
      data-disabled={disabled || undefined}
      data-loading={loading || undefined}
      {...props}
    >
      {label ? (
        <label
          htmlFor={id}
          className="text-[length:var(--ecmp-font-label-size)] font-[number:var(--ecmp-font-label-weight)] leading-[var(--ecmp-font-label-line)] text-ecmp-text-primary"
        >
          {label}
          {required ? (
            <span className="ml-1 text-ecmp-danger" aria-hidden="true">
              *
            </span>
          ) : null}
        </label>
      ) : null}
      {description ? (
        <p
          id={descId}
          className="text-[length:var(--ecmp-font-helper-size)] leading-[var(--ecmp-font-helper-line)] text-ecmp-text-secondary"
        >
          {description}
        </p>
      ) : null}
      <div className="relative min-w-0">{children}</div>
      {error ? (
        <p
          id={errorId}
          role="alert"
          className="text-[length:var(--ecmp-font-helper-size)] leading-[var(--ecmp-font-helper-line)] text-ecmp-danger-text"
        >
          {error}
        </p>
      ) : helperText ? (
        <p
          id={hintId}
          className="text-[length:var(--ecmp-font-helper-size)] leading-[var(--ecmp-font-helper-line)] text-ecmp-text-secondary"
        >
          {helperText}
        </p>
      ) : null}
    </div>
  );
}

/** Shared visual classes for text-like controls (Input / Select / Textarea). */
export function controlSurfaceClass(error?: string) {
  return cn(
    "w-full border bg-ecmp-surface text-ecmp-text-primary",
    "text-[length:var(--ecmp-font-body-size)] leading-[var(--ecmp-font-body-line)]",
    "placeholder:text-ecmp-muted",
    "transition-[border-color,background-color,box-shadow] duration-[var(--ecmp-duration-fast)] ease-[var(--ecmp-ease-hover)]",
    "hover:border-ecmp-secondary",
    "disabled:cursor-not-allowed disabled:bg-ecmp-hover disabled:text-ecmp-disabled disabled:hover:border-ecmp-border",
    error ? "border-ecmp-danger" : "border-ecmp-border",
  );
}
