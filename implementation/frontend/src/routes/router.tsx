import { createBrowserRouter } from 'react-router-dom'
import App from '../App'
import { CaseDetailPage } from '../pages/CaseDetailPage'
import { CaseQueuePage } from '../pages/CaseQueuePage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: <CaseQueuePage />,
      },
      {
        path: 'cases/:caseId',
        element: <CaseDetailPage />,
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
