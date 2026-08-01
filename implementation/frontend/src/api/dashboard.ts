import { apiRequest } from './client'
import type { DashboardQueuesResponse } from './types'

/** GET /v1/dashboard/queues — API-040 (CAP-007). Not API-390 / API-513. */
export function getDashboardQueues(): Promise<DashboardQueuesResponse> {
  return apiRequest<DashboardQueuesResponse>('/v1/dashboard/queues')
}
