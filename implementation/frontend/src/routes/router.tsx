import { Suspense, lazy } from 'react'
import { createBrowserRouter } from 'react-router-dom'
import App from '../App'

const CaseQueuePage = lazy(() =>
  import('../pages/CaseQueuePage').then((m) => ({ default: m.CaseQueuePage })),
)
const CaseDetailPage = lazy(() =>
  import('../pages/CaseDetailPage').then((m) => ({ default: m.CaseDetailPage })),
)

const routeFallback = (
  <p style={{ padding: '1.5rem', fontFamily: 'system-ui, sans-serif' }}>
    Loading…
  </p>
)

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={routeFallback}>
            <CaseQueuePage />
          </Suspense>
        ),
      },
      {
        path: 'cases/:caseId',
        element: (
          <Suspense fallback={routeFallback}>
            <CaseDetailPage />
          </Suspense>
        ),
      },
      {
        path: '*',
        element: (
          <p style={{ padding: '1.5rem', fontFamily: 'system-ui, sans-serif' }}>
            Page not found.
          </p>
        ),
      },
    ],
  },
])
