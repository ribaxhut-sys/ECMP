import {
  forwardRef,
  type InputHTMLAttributes,
  type ReactNode,
} from "react";
import { cn } from "@/shared/utils";
import { FormField, formFieldDescribedBy } from "@/shared/ui/form-field";

export interface RadioOption {
  value: string;
  label: ReactNode;
  disabled?: boolean;
}

export interface RadioGroupProps {
  name: string;
  value?: string;
  defaultValue?: string;
  onChange?: (value: string) => void;
  options: readonly RadioOption[];
  label?: string;
  description?: string;
  hint?: string;
  helper?: string;
  error?: string;
  required?: boolean;
  disabled?: boolean;
  className?: string;
}

/**
 * Presentational radio group. Wiring of value remains with the parent.
 */
export function RadioGroup({
  name,
  value,
  defaultValue,
  onChange,
  options,
  label,
  description,
  hint,
  helper,
  error,
  required,
  disabled,
  className,
}: RadioGroupProps) {
  const groupId = `${name}-group`;
  const labelId = label ? `${groupId}-label` : undefined;
  const describedBy = formFieldDescribedBy(groupId, {
    description,
    helper,
    hint,
    error,
  });

  return (
    <FormField
      id={groupId}
      description={description}
      helper={helper}
      hint={hint}
      error={error}
      required={required}
      disabled={disabled}
      className={className}
    >
      <div
        role="radiogroup"
        aria-labelledby={labelId}
        aria-required={required || undefined}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy}
        className="flex flex-col gap-[var(--ecmp-space-8)]"
      >
        {label ? (
          <p
            id={labelId}
            className="text-[length:var(--ecmp-font-label-size)] font-[number:var(--ecmp-font-label-weight)] text-ecmp-text-primary"
          >
            {label}
            {required ? (
              <span className="ml-1 text-ecmp-danger" aria-hidden="true">
                *
              </span>
            ) : null}
          </p>
        ) : null}
        {options.map((option) => {
          const optionId = `${name}-${option.value}`;
          return (
            <label
              key={option.value}
              htmlFor={optionId}
              className={cn(
                "inline-flex min-h-[var(--ecmp-touch-min)] cursor-pointer items-start gap-3",
                (disabled || option.disabled) && "cursor-not-allowed opacity-70",
              )}
            >
              <input
                id={optionId}
                type="radio"
                name={name}
                value={option.value}
                checked={value !== undefined ? value === option.value : undefined}
                defaultChecked={
                  value === undefined ? defaultValue === option.value : undefined
                }
                disabled={disabled || option.disabled}
                required={required}
                onChange={() => onChange?.(option.value)}
                className={cn(
                  "mt-1 size-4 shrink-0 border-ecmp-border bg-ecmp-surface text-ecmp-primary",
                  "accent-[var(--ecmp-color-primary)]",
                  "transition-[border-color] duration-[var(--ecmp-duration-fast)] ease-[var(--ecmp-ease-hover)]",
                  error && "border-ecmp-danger",
                )}
              />
              <span className="min-w-0 pt-0.5 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                {option.label}
              </span>
            </label>
          );
        })}
      </div>
    </FormField>
  );
}

export interface RadioProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, "type" | "size"> {
  label?: ReactNode;
}

export const Radio = forwardRef<HTMLInputElement, RadioProps>(function Radio(
  { className, id, label, disabled, ...props },
  ref,
) {
  const inputId = id ?? props.name ?? "radio";
  return (
    <label
      htmlFor={inputId}
      className={cn(
        "inline-flex min-h-[var(--ecmp-touch-min)] cursor-pointer items-start gap-3",
        disabled && "cursor-not-allowed opacity-70",
        className,
      )}
    >
      <input
        ref={ref}
        id={inputId}
        type="radio"
        disabled={disabled}
        className={cn(
          "mt-1 size-4 shrink-0 border-ecmp-border bg-ecmp-surface text-ecmp-primary",
          "accent-[var(--ecmp-color-primary)]",
        )}
        {...props}
      />
      {label ? (
        <span className="min-w-0 pt-0.5 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
          {label}
        </span>
      ) : null}
    </label>
  );
});
