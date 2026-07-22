import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { AsyncPanel } from './AsyncPanel'

describe('AsyncPanel', () => {
  it('renders loading skeleton by default', () => {
    const { container } = render(
      <AsyncPanel
        isLoading
        isError={false}
        isEmpty={false}
        emptyTitle=""
        emptyMessage=""
      >
        <p>content</p>
      </AsyncPanel>,
    )
    expect(container.querySelector('[aria-busy="true"]')).toBeTruthy()
    expect(screen.queryByText('content')).toBeNull()
  })

  it('renders custom loading content', () => {
    render(
      <AsyncPanel
        isLoading
        loadingContent={<div data-testid="custom-load">loading</div>}
        isError={false}
        isEmpty={false}
        emptyTitle=""
        emptyMessage=""
      >
        <p>content</p>
      </AsyncPanel>,
    )
    expect(screen.getByTestId('custom-load')).toBeInTheDocument()
  })

  it('renders error with errorAction', async () => {
    const onClick = vi.fn()
    const user = userEvent.setup()
    render(
      <AsyncPanel
        isLoading={false}
        isError
        errorTitle="Boom"
        errorMessage="Failed"
        errorAction={{ label: 'Back to queue', onClick }}
        isEmpty={false}
        emptyTitle=""
        emptyMessage=""
      >
        <p>content</p>
      </AsyncPanel>,
    )
    expect(screen.getByText('Boom')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Back to queue' }))
    expect(onClick).toHaveBeenCalledOnce()
  })

  it('renders empty state', () => {
    render(
      <AsyncPanel
        isLoading={false}
        isError={false}
        isEmpty
        emptyTitle="No notes yet."
        emptyMessage="Add one."
      >
        <p>content</p>
      </AsyncPanel>,
    )
    expect(screen.getByText('No notes yet.')).toBeInTheDocument()
    expect(screen.queryByText('content')).toBeNull()
  })

  it('renders children when ready', () => {
    render(
      <AsyncPanel
        isLoading={false}
        isError={false}
        isEmpty={false}
        emptyTitle=""
        emptyMessage=""
      >
        <p>ready</p>
      </AsyncPanel>,
    )
    expect(screen.getByText('ready')).toBeInTheDocument()
  })
})

describe('QueryClientProvider smoke', () => {
  it('mounts a provider for hook tests', () => {
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    })
    render(
      <QueryClientProvider client={client}>
        <div>ok</div>
      </QueryClientProvider>,
    )
    expect(screen.getByText('ok')).toBeInTheDocument()
  })
})
