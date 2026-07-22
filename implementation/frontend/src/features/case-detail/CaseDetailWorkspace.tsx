import { useNavigate, useParams } from 'react-router-dom'
import { ApiError, getErrorCopy, isApiError } from '../../api/errors'
import { ErrorBanner } from '../../components/ErrorBanner'
import { LoadingSkeleton } from '../../components/LoadingSkeleton'
import { useMediaQuery } from '../../lib/useMediaQuery'
import { CaseHeader } from './components/CaseHeader'
import { CaseInfoPanel } from './components/CaseInfoPanel'
import { CaseMetaPanel } from './components/CaseMetaPanel'
import { CustomerReferencePanel } from './components/CustomerReferencePanel'
import { ActivityTimelinePlaceholder } from './components/ActivityTimelinePlaceholder'
import { ActionPanel } from './components/ActionPanel'
import { useCase } from './hooks/useCase'
import styles from './CaseDetailWorkspace.module.css'

interface CaseDetailWorkspaceProps {
  caseId: string
}

export function CaseDetailWorkspace({ caseId }: CaseDetailWorkspaceProps) {
  const navigate = useNavigate()
  const query = useCase(caseId)
  const isDesktop = useMediaQuery('(min-width: 1024px)')
  const isMobile = useMediaQuery('(max-width: 767px)')

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

  if (query.isError) {
    const error = isApiError(query.error)
      ? query.error
      : new ApiError(500, 'INTERNAL_ERROR', 'Unexpected error')
    const copy = getErrorCopy(error, 'load')
    const isNotFoundOrForbidden =
      error.code === 'NOT_FOUND' || error.code === 'FORBIDDEN'
    return (
      <div className={styles.page}>
        <ErrorBanner
          title={copy.title}
          message={copy.message}
          action={
            isNotFoundOrForbidden
              ? { label: 'Back to queue', onClick: () => navigate('/') }
              : { label: 'Retry', onClick: () => void query.refetch() }
          }
        />
      </div>
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
      <div className={styles.layout}>
        <div className={styles.main}>
          <CaseInfoPanel caseData={caseData} />
          <ActivityTimelinePlaceholder />
          {!isMobile ? actionPanel : null}
        </div>

        {isDesktop ? (
          <aside className={styles.side}>{sidePanels}</aside>
        ) : (
          <details className={styles.detailsAccordion}>
            <summary className={styles.detailsSummary}>Details</summary>
            <div className={styles.side}>{sidePanels}</div>
          </details>
        )}
      </div>

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
