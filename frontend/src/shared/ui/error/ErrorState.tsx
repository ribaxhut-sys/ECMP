import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/shared/utils";
import { Alert } from "@/shared/ui/alert";

export interface ErrorStateProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  message: string;
  code?: string;
  actionLabel?: string;
  onRetry?: () => void;
  children?: ReactNode;
}

export function ErrorState({
  className,
  title = "Something went wrong",
  message,
  code,
  actionLabel = "Retry",
  onRetry,
  children,
  ...props
}: ErrorStateProps) {
  return (
    <div className={cn("w-full", className)} {...props}>
      <Alert
        tone="danger"
        title={title}
        description={
          <>
            <p>
              {message}
              {code ? ` (${code})` : ""}
            </p>
            {children}
          </>
        }
        actionLabel={onRetry ? actionLabel : undefined}
        onAction={onRetry}
      />
    </div>
  );
}
