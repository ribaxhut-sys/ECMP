import { forwardRef, type InputHTMLAttributes, type ReactNode } from "react";
import { cn } from "@/shared/utils";
import { FormField, formFieldDescribedBy } from "@/shared/ui/form-field";

export interface CheckboxProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, "type" | "size"> {
  label?: string;
  description?: string;
  hint?: string;
  helper?: string;
  error?: string;
  /** Optional rich label content (overrides `label` text when both set for visual). */
  labelContent?: ReactNode;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  function Checkbox(
    {
      className,
      id,
      label,
      labelContent,
      description,
      hint,
      helper,
      error,
      required,
      disabled,
      ...props
    },
    ref,
  ) {
    const inputId = id ?? props.name ?? "checkbox";
    const describedBy = formFieldDescribedBy(inputId, {
      description,
      helper,
      hint,
      error,
    });
    const showFieldChrome = Boolean(description || helper || hint || error);

    const control = (
      <label
        htmlFor={inputId}
        className={cn(
          "inline-flex min-h-[var(--ecmp-touch-min)] cursor-pointer items-start gap-3",
          disabled && "cursor-not-allowed opacity-70",
          !showFieldChrome && className,
        )}
      >
        <input
          ref={ref}
          id={inputId}
          type="checkbox"
          required={required}
          disabled={disabled}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
          className={cn(
            "mt-1 size-4 shrink-0 rounded-[var(--ecmp-radius-sm)] border border-ecmp-border bg-ecmp-surface text-ecmp-primary",
            "accent-[var(--ecmp-color-primary)]",
            "transition-[border-color,box-shadow] duration-[var(--ecmp-duration-fast)] ease-[var(--ecmp-ease-hover)]",
            error && "border-ecmp-danger",
          )}
          {...props}
        />
        <span className="min-w-0 pt-0.5 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
          {labelContent ?? label}
          {required ? (
            <span className="ml-1 text-ecmp-danger" aria-hidden="true">
              *
            </span>
          ) : null}
        </span>
      </label>
    );

    if (!showFieldChrome) {
      return control;
    }

    return (
      <FormField
        id={inputId}
        description={description}
        helper={helper}
        hint={hint}
        error={error}
        required={required}
        disabled={disabled}
        className={className}
      >
        {control}
      </FormField>
    );
  },
);
