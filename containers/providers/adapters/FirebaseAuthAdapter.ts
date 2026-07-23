/**
 * FirebaseAuthAdapter
 * Origin Signature: MrLiouWord
 *
 * Wraps Firebase Authentication for use via the AuthProvider interface.
 * This is the TRANSITION adapter — retain for Phase 0-1.
 *
 * Runtime dependencies are loaded dynamically so the build does not hard-require
 * the Firebase SDK when using a different provider.
 */

import type { AuthProvider, AuthUser } from '../interfaces/AuthProvider'

/* -------------------------------------------------------------------------- */
/*  Minimal type stubs so we don't hard-depend on firebase package at compile  */
/* -------------------------------------------------------------------------- */

type FirebaseUser = {
  uid: string
  email: string | null
  displayName: string | null
  getIdToken(forceRefresh?: boolean): Promise<string>
}

type Unsubscribe = () => void

/* -------------------------------------------------------------------------- */

export class FirebaseAuthAdapter implements AuthProvider {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private auth: any = null

  /**
   * Lazily initialise the Firebase Auth instance.
   * Throws if the firebase/auth package is not installed.
   */
  private async getAuth(): Promise<NonNullable<typeof this.auth>> {
    if (this.auth) return this.auth

    // Dynamic import keeps firebase out of the bundle when not used
    const { initializeApp, getApps, getApp } = await import(
      /* @ts-expect-error optional peer dependency */
      'firebase/app'
    )
    const { getAuth } = await import(
      /* @ts-expect-error optional peer dependency */
      'firebase/auth'
    )

    const firebaseConfig = {
      apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
      authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
      projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
      storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
      messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
      appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
    }

    const app = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig)
    this.auth = getAuth(app)
    return this.auth
  }

  async signIn(): Promise<void> {
    const auth = await this.getAuth()
    const { GoogleAuthProvider, signInWithPopup } = await import(
      /* @ts-expect-error optional peer dependency */
      'firebase/auth'
    )
    const provider = new GoogleAuthProvider()
    await signInWithPopup(auth, provider)
  }

  async signOut(): Promise<void> {
    const auth = await this.getAuth()
    const { signOut } = await import(
      /* @ts-expect-error optional peer dependency */
      'firebase/auth'
    )
    await signOut(auth)
  }

  async getAccessToken(): Promise<string | null> {
    const auth = await this.getAuth()
    const user: FirebaseUser | null = auth.currentUser
    if (!user) return null
    return user.getIdToken()
  }

  async getCurrentUser(): Promise<AuthUser | null> {
    const auth = await this.getAuth()
    const user: FirebaseUser | null = auth.currentUser
    if (!user) return null
    return {
      uid: user.uid,
      email: user.email,
      displayName: user.displayName,
    }
  }

  onAuthStateChanged(callback: (user: AuthUser | null) => void): () => void {
    // Return a no-op unsubscribe until auth is ready; actual subscription
    // should be set up after getAuth() resolves in production code.
    let unsubscribe: Unsubscribe = () => {}

    this.getAuth().then((auth) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      import('firebase/auth' as any).then(({ onAuthStateChanged }) => {
        unsubscribe = onAuthStateChanged(auth, (user: FirebaseUser | null) => {
          if (!user) {
            callback(null)
            return
          }
          callback({
            uid: user.uid,
            email: user.email,
            displayName: user.displayName,
          })
        })
      })
    })

    return () => unsubscribe()
  }
}
