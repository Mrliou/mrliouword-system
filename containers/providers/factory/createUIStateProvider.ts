/**
 * createUIStateProvider factory
 * Origin Signature: MrLiouWord
 *
 * Reads UI_STATE_PROVIDER to select the correct adapter.
 *
 *   UI_STATE_PROVIDER=firestore  → FirestoreUIStateAdapter  (Phase 0-1)
 *   UI_STATE_PROVIDER=postgres   → PostgresUIStateAdapter   (Phase 2+)
 */

import type { UIStateProvider } from '../interfaces/UIStateProvider'

export type UIStateProviderName = 'firestore' | 'postgres'

export function createUIStateProvider(
  override?: UIStateProviderName
): UIStateProvider {
  const name: UIStateProviderName =
    override ??
    ((typeof process !== 'undefined' &&
      (process.env?.UI_STATE_PROVIDER as UIStateProviderName)) ||
      'firestore')

  switch (name) {
    case 'postgres': {
      const { PostgresUIStateAdapter } = require('../adapters/PostgresUIStateAdapter')
      return new PostgresUIStateAdapter()
    }
    case 'firestore':
    default: {
      const { FirestoreUIStateAdapter } = require('../adapters/FirestoreUIStateAdapter')
      return new FirestoreUIStateAdapter()
    }
  }
}
