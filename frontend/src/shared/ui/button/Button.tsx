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
  | "danger";
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
  primary:
    "bg-ecmp-primary text-ecmp-primary-foreground hover:opacity-90 border border-transparent",
  secondary:
    "bg-ecmp-secondary text-ecmp-secondary-foreground hover:opacity-90 border border-transparent",
  outline:
    "bg-ecmp-surface text-ecmp-text-primary border border-ecmp-border hover:bg-ecmp-secondary-muted",
  ghost:
    "bg-transparent text-ecmp-text-primary border border-transparent hover:bg-ecmp-secondary-muted",
  danger:
    "bg-ecmp-danger text-ecmp-danger-foreground hover:opacity-90 border border-transparent",
};

const sizeClass: Record<ButtonSize, string> = {
  sm: "min-h-[44px] px-3 text-[length:var(--ecmp-font-caption-size)] gap-2",
  md: "min-h-[44px] px-4 text-[length:var(--ecmp-font-body-size)] gap-2",
  lg: "min-h-[48px] px-6 text-[length:var(--ecmp-font-body-size)] gap-2",
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
          "inline-flex items-center justify-center rounded-[var(--ecmp-radius-md)] font-medium transition-opacity",
          "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus",
          "disabled:pointer-events-none disabled:opacity-50",
          variantClass[variant],
          sizeClass[size],
          fullWidth && "w-full",
          className,
        )}
        {...props}
      >
        {loading ? <IconSpinner className="size-4" /> : leftIcon}
        {children}
        {!loading ? rightIcon : null}
      </button>
    );
  },
);
