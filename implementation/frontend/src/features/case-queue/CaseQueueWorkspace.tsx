import { useCallback, useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { ApiError, isApiError } from '../../api/errors'
import { useAuth } from '../../auth/AuthContext'
import { EmptyState } from '../../components/EmptyState'
import { ErrorBanner } from '../../components/ErrorBanner'
import { LoadingSkeleton } from '../../components/LoadingSkeleton'
import { CaseQueueTable } from './components/CaseQueueTable'
import { PaginationControls } from './components/PaginationControls'
import { QueueFilterBar } from './components/QueueFilterBar'
import {
  defaultQueueFilters,
  filtersToSearchParams,
  hasActiveFilters,
  parseQueueFilters,
  type CaseQueueFilters,
} from './filters'
import { useCaseQueue } from './hooks/useCaseQueue'
import styles from './CaseQueueWorkspace.module.css'

export function CaseQueueWorkspace() {
  const { onUnauthenticated } = useAuth()
  const [searchParams, setSearchParams] = useSearchParams()
  const [validationHint, setValidationHint] = useState<string | null>(null)

  const filters = useMemo(
    () => parseQueueFilters(searchParams),
    [searchParams],
  )

  const query = useCaseQueue(filters)

  const writeFilters = useCallback(
    (next: CaseQueueFilters, options?: { replace?: boolean }) => {
      setSearchParams(filtersToSearchParams(next), {
        replace: options?.replace ?? false,
      })
    },
    [setSearchParams],
  )

  const patchFilters = useCallback(
    (patch: Partial<CaseQueueFilters>) => {
      const resettingPage =
        'status' in patch ||
        'priority' in patch ||
        'caseType' in patch ||
        'assigneeId' in patch
      writeFilters({
        ...filters,
        ...patch,
        ...(resettingPage && !('page' in patch) ? { page: 1 } : {}),
      })
    },
    [filters, writeFilters],
  )

  const clearFilters = useCallback(() => {
    writeFilters({
      page: 1,
      pageSize: filters.pageSize,
    })
  }, [filters.pageSize, writeFilters])

  useEffect(() => {
    if (!query.isError || !isApiError(query.error)) return
    if (query.error.code !== 'VALIDATION_ERROR') return
    setValidationHint(
      query.error.message ||
        'Invalid pagination parameters were reset to defaults.',
    )
    writeFilters(defaultQueueFilters(), { replace: true })
  }, [query.isError, query.error, writeFilters])

  if (query.isError) {
    const error = isApiError(query.error)
      ? query.error
      : new ApiError(500, 'INTERNAL_ERROR', 'Unexpected error')

    if (error.code === 'UNAUTHENTICATED') {
      onUnauthenticated?.()
    }

    if (error.code === 'FORBIDDEN') {
      return (
        <main className={styles.page}>
          <ErrorBanner
            title="You don't have access to view cases"
            message="You don't have permission to view the case queue."
          />
        </main>
      )
    }

    if (error.code === 'VALIDATION_ERROR') {
      // URL reset in effect; show filters + brief hint while recovering.
      return (
        <main className={styles.page}>
          <header className={styles.header}>
            <h1 className={styles.title}>Case queue</h1>
          </header>
          <QueueFilterBar
            filters={filters}
            isFetching={false}
            onChange={patchFilters}
            onClear={clearFilters}
          />
          {validationHint ? (
            <ErrorBanner title="Validation error" message={validationHint} />
          ) : null}
        </main>
      )
    }
  }

  const isInitialLoading = query.isLoading && !query.data
  const isFetching = query.isFetching
  const page = query.data
  const filtersActive = hasActiveFilters(filters)

  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>Case queue</h1>
        <p className={styles.subtitle}>
          Browse and open cases. Sorted by created date (newest first).
        </p>
      </header>

      <QueueFilterBar
        filters={filters}
        isFetching={Boolean(query.data) && isFetching}
        onChange={patchFilters}
        onClear={clearFilters}
      />

      {validationHint ? (
        <div className={styles.inlineError}>
          <ErrorBanner
            title="Validation error"
            message={validationHint}
            action={{
              label: 'Dismiss',
              onClick: () => setValidationHint(null),
            }}
          />
        </div>
      ) : null}

      {isInitialLoading ? (
        <LoadingSkeleton variant="table" />
      ) : query.isError ? (
        <ErrorBanner
          title="Something went wrong"
          message={
            isApiError(query.error) && query.error.code === 'NETWORK_ERROR'
              ? 'Connection problem. Check your network and try again.'
              : 'Something went wrong. Please try again.'
          }
          action={{
            label: 'Retry',
            onClick: () => {
              void query.refetch()
            },
          }}
        />
      ) : page && page.totalItems === 0 ? (
        filtersActive ? (
          <EmptyState
            title="No cases match your filters."
            message="Try clearing filters or adjusting status, priority, type, or assignee."
            action={{ label: 'Clear filters', onClick: clearFilters }}
          />
        ) : (
          <EmptyState
            title="No cases yet."
            message="Cases will appear here when they are created."
          />
        )
      ) : page ? (
        <>
          <CaseQueueTable items={page.items} dimmed={isFetching} />
          <PaginationControls
            page={filters.page}
            pageSize={filters.pageSize}
            totalItems={page.totalItems}
            isFetching={isFetching}
            onPageChange={(nextPage) => patchFilters({ page: nextPage })}
          />
        </>
      ) : null}
    </main>
  )
}
