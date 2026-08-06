import { forwardRef, type InputHTMLAttributes } from "react";
import { cn } from "@/shared/utils";
import {
  FormField,
  controlSurfaceClass,
  formFieldDescribedBy,
} from "@/shared/ui/form-field";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  description?: string;
  hint?: string;
  helper?: string;
  error?: string;
  loading?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
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
    ...props
  },
  ref,
) {
  const inputId = id ?? props.name ?? "input";
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
      <input
        ref={ref}
        id={inputId}
        required={required}
        disabled={disabled || loading}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy}
        aria-busy={loading || undefined}
        className={cn(
          "ecmp-touch rounded-[var(--ecmp-radius-input)] px-3",
          controlSurfaceClass(error),
          className,
        )}
        {...props}
      />
    </FormField>
  );
});
