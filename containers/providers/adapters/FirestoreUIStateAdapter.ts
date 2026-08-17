/**
 * FirestoreUIStateAdapter
 * Origin Signature: MrLiouWord
 *
 * Persists user UI state in Firestore.
 * Transition adapter for Phase 0-1. Switch to PostgresUIStateAdapter in Phase 2+.
 */

import type { UIStateProvider, UIState } from '../interfaces/UIStateProvider'

export class FirestoreUIStateAdapter implements UIStateProvider {
  private readonly collection: string

  constructor(collection = 'ui_preferences') {
    this.collection = collection
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private async getFirestore(): Promise<any> {
    const { initializeApp, getApps, getApp } = await import(
      /* @ts-expect-error optional peer dependency */
      'firebase/app'
    )
    const { getFirestore } = await import(
      /* @ts-expect-error optional peer dependency */
      'firebase/firestore'
    )

    const app =
      getApps().length > 0
        ? getApp()
        : initializeApp({
            apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
            authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
            projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
          })

    return getFirestore(app)
  }

  async load(userId: string): Promise<UIState | null> {
    const db = await this.getFirestore()
    const { doc, getDoc } = await import(
      /* @ts-expect-error optional peer dependency */
      'firebase/firestore'
    )

    const snap = await getDoc(doc(db, this.collection, userId))
    if (!snap.exists()) return null
    return snap.data() as UIState
  }

  async save(userId: string, state: Partial<UIState>): Promise<UIState> {
    const db = await this.getFirestore()
    const { doc, setDoc, getDoc } = await import(
      /* @ts-expect-error optional peer dependency */
      'firebase/firestore'
    )

    const ref = doc(db, this.collection, userId)
    const existing = (await getDoc(ref)).data() as UIState | undefined
    const merged: UIState = {
      ...(existing || {}),
      ...state,
      userId,
      updatedAt: new Date().toISOString(),
    }
    await setDoc(ref, merged, { merge: true })
    return merged
  }

  async clear(userId: string): Promise<void> {
    const db = await this.getFirestore()
    const { doc, deleteDoc } = await import(
      /* @ts-expect-error optional peer dependency */
      'firebase/firestore'
    )
    await deleteDoc(doc(db, this.collection, userId))
  }
}
