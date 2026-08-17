/**
 * AuthProvider interface
 * Origin Signature: MrLiouWord
 *
 * Abstraction layer for authentication backends.
 * Supported implementations: FirebaseAuthAdapter, AuthentikAuthAdapter
 * Switch via NEXT_PUBLIC_AUTH_PROVIDER env var.
 */

export interface AuthUser {
  uid: string
  email: string | null
  displayName: string | null
  /** Raw provider-specific claims/attributes */
  claims?: Record<string, unknown>
}

export interface AuthProvider {
  /**
   * Trigger the sign-in flow (redirect or popup depending on adapter).
   * Resolves when the user is authenticated.
   */
  signIn(): Promise<void>

  /**
   * Sign out the current user and clear any persisted tokens.
   */
  signOut(): Promise<void>

  /**
   * Return a valid access token for the currently authenticated user,
   * or null if the user is not signed in.
   */
  getAccessToken(): Promise<string | null>

  /**
   * Return the currently authenticated user, or null.
   */
  getCurrentUser(): Promise<AuthUser | null>

  /**
   * Subscribe to auth state changes.
   * Returns an unsubscribe function.
   */
  onAuthStateChanged(callback: (user: AuthUser | null) => void): () => void
}
