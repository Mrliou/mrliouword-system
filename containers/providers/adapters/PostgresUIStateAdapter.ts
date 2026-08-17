/**
 * PostgresUIStateAdapter
 * Origin Signature: MrLiouWord
 *
 * Persists user UI state via the MRL API Gateway → Postgres.
 * The frontend NEVER connects directly to the database; all reads/writes
 * go through the server-side API endpoint.
 *
 * API contract (must be implemented in mrl-api-gateway):
 *   GET  /api/mrl/ui-state/:userId   → { ok, data: UIState }
 *   POST /api/mrl/ui-state/:userId   body: Partial<UIState> → { ok, data: UIState }
 *   DELETE /api/mrl/ui-state/:userId → { ok }
 *
 * TODO: wire up database schema (see docs/MIGRATION.md Phase 3).
 */

import type { UIStateProvider, UIState } from '../interfaces/UIStateProvider'

function getApiBase(): string {
  return (
    (typeof process !== 'undefined' &&
      process.env?.NEXT_PUBLIC_API_BASE_URL) ||
    'https://api.mrliouword.com'
  )
}

async function apiRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${getApiBase()}${path}`
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  })

  if (!res.ok) {
    const body = await res.text().catch(() => '')
    throw new Error(`API ${options.method || 'GET'} ${path} → ${res.status}: ${body}`)
  }

  const json = await res.json() as { data: T }
  return json.data
}

export class PostgresUIStateAdapter implements UIStateProvider {
  async load(userId: string): Promise<UIState | null> {
    try {
      return await apiRequest<UIState>(`/api/mrl/ui-state/${encodeURIComponent(userId)}`)
    } catch {
      return null
    }
  }

  async save(userId: string, state: Partial<UIState>): Promise<UIState> {
    return apiRequest<UIState>(
      `/api/mrl/ui-state/${encodeURIComponent(userId)}`,
      {
        method: 'POST',
        body: JSON.stringify(state),
      }
    )
  }

  async clear(userId: string): Promise<void> {
    await apiRequest<void>(
      `/api/mrl/ui-state/${encodeURIComponent(userId)}`,
      { method: 'DELETE' }
    )
  }
}
