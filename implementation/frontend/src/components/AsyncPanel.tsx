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
  onRetry?: () => void
  isEmpty: boolean
  emptyTitle: string
  emptyMessage: string
  emptyAction?: { label: string; onClick: () => void }
  children: ReactNode
}

/**
 * Shared loading / error / empty / content pattern for new panels (Sprint-06).
 * Do not retrofit shipped Case Detail / Case Queue screens onto this yet.
 */
export function AsyncPanel({
  isLoading,
  isError,
  errorTitle = 'Something went wrong',
  errorMessage = 'Something went wrong. Please try again.',
  onRetry,
  isEmpty,
  emptyTitle,
  emptyMessage,
  emptyAction,
  children,
}: AsyncPanelProps) {
  if (isLoading) {
    return (
      <div className={styles.body} aria-busy="true">
        <LoadingSkeleton variant="panel" />
      </div>
    )
  }

  if (isError) {
    return (
      <div className={styles.body}>
        <ErrorBanner
          title={errorTitle}
          message={errorMessage}
          action={
            onRetry ? { label: 'Retry', onClick: onRetry } : undefined
          }
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
