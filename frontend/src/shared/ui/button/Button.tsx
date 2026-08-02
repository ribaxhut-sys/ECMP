import {
  forwardRef,
  type ButtonHTMLAttributes,
  type ReactNode,
} from "react";
import { cn } from "@/shared/utils";
import { IconSpinner } from "@/shared/icons";

export type ButtonVariant =
  | "primary"
  | "secondary"
  | "outline"
  | "ghost"
  | "danger"
  | "success";
export type ButtonSize = "sm" | "md" | "lg";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  fullWidth?: boolean;
}

const variantClass: Record<ButtonVariant, string> = {
  primary: cn(
    "border border-transparent bg-ecmp-primary text-ecmp-primary-foreground shadow-ecmp-raised",
    "hover:bg-[color-mix(in_srgb,var(--ecmp-color-primary)_88%,black)] hover:shadow-ecmp-hover",
    "active:bg-[color-mix(in_srgb,var(--ecmp-color-primary)_78%,black)] active:shadow-ecmp-surface",
  ),
  secondary: cn(
    "border border-transparent bg-ecmp-secondary text-ecmp-secondary-foreground shadow-ecmp-raised",
    "hover:bg-[color-mix(in_srgb,var(--ecmp-color-secondary)_88%,black)] hover:shadow-ecmp-hover",
    "active:bg-[color-mix(in_srgb,var(--ecmp-color-secondary)_78%,black)] active:shadow-ecmp-surface",
  ),
  outline: cn(
    "border border-ecmp-border bg-ecmp-surface text-ecmp-text-primary shadow-ecmp-surface",
    "hover:border-ecmp-secondary hover:bg-ecmp-hover hover:shadow-ecmp-raised",
    "active:bg-ecmp-pressed",
  ),
  ghost: cn(
    "border border-transparent bg-transparent text-ecmp-text-primary shadow-ecmp-surface",
    "hover:bg-ecmp-hover",
    "active:bg-ecmp-pressed",
  ),
  danger: cn(
    "border border-transparent bg-ecmp-danger text-ecmp-danger-foreground shadow-ecmp-raised",
    "hover:bg-[color-mix(in_srgb,var(--ecmp-color-danger)_88%,black)] hover:shadow-ecmp-hover",
    "active:bg-[color-mix(in_srgb,var(--ecmp-color-danger)_78%,black)] active:shadow-ecmp-surface",
  ),
  success: cn(
    "border border-transparent bg-ecmp-success text-ecmp-success-foreground shadow-ecmp-raised",
    "hover:bg-[color-mix(in_srgb,var(--ecmp-color-success)_88%,black)] hover:shadow-ecmp-hover",
    "active:bg-[color-mix(in_srgb,var(--ecmp-color-success)_78%,black)] active:shadow-ecmp-surface",
  ),
};

const sizeClass: Record<ButtonSize, string> = {
  sm: "min-h-[var(--ecmp-touch-min)] gap-2 px-3 text-[length:var(--ecmp-font-body-small-size)]",
  md: "min-h-[var(--ecmp-touch-min)] gap-2 px-4 text-[length:var(--ecmp-font-body-size)]",
  lg: "min-h-12 gap-2.5 px-6 text-[length:var(--ecmp-font-body-size)]",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  function Button(
    {
      className,
      variant = "primary",
      size = "md",
      loading = false,
      disabled,
      leftIcon,
      rightIcon,
      fullWidth,
      children,
      type = "button",
      ...props
    },
    ref,
  ) {
    return (
      <button
        ref={ref}
        type={type}
        disabled={disabled || loading}
        aria-busy={loading || undefined}
        className={cn(
          "inline-flex items-center justify-center rounded-[var(--ecmp-radius-button)] font-medium",
          "transition-[background-color,border-color,box-shadow,color,transform] duration-[var(--ecmp-duration-fast)] ease-[var(--ecmp-ease-hover)]",
          "active:scale-[0.98]",
          "disabled:pointer-events-none disabled:opacity-50 disabled:shadow-ecmp-surface",
          variantClass[variant],
          sizeClass[size],
          fullWidth && "w-full",
          className,
        )}
        {...props}
      >
        {loading ? (
          <IconSpinner className="size-4" aria-hidden />
        ) : (
          leftIcon
        )}
        {children}
        {!loading ? rightIcon : null}
      </button>
    );
  },
);
