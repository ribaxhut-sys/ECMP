import type { Case } from '../../../api/types'
import styles from './CaseInfoPanel.module.css'

interface CaseInfoPanelProps {
  caseData: Case
}

function formatDateTime(iso: string): string {
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(iso))
  } catch {
    return iso
  }
}

export function CaseInfoPanel({ caseData }: CaseInfoPanelProps) {
  return (
    <section className={styles.panel} aria-labelledby="case-info-heading">
      <h2 id="case-info-heading" className={styles.subject}>
        {caseData.subject}
      </h2>
      <p className={styles.description}>{caseData.description}</p>
      <dl className={styles.meta}>
        <div>
          <dt>Type</dt>
          <dd>{caseData.caseType}</dd>
        </div>
        <div>
          <dt>Channel</dt>
          <dd>{caseData.channel ?? '—'}</dd>
        </div>
        <div>
          <dt>Created</dt>
          <dd>{formatDateTime(caseData.createdAt)}</dd>
        </div>
        <div>
          <dt>Created by</dt>
          <dd>{caseData.createdBy}</dd>
        </div>
      </dl>
    </section>
  )
}
