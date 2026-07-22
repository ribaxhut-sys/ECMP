import styles from './PaginationControls.module.css'

interface PaginationControlsProps {
  page: number
  pageSize: number
  totalItems: number
  isFetching: boolean
  onPageChange: (page: number) => void
}

export function PaginationControls({
  page,
  pageSize,
  totalItems,
  isFetching,
  onPageChange,
}: PaginationControlsProps) {
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize) || 1)
  const safePage = Math.min(page, totalPages)
  const start = totalItems === 0 ? 0 : (safePage - 1) * pageSize + 1
  const end = Math.min(safePage * pageSize, totalItems)
  const canPrev = safePage > 1
  const canNext = safePage < totalPages

  return (
    <div className={styles.bar} aria-label="Pagination">
      <p className={styles.info} aria-live="polite">
        {totalItems === 0
          ? 'Showing 0 of 0'
          : `Showing ${start}–${end} of ${totalItems}`}
      </p>
      <div className={styles.buttons}>
        <button
          type="button"
          className={styles.button}
          disabled={!canPrev || isFetching}
          onClick={() => onPageChange(safePage - 1)}
          aria-label="Previous page"
        >
          {isFetching && canPrev ? '…' : 'Previous'}
        </button>
        <span className={styles.pageLabel}>
          Page {safePage} of {totalPages}
        </span>
        <button
          type="button"
          className={styles.button}
          disabled={!canNext || isFetching}
          onClick={() => onPageChange(safePage + 1)}
          aria-label="Next page"
        >
          {isFetching && canNext ? '…' : 'Next'}
        </button>
      </div>
    </div>
  )
}
