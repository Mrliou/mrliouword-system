/**
 * UIStateProvider interface
 * Origin Signature: MrLiouWord
 *
 * Abstraction for persisting user UI preferences/state.
 * Switch via UI_STATE_PROVIDER env var: 'firestore' | 'postgres'
 */

export interface UIState {
  userId: string
  theme?: 'light' | 'dark' | 'system'
  language?: string
  sidebarOpen?: boolean
  /** Arbitrary extra preference keys */
  preferences?: Record<string, unknown>
  updatedAt?: string
}

export interface UIStateProvider {
  /**
   * Load the UI state for the given user.
   * Returns null if no state has been saved yet.
   */
  load(userId: string): Promise<UIState | null>

  /**
   * Persist (merge) UI state for the given user.
   * Partial updates are merged with existing state.
   */
  save(userId: string, state: Partial<UIState>): Promise<UIState>

  /**
   * Delete all persisted state for the given user.
   */
  clear(userId: string): Promise<void>
}
