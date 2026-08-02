import { forwardRef, type TextareaHTMLAttributes } from "react";
import { cn } from "@/shared/utils";
import {
  FormField,
  controlSurfaceClass,
  formFieldDescribedBy,
} from "@/shared/ui/form-field";

export interface TextareaProps
  extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  description?: string;
  hint?: string;
  helper?: string;
  error?: string;
  loading?: boolean;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  function Textarea(
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
      rows = 4,
      ...props
    },
    ref,
  ) {
    const inputId = id ?? props.name ?? "textarea";
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
        <textarea
          ref={ref}
          id={inputId}
          rows={rows}
          required={required}
          disabled={disabled || loading}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
          aria-busy={loading || undefined}
          className={cn(
            "min-h-[88px] rounded-[var(--ecmp-radius-textarea)] px-3 py-3",
            controlSurfaceClass(error),
            className,
          )}
          {...props}
        />
      </FormField>
    );
  },
);
