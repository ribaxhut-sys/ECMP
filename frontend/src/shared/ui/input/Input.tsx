import { forwardRef, type InputHTMLAttributes } from "react";
import { cn } from "@/shared/utils";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  hint?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { className, id, label, hint, error, required, ...props },
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
      <input
        ref={ref}
        id={inputId}
        required={required}
        aria-invalid={error ? true : undefined}
        aria-describedby={
          [errorId, hintId].filter(Boolean).join(" ") || undefined
        }
        className={cn(
          "ecmp-touch w-full rounded-[var(--ecmp-radius-md)] border bg-ecmp-surface px-3 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary",
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
});
