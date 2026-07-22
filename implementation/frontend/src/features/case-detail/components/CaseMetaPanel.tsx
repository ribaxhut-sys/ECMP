import type { Case } from '../../../api/types'
import styles from './CaseMetaPanel.module.css'

interface CaseMetaPanelProps {
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

export function CaseMetaPanel({ caseData }: CaseMetaPanelProps) {
  return (
    <section className={styles.panel} aria-labelledby="case-meta-heading">
      <h2 id="case-meta-heading" className={styles.title}>
        Case details
      </h2>
      <dl className={styles.list}>
        <div>
          <dt>Assignee</dt>
          <dd>{caseData.assigneeId ?? 'Unassigned'}</dd>
        </div>
        <div>
          <dt>Unit</dt>
          <dd>{caseData.unitId ?? '—'}</dd>
        </div>
        <div>
          <dt>Updated</dt>
          <dd>{formatDateTime(caseData.updatedAt)}</dd>
        </div>
      </dl>
    </section>
  )
}
