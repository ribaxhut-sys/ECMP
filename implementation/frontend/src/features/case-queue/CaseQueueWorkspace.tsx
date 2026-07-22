import { useCallback, useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { ApiError, isApiError } from '../../api/errors'
import { useAuth } from '../../auth/AuthContext'
import { AsyncPanel } from '../../components/AsyncPanel'
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

    // Full-page 403 — filters are not useful without cases:read.
    if (error.code === 'FORBIDDEN') {
      return (
        <main className={styles.page}>
          <AsyncPanel
            isLoading={false}
            isError
            errorTitle="You don't have access to view cases"
            errorMessage="You don't have permission to view the case queue."
            isEmpty={false}
            emptyTitle=""
            emptyMessage=""
          >
            {null}
          </AsyncPanel>
        </main>
      )
    }

    // Validation recovery stays workspace-local (filters remain usable).
    if (error.code === 'VALIDATION_ERROR') {
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
  const hardError =
    query.isError &&
    !(isApiError(query.error) && query.error.code === 'VALIDATION_ERROR') &&
    !(isApiError(query.error) && query.error.code === 'FORBIDDEN')

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

      {/*
        Dimmed-refetch stays workspace-local (CaseQueueTable dimmed=isFetching).
        AsyncPanel covers initial-load / hard-error / empty only (Sprint-07 §2a).
      */}
      <AsyncPanel
        isLoading={isInitialLoading}
        loadingContent={<LoadingSkeleton variant="table" />}
        isError={hardError}
        errorTitle="Something went wrong"
        errorMessage={
          isApiError(query.error) && query.error.code === 'NETWORK_ERROR'
            ? 'Connection problem. Check your network and try again.'
            : 'Something went wrong. Please try again.'
        }
        errorAction={{
          label: 'Retry',
          onClick: () => {
            void query.refetch()
          },
        }}
        isEmpty={Boolean(page && page.totalItems === 0)}
        emptyTitle={
          filtersActive ? 'No cases match your filters.' : 'No cases yet.'
        }
        emptyMessage={
          filtersActive
            ? 'Try clearing filters or adjusting status, priority, type, or assignee.'
            : 'Cases will appear here when they are created.'
        }
        emptyAction={
          filtersActive
            ? { label: 'Clear filters', onClick: clearFilters }
            : undefined
        }
      >
        {page ? (
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
      </AsyncPanel>
    </main>
  )
}
