/**
 * createMemoryProvider factory
 * Origin Signature: MrLiouWord
 *
 * Reads MEMORY_PROVIDER to select the correct adapter.
 *
 *   MEMORY_PROVIDER=api  → delegates to /api/mrl/memory/search (default)
 *   MEMORY_PROVIDER=kv   → CloudflareKV (Cloudflare Worker context only)
 */

import type { MemoryProvider } from '../interfaces/MemoryProvider'

export type MemoryProviderName = 'api' | 'kv'

export function createMemoryProvider(
  override?: MemoryProviderName
): MemoryProvider {
  const name: MemoryProviderName =
    override ??
    ((typeof process !== 'undefined' &&
      (process.env?.MEMORY_PROVIDER as MemoryProviderName)) ||
      'api')

  switch (name) {
    case 'api':
    default:
      return new ApiMemoryAdapter()
  }
}

/* ------------------------------------------------------------------ */
/*  Built-in minimal API adapter (no separate file needed)             */
/* ------------------------------------------------------------------ */

import type { MemoryRecord, MemoryCommitInput } from '../interfaces/MemoryProvider'

function getApiBase(): string {
  return (
    (typeof process !== 'undefined' && process.env?.NEXT_PUBLIC_API_BASE_URL) ||
    'https://api.mrliouword.com'
  )
}

class ApiMemoryAdapter implements MemoryProvider {
  async search(query: string, limit = 10): Promise<MemoryRecord[]> {
    const res = await fetch(`${getApiBase()}/api/mrl/memory/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, limit }),
    })
    if (!res.ok) throw new Error(`memory search failed: ${res.status}`)
    const json = await res.json() as { data: MemoryRecord[] }
    return json.data
  }

  async commit(input: MemoryCommitInput): Promise<MemoryRecord> {
    const res = await fetch(`${getApiBase()}/api/mrl/memory/commit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    })
    if (!res.ok) throw new Error(`memory commit failed: ${res.status}`)
    const json = await res.json() as { data: MemoryRecord }
    return json.data
  }

  async get(id: string): Promise<MemoryRecord | null> {
    const res = await fetch(
      `${getApiBase()}/api/mrl/memory/${encodeURIComponent(id)}`
    )
    if (!res.ok) return null
    const json = await res.json() as { data: MemoryRecord }
    return json.data
  }
}
