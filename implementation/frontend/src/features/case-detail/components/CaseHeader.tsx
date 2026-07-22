import { Link } from 'react-router-dom'
import type { Case } from '../../../api/types'
import { PriorityBadge } from '../../../components/PriorityBadge'
import { StatusBadge } from '../../../components/StatusBadge'
import styles from './CaseHeader.module.css'

interface CaseHeaderProps {
  caseData: Case
}

export function CaseHeader({ caseData }: CaseHeaderProps) {
  return (
    <header className={styles.header}>
      <Link to="/" className={styles.back}>
        ← Back to queue
      </Link>
      <h1 className={styles.caseId}>{caseData.caseId}</h1>
      <div className={styles.badges}>
        <StatusBadge status={caseData.status} />
        <PriorityBadge priority={caseData.priority} />
      </div>
    </header>
  )
}
