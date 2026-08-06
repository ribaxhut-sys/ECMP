import { forwardRef, type SelectHTMLAttributes } from "react";
import { cn } from "@/shared/utils";
import { IconChevronDown } from "@/shared/icons";
import {
  FormField,
  controlSurfaceClass,
  formFieldDescribedBy,
} from "@/shared/ui/form-field";

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  description?: string;
  hint?: string;
  helper?: string;
  error?: string;
  loading?: boolean;
  options: readonly SelectOption[];
  placeholder?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  function Select(
    {
      className,
      id,
      label,
      description,
      hint,
      helper,
      error,
      required,
      disabled,
      loading,
      options,
      placeholder,
      ...props
    },
    ref,
  ) {
    const inputId = id ?? props.name ?? "select";
    const describedBy = formFieldDescribedBy(inputId, {
      description,
      helper,
      hint,
      error,
    });

    return (
      <FormField
        id={inputId}
        label={label}
        description={description}
        helper={helper}
        hint={hint}
        error={error}
        required={required}
        disabled={disabled}
        loading={loading}
      >
        <div className="relative">
          <select
            ref={ref}
            id={inputId}
            required={required}
            disabled={disabled || loading}
            aria-invalid={error ? true : undefined}
            aria-describedby={describedBy}
            aria-busy={loading || undefined}
            className={cn(
              "ecmp-touch appearance-none rounded-[var(--ecmp-radius-select)] py-0 pl-3 pr-10",
              controlSurfaceClass(error),
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
          <IconChevronDown
            className="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2 text-ecmp-text-secondary"
            aria-hidden
          />
        </div>
      </FormField>
    );
  },
);
