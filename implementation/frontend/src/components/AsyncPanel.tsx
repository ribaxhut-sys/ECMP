import type { ReactNode } from 'react'
import { EmptyState } from './EmptyState'
import { ErrorBanner } from './ErrorBanner'
import { LoadingSkeleton } from './LoadingSkeleton'
import styles from './AsyncPanel.module.css'

export interface AsyncPanelProps {
  isLoading: boolean
  isError: boolean
  errorTitle?: string
  errorMessage?: string
  /** @deprecated Prefer errorAction when the label is not always "Retry". */
  onRetry?: () => void
  /** Caller-chosen error action (Back to queue vs Retry, etc.). */
  errorAction?: { label: string; onClick: () => void }
  isEmpty: boolean
  emptyTitle: string
  emptyMessage: string
  emptyAction?: { label: string; onClick: () => void }
  /** Override default panel skeleton (e.g. table skeleton for Case Queue). */
  loadingContent?: ReactNode
  children: ReactNode
}

/**
 * Shared loading / error / empty / content pattern.
 * Timeline / Audit / Notes already use this; Case Detail / Queue retrofit (Sprint-07)
 * keeps dimmed-refetch / validation-recovery workspace-local.
 */
export function AsyncPanel({
  isLoading,
  isError,
  errorTitle = 'Something went wrong',
  errorMessage = 'Something went wrong. Please try again.',
  onRetry,
  errorAction,
  isEmpty,
  emptyTitle,
  emptyMessage,
  emptyAction,
  loadingContent,
  children,
}: AsyncPanelProps) {
  if (isLoading) {
    return (
      <div className={styles.body} aria-busy="true">
        {loadingContent ?? <LoadingSkeleton variant="panel" />}
      </div>
    )
  }

  if (isError) {
    const action =
      errorAction ??
      (onRetry ? { label: 'Retry', onClick: onRetry } : undefined)
    return (
      <div className={styles.body}>
        <ErrorBanner
          title={errorTitle}
          message={errorMessage}
          action={action}
        />
      </div>
    )
  }

  if (isEmpty) {
    return (
      <div className={styles.body}>
        <EmptyState
          title={emptyTitle}
          message={emptyMessage}
          action={emptyAction}
        />
      </div>
    )
  }

  return <div className={styles.body}>{children}</div>
}
