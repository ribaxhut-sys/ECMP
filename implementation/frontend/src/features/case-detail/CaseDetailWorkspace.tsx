import { lazy, Suspense, useCallback, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ApiError, getErrorCopy, isApiError } from '../../api/errors'
import { useAuth } from '../../auth/AuthContext'
import { ErrorBanner } from '../../components/ErrorBanner'
import { LoadingSkeleton } from '../../components/LoadingSkeleton'
import { useMediaQuery } from '../../lib/useMediaQuery'
import { CaseHeader } from './components/CaseHeader'
import { CaseInfoPanel } from './components/CaseInfoPanel'
import { CaseMetaPanel } from './components/CaseMetaPanel'
import { CustomerReferencePanel } from './components/CustomerReferencePanel'
import { ActionPanel } from './components/ActionPanel'
import { useCase } from './hooks/useCase'
import styles from './CaseDetailWorkspace.module.css'

const CaseActivityTimeline = lazy(
  () => import('./components/CaseActivityTimeline'),
)
const AuditHistoryPanel = lazy(() => import('./components/AuditHistoryPanel'))
const NotesPanel = lazy(() => import('../case-notes/NotesPanel'))

interface CaseDetailWorkspaceProps {
  caseId: string
}

function PanelFallback() {
  return <LoadingSkeleton variant="panel" />
}

export function CaseDetailWorkspace({ caseId }: CaseDetailWorkspaceProps) {
  const navigate = useNavigate()
  const { onUnauthenticated } = useAuth()
  const query = useCase(caseId)
  const isDesktop = useMediaQuery('(min-width: 1024px)')
  const isMobile = useMediaQuery('(max-width: 767px)')
  const [caseGone, setCaseGone] = useState(false)

  const handleCaseGone = useCallback(() => setCaseGone(true), [])

  if (query.isLoading) {
    return (
      <div className={styles.page} aria-busy="true" aria-label="Loading case">
        <LoadingSkeleton variant="header" />
        <div className={styles.layout}>
          <div className={styles.main}>
            <LoadingSkeleton variant="panel" />
            <LoadingSkeleton variant="panel" />
          </div>
          <aside className={styles.side}>
            <LoadingSkeleton variant="panel" />
            <LoadingSkeleton variant="panel" />
          </aside>
        </div>
      </div>
    )
  }

  if (caseGone) {
    return (
      <main className={styles.page}>
        <ErrorBanner
          title="Case not found"
          message="This case does not exist or is no longer available."
          action={{ label: 'Back to queue', onClick: () => navigate('/') }}
        />
      </main>
    )
  }

  if (query.isError) {
    const error = isApiError(query.error)
      ? query.error
      : new ApiError(500, 'INTERNAL_ERROR', 'Unexpected error')

    if (error.code === 'UNAUTHENTICATED') {
      onUnauthenticated?.()
    }

    const copy = getErrorCopy(error, 'load')
    const isNotFoundOrForbidden =
      error.code === 'NOT_FOUND' || error.code === 'FORBIDDEN'
    return (
      <main className={styles.page}>
        <ErrorBanner
          title={copy.title}
          message={copy.message}
          action={
            isNotFoundOrForbidden
              ? { label: 'Back to queue', onClick: () => navigate('/') }
              : { label: 'Retry', onClick: () => void query.refetch() }
          }
        />
      </main>
    )
  }

  const caseData = query.data
  if (!caseData) {
    return null
  }

  const refreshing = query.isFetching && !query.isLoading
  const actionPanel = (
    <ActionPanel
      caseData={caseData}
      isRefreshing={refreshing}
      stickyMobile={isMobile}
      onCaseGone={handleCaseGone}
    />
  )

  const sidePanels = (
    <>
      <CustomerReferencePanel caseData={caseData} />
      <CaseMetaPanel caseData={caseData} />
    </>
  )

  return (
    <div className={`${styles.page} ${isMobile ? styles.pageMobile : ''}`}>
      <CaseHeader caseData={caseData} />
      <main className={styles.layout}>
        <div className={styles.main}>
          <CaseInfoPanel caseData={caseData} />
          <Suspense fallback={<PanelFallback />}>
            <CaseActivityTimeline caseId={caseId} />
          </Suspense>
          <Suspense fallback={<PanelFallback />}>
            <AuditHistoryPanel caseId={caseId} />
          </Suspense>
          <Suspense fallback={<PanelFallback />}>
            <NotesPanel caseId={caseId} />
          </Suspense>
          {!isMobile ? actionPanel : null}
        </div>

        {isDesktop ? (
          <aside className={styles.side} aria-label="Case reference">
            {sidePanels}
          </aside>
        ) : (
          <details className={styles.detailsAccordion}>
            <summary className={styles.detailsSummary}>Details</summary>
            <div className={styles.side}>{sidePanels}</div>
          </details>
        )}
      </main>

      {isMobile ? (
        <div className={styles.mobileActionSlot}>{actionPanel}</div>
      ) : null}
    </div>
  )
}

export function CaseDetailWorkspaceRoute() {
  const { caseId } = useParams<{ caseId: string }>()
  if (!caseId) {
    return (
      <ErrorBanner
        title="Case not found"
        message="Missing case id in the URL."
      />
    )
  }
  return <CaseDetailWorkspace caseId={caseId} />
}
