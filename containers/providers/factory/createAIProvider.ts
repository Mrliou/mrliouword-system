/**
 * createAIProvider factory
 * Origin Signature: MrLiouWord
 *
 * Reads AI_PROVIDER to select the correct adapter.
 *
 *   AI_PROVIDER=local      → MRLiouLocalProvider  (DL580 runtime)
 *   AI_PROVIDER=gemini     → (TODO: GeminiAIAdapter)
 *   AI_PROVIDER=openai     → (TODO: OpenAIAdapter)
 *   AI_PROVIDER=anthropic  → (TODO: AnthropicAdapter)
 */

import type { AIProvider } from '../interfaces/AIProvider'

export type AIProviderName = 'local' | 'gemini' | 'openai' | 'anthropic'

export function createAIProvider(override?: AIProviderName): AIProvider {
  const name: AIProviderName =
    override ??
    ((typeof process !== 'undefined' &&
      (process.env?.AI_PROVIDER as AIProviderName)) ||
      'local')

  switch (name) {
    case 'local':
    default: {
      const { MRLiouLocalProvider } = require('../adapters/MRLiouLocalProvider')
      return new MRLiouLocalProvider()
    }
    // TODO: add cases for 'gemini', 'openai', 'anthropic' as those adapters are built
  }
}
