/**
 * AIProvider interface
 * Origin Signature: MrLiouWord
 *
 * Abstraction layer for AI model backends.
 * Switch via AI_PROVIDER env var: 'gemini' | 'local' | 'openai' | 'anthropic'
 */

export interface ModelInfo {
  id: string
  name: string
  description?: string
  contextWindow?: number
  /** e.g. 'text', 'multimodal', 'embedding' */
  type?: string
  /** Provider-specific metadata */
  meta?: Record<string, unknown>
}

export interface GenerateRequest {
  model: string
  messages: Array<{
    role: 'user' | 'assistant' | 'system'
    content: string
  }>
  temperature?: number
  maxTokens?: number
  stream?: boolean
  /** Extra provider-specific parameters */
  options?: Record<string, unknown>
}

export type GenerateEventType = 'delta' | 'done' | 'error' | 'metadata'

export interface GenerateEvent {
  type: GenerateEventType
  /** Text chunk (for 'delta' events) */
  delta?: string
  /** Final full content (for 'done' events) */
  content?: string
  /** Error details (for 'error' events) */
  error?: string
  /** Usage statistics etc. (for 'metadata' events) */
  metadata?: Record<string, unknown>
}

export type HealthStatus = 'healthy' | 'degraded' | 'unavailable'

export interface HealthResponse {
  status: HealthStatus
  latencyMs?: number
  message?: string
  models?: string[]
}

export interface AIProvider {
  /**
   * List available models from this provider.
   */
  listModels(): Promise<ModelInfo[]>

  /**
   * Generate a response. Yields GenerateEvent objects for streaming.
   * Adapters that don't support streaming may yield a single 'done' event.
   */
  generate(request: GenerateRequest): AsyncIterable<GenerateEvent>

  /**
   * Health-check the underlying model service.
   */
  health(): Promise<HealthResponse>
}
