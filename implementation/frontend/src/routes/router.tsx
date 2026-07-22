import { createBrowserRouter } from 'react-router-dom'
import App from '../App'
import { CaseDetailPage } from '../pages/CaseDetailPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: (
          <p style={{ padding: '1.5rem', fontFamily: 'system-ui, sans-serif' }}>
            Open a case from its URL (e.g. /cases/CASE-…). Queue screen is out of
            scope for Sprint-04.
          </p>
        ),
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
