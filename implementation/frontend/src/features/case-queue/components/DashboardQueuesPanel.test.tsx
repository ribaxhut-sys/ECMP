import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { DashboardQueuesPanel } from './DashboardQueuesPanel'

describe('DashboardQueuesPanel', () => {
  it('renders asOf and queue buckets from API-040', async () => {
    const onSelect = vi.fn()
    render(
      <DashboardQueuesPanel
        asOf="2026-07-21T09:30:00Z"
        queues={[
          {
            unitId: 'UNIT-01',
            status: 'ASSIGNED',
            count: 5,
            oldestCreatedAt: '2026-07-20T02:10:00Z',
          },
        ]}
        onSelectStatus={onSelect}
      />,
    )

    expect(
      screen.getByRole('region', { name: 'Operational queue dashboard' }),
    ).toBeInTheDocument()
    expect(screen.getByText('5')).toBeInTheDocument()
    expect(screen.getByText(/Unit UNIT-01/)).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: /Assigned/i }))
    expect(onSelect).toHaveBeenCalledWith('ASSIGNED')
  })

  it('shows empty state when no unit-scoped buckets', () => {
    render(
      <DashboardQueuesPanel
        asOf="2026-07-21T09:30:00Z"
        queues={[]}
        onSelectStatus={vi.fn()}
      />,
    )
    expect(
      screen.getByText(/No unit-scoped cases in queue yet/i),
    ).toBeInTheDocument()
  })
})
