"use client";

import {
  useEffect,
  useId,
  useRef,
  type HTMLAttributes,
  type ReactNode,
} from "react";
import { createPortal } from "react-dom";
import { useTranslations } from "next-intl";
import { cn } from "@/shared/utils";
import { IconClose } from "@/shared/icons";
import { Button } from "@/shared/ui/button";

export interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  footer?: ReactNode;
  size?: "sm" | "md" | "lg";
}

const sizeClass = {
  sm: "max-w-md",
  md: "max-w-[var(--ecmp-modal-max-width)]",
  lg: "max-w-[var(--ecmp-modal-max-width)]",
} as const;

export function Modal({
  open,
  onClose,
  title,
  children,
  footer,
  size = "md",
}: ModalProps) {
  const t = useTranslations("common");
  const titleId = useId();
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const previous = document.activeElement as HTMLElement | null;
    dialogRef.current?.focus();

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }

    document.addEventListener("keydown", onKeyDown);
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = originalOverflow;
      previous?.focus();
    };
  }, [open, onClose]);

  if (!open || typeof document === "undefined") return null;

  return createPortal(
    <div className="fixed inset-0 z-[var(--ecmp-z-modal)] flex items-end justify-center p-4 sm:items-center">
      <button
        type="button"
        aria-label={t("closeDialogOverlay")}
        className="absolute inset-0 bg-ecmp-overlay backdrop-blur-[3px] transition-opacity duration-[var(--ecmp-duration-fast)] ease-[var(--ecmp-ease-exit)]"
        onClick={onClose}
      />
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        tabIndex={-1}
        className={cn(
          "relative z-10 flex max-h-[90vh] w-full flex-col overflow-hidden",
          "rounded-[var(--ecmp-radius-modal)] border border-ecmp-border/80 bg-ecmp-surface shadow-ecmp-overlay",
          "animate-[ecmp-modal-enter_var(--ecmp-duration-normal)_var(--ecmp-ease-enter)]",
          "motion-reduce:animate-none",
          sizeClass[size],
        )}
      >
        <header className="flex shrink-0 items-center justify-between gap-3 border-b border-ecmp-border/80 px-5 py-4 md:px-6">
          <h2
            id={titleId}
            className="text-[length:var(--ecmp-font-title-size)] font-semibold tracking-tight text-ecmp-text-primary"
          >
            {title}
          </h2>
          <Button
            variant="ghost"
            size="sm"
            aria-label={t("closeDialog")}
            onClick={onClose}
            className="!min-h-[44px] !min-w-[44px] px-0"
          >
            <IconClose />
          </Button>
        </header>
        <div className="min-h-0 flex-1 overflow-y-auto px-5 py-5 md:px-6">
          {children}
        </div>
        {footer ? (
          <footer className="flex shrink-0 flex-col-reverse gap-2 border-t border-ecmp-border/80 px-5 py-4 sm:flex-row sm:justify-end md:px-6">
            {footer}
          </footer>
        ) : null}
      </div>
    </div>,
    document.body,
  );
}

export function ModalSection({
  className,
  children,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("space-y-3", className)} {...props}>
      {children}
    </div>
  );
}
