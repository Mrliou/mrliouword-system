/**
 * MRLiouLocalProvider
 * Origin Signature: MrLiouWord
 *
 * AI provider that calls the local MRLiou runtime on the DL580.
 * Implements the AIProvider interface; use via createAIProvider('local').
 *
 * Runtime service:
 *   GET  /health                  → { ok, service, version }
 *   GET  /api/mrl/runtimeos/ai/models → { ok, data: ModelInfo[] }
 *   POST /api/mrl/runtimeos/ai/generate → SSE stream or JSON
 *
 * Environment:
 *   MRL_API_BASE_URL=http://mrl-runtime:7810   (server-side only!)
 */

import type {
  AIProvider,
  ModelInfo,
  GenerateRequest,
  GenerateEvent,
  HealthResponse,
} from '../interfaces/AIProvider'

function getRuntimeBase(): string {
  return (
    (typeof process !== 'undefined' && process.env?.MRL_API_BASE_URL) ||
    'http://localhost:7810'
  )
}

export class MRLiouLocalProvider implements AIProvider {
  async listModels(): Promise<ModelInfo[]> {
    const res = await fetch(
      `${getRuntimeBase()}/api/mrl/runtimeos/ai/models`
    )
    if (!res.ok) throw new Error(`listModels failed: ${res.status}`)
    const json = await res.json() as { data: ModelInfo[] }
    return json.data
  }

  async *generate(request: GenerateRequest): AsyncIterable<GenerateEvent> {
    const res = await fetch(
      `${getRuntimeBase()}/api/mrl/runtimeos/ai/generate`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      }
    )

    if (!res.ok) {
      const text = await res.text()
      yield { type: 'error', error: `generate failed: ${res.status} ${text}` }
      return
    }

    const contentType = res.headers.get('content-type') || ''

    // SSE streaming response
    if (contentType.includes('text/event-stream')) {
      const reader = res.body?.getReader()
      if (!reader) {
        yield { type: 'error', error: 'No response body' }
        return
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim()
            if (data === '[DONE]') {
              yield { type: 'done' }
              return
            }
            try {
              const event = JSON.parse(data) as GenerateEvent
              yield event
            } catch {
              // skip malformed SSE lines
            }
          }
        }
      }

      yield { type: 'done' }
      return
    }

    // Non-streaming JSON response
    const json = await res.json() as { data?: { content?: string }; content?: string }
    const content: string = json.data?.content ?? json.content ?? ''
    yield { type: 'delta', delta: content }
    yield { type: 'done', content }
  }

  async health(): Promise<HealthResponse> {
    try {
      const start = Date.now()
      const res = await fetch(`${getRuntimeBase()}/health`)
      const latencyMs = Date.now() - start

      if (!res.ok) {
        return { status: 'degraded', latencyMs, message: `HTTP ${res.status}` }
      }

      const json = await res.json() as { service?: string; models?: string[] }
      return {
        status: 'healthy',
        latencyMs,
        message: json.service,
        models: json.models,
      }
    } catch (err) {
      return {
        status: 'unavailable',
        message: err instanceof Error ? err.message : 'Unknown error',
      }
    }
  }
}
