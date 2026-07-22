import type { Case } from '../../../api/types'
import styles from './CustomerReferencePanel.module.css'

interface CustomerReferencePanelProps {
  caseData: Case
}

/**
 * Degraded Customer panel (Screen Spec Gap #3 / API-010 deferred).
 * Shows only fields already on Case — never fabricates name/contact.
 */
export function CustomerReferencePanel({ caseData }: CustomerReferencePanelProps) {
  return (
    <section className={styles.panel} aria-labelledby="customer-panel-heading">
      <h2 id="customer-panel-heading" className={styles.title}>
        Customer
      </h2>
      <dl className={styles.list}>
        <div>
          <dt>Customer ID</dt>
          <dd>{caseData.customerId}</dd>
        </div>
        <div>
          <dt>Verification</dt>
          <dd>
            {caseData.customerVerified ? (
              <span className={styles.verified}>Verified</span>
            ) : (
              <span className={styles.unverified}>Unverified</span>
            )}
          </dd>
        </div>
      </dl>
      <p className={styles.note}>
        Reference only — full profile not yet available
      </p>
    </section>
  )
}
