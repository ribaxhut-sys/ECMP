import { forwardRef, type TextareaHTMLAttributes } from "react";
import { cn } from "@/shared/utils";

export interface TextareaProps
  extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  hint?: string;
  error?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  function Textarea(
    { className, id, label, hint, error, required, rows = 4, ...props },
    ref,
  ) {
    const inputId = id ?? props.name;
    const hintId = hint ? `${inputId}-hint` : undefined;
    const errorId = error ? `${inputId}-error` : undefined;

    return (
      <div className="flex w-full flex-col gap-2">
        {label ? (
          <label
            htmlFor={inputId}
            className="text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary"
          >
            {label}
            {required ? (
              <span className="ml-1 text-ecmp-danger" aria-hidden="true">
                *
              </span>
            ) : null}
          </label>
        ) : null}
        <textarea
          ref={ref}
          id={inputId}
          rows={rows}
          required={required}
          aria-invalid={error ? true : undefined}
          aria-describedby={
            [errorId, hintId].filter(Boolean).join(" ") || undefined
          }
          className={cn(
            "min-h-[88px] w-full rounded-[var(--ecmp-radius-md)] border bg-ecmp-surface px-3 py-3 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary",
            "placeholder:text-ecmp-text-secondary",
            "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus",
            error ? "border-ecmp-danger" : "border-ecmp-border",
            className,
          )}
          {...props}
        />
        {error ? (
          <p id={errorId} role="alert" className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-danger">
            {error}
          </p>
        ) : hint ? (
          <p id={hintId} className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
            {hint}
          </p>
        ) : null}
      </div>
    );
  },
);
