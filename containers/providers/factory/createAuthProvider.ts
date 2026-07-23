/**
 * createAuthProvider factory
 * Origin Signature: MrLiouWord
 *
 * Reads NEXT_PUBLIC_AUTH_PROVIDER to select the correct adapter.
 *
 *   NEXT_PUBLIC_AUTH_PROVIDER=firebase   → FirebaseAuthAdapter  (Phase 0-1 default)
 *   NEXT_PUBLIC_AUTH_PROVIDER=authentik  → AuthentikAuthAdapter (Phase 2+ target)
 */

import type { AuthProvider } from '../interfaces/AuthProvider'

export type AuthProviderName = 'firebase' | 'authentik'

export function createAuthProvider(
  override?: AuthProviderName
): AuthProvider {
  const name: AuthProviderName =
    override ??
    ((typeof process !== 'undefined' &&
      (process.env?.NEXT_PUBLIC_AUTH_PROVIDER as AuthProviderName)) ||
      'firebase')

  switch (name) {
    case 'authentik': {
      // Lazy require keeps firebase entirely out of the bundle
      const { AuthentikAuthAdapter } = require('../adapters/AuthentikAuthAdapter')
      return new AuthentikAuthAdapter()
    }
    case 'firebase':
    default: {
      const { FirebaseAuthAdapter } = require('../adapters/FirebaseAuthAdapter')
      return new FirebaseAuthAdapter()
    }
  }
}
