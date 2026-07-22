import { useNavigate, useParams } from 'react-router-dom'
import { ApiError, getErrorCopy, isApiError } from '../../api/errors'
import { ErrorBanner } from '../../components/ErrorBanner'
import { LoadingSkeleton } from '../../components/LoadingSkeleton'
import { CaseHeader } from './components/CaseHeader'
import { CaseInfoPanel } from './components/CaseInfoPanel'
import { CaseMetaPanel } from './components/CaseMetaPanel'
import { CustomerReferencePanel } from './components/CustomerReferencePanel'
import { ActivityTimelinePlaceholder } from './components/ActivityTimelinePlaceholder'
import { useCase } from './hooks/useCase'
import styles from './CaseDetailWorkspace.module.css'

interface CaseDetailWorkspaceProps {
  caseId: string
}

export function CaseDetailWorkspace({ caseId }: CaseDetailWorkspaceProps) {
  const navigate = useNavigate()
  const query = useCase(caseId)

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

  return (
    <div className={styles.page}>
      <CaseHeader caseData={caseData} />
      <div className={styles.layout}>
        <div className={styles.main}>
          <CaseInfoPanel caseData={caseData} />
          <ActivityTimelinePlaceholder />
          {/* ActionPanel — Step 4+ */}
        </div>
        <aside className={styles.side}>
          <CustomerReferencePanel caseData={caseData} />
          <CaseMetaPanel caseData={caseData} />
        </aside>
      </div>
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
