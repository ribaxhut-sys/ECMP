import { forwardRef, type SelectHTMLAttributes } from "react";
import { cn } from "@/shared/utils";

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  hint?: string;
  error?: string;
  options: readonly SelectOption[];
  placeholder?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  function Select(
    {
      className,
      id,
      label,
      hint,
      error,
      required,
      options,
      placeholder,
      ...props
    },
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
        <select
          ref={ref}
          id={inputId}
          required={required}
          aria-invalid={error ? true : undefined}
          aria-describedby={
            [errorId, hintId].filter(Boolean).join(" ") || undefined
          }
          className={cn(
            "ecmp-touch w-full appearance-none rounded-[var(--ecmp-radius-md)] border bg-ecmp-surface px-3 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary",
            "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus",
            error ? "border-ecmp-danger" : "border-ecmp-border",
            className,
          )}
          {...props}
        >
          {placeholder ? (
            <option value="" disabled>
              {placeholder}
            </option>
          ) : null}
          {options.map((option) => (
            <option
              key={option.value}
              value={option.value}
              disabled={option.disabled}
            >
              {option.label}
            </option>
          ))}
        </select>
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
