/**
 * AuthentikAuthAdapter
 * Origin Signature: MrLiouWord
 *
 * OIDC / PKCE client-side authentication via Authentik.
 * This is the TARGET autonomous adapter for Phase 2+.
 *
 * TODO: Replace placeholder values with your real Authentik tenant:
 *   - NEXT_PUBLIC_AUTH_BASE_URL → e.g. https://auth.mrliouword.com
 *   - NEXT_PUBLIC_AUTH_CLIENT_ID → Authentik application slug
 *   - AUTH_CLIENT_SECRET → server-side only, never NEXT_PUBLIC_*
 *
 * PKCE flow (no client secret required for SPA):
 *   1. generateCodeVerifier / generateCodeChallenge
 *   2. redirect to Authentik /authorize
 *   3. exchange code + verifier for tokens at /token
 *   4. store tokens in sessionStorage (or httpOnly cookie via BFF)
 */

import type { AuthProvider, AuthUser } from '../interfaces/AuthProvider'

/* -------------------------------------------------------------------------- */
/*  Helpers                                                                     */
/* -------------------------------------------------------------------------- */

function randomBase64url(bytes: number): string {
  const arr = new Uint8Array(bytes)
  crypto.getRandomValues(arr)
  return btoa(String.fromCharCode(...arr))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '')
}

async function sha256Base64url(plain: string): Promise<string> {
  const encoded = new TextEncoder().encode(plain)
  const digest = await crypto.subtle.digest('SHA-256', encoded)
  return btoa(String.fromCharCode(...new Uint8Array(digest)))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '')
}

/* -------------------------------------------------------------------------- */
/*  Token storage (sessionStorage-backed, swap for secure cookie BFF later)   */
/* -------------------------------------------------------------------------- */

const TOKEN_KEY = 'mrl_oidc_tokens'

interface OIDCTokens {
  accessToken: string
  idToken?: string
  refreshToken?: string
  expiresAt: number
}

function saveTokens(tokens: OIDCTokens): void {
  try {
    sessionStorage.setItem(TOKEN_KEY, JSON.stringify(tokens))
  } catch {
    // no-op in environments without sessionStorage (SSR)
  }
}

function loadTokens(): OIDCTokens | null {
  try {
    const raw = sessionStorage.getItem(TOKEN_KEY)
    return raw ? (JSON.parse(raw) as OIDCTokens) : null
  } catch {
    return null
  }
}

function clearTokens(): void {
  try {
    sessionStorage.removeItem(TOKEN_KEY)
  } catch {
    // no-op
  }
}

/* -------------------------------------------------------------------------- */

export class AuthentikAuthAdapter implements AuthProvider {
  private readonly baseUrl: string
  private readonly clientId: string
  private readonly redirectUri: string

  /** Registered onAuthStateChanged listeners */
  private listeners: Array<(user: AuthUser | null) => void> = []

  constructor() {
    this.baseUrl =
      (typeof process !== 'undefined' &&
        process.env?.NEXT_PUBLIC_AUTH_BASE_URL) ||
      ''
    this.clientId =
      (typeof process !== 'undefined' &&
        process.env?.NEXT_PUBLIC_AUTH_CLIENT_ID) ||
      ''
    // Default to current origin + /auth/callback
    this.redirectUri =
      typeof window !== 'undefined'
        ? `${window.location.origin}/auth/callback`
        : ''
  }

  private get authorizeEndpoint(): string {
    // TODO: verify slug with actual Authentik application config
    return `${this.baseUrl}/application/o/authorize/`
  }

  private get tokenEndpoint(): string {
    return `${this.baseUrl}/application/o/token/`
  }

  private get userInfoEndpoint(): string {
    return `${this.baseUrl}/application/o/userinfo/`
  }

  private get endSessionEndpoint(): string {
    return `${this.baseUrl}/application/o/end-session/`
  }

  async signIn(): Promise<void> {
    const verifier = randomBase64url(32)
    const challenge = await sha256Base64url(verifier)
    const state = randomBase64url(16)

    sessionStorage.setItem('pkce_verifier', verifier)
    sessionStorage.setItem('pkce_state', state)

    const params = new URLSearchParams({
      client_id: this.clientId,
      redirect_uri: this.redirectUri,
      response_type: 'code',
      scope: 'openid profile email offline_access',
      code_challenge: challenge,
      code_challenge_method: 'S256',
      state,
    })

    window.location.href = `${this.authorizeEndpoint}?${params}`
  }

  /**
   * Call this from your /auth/callback page to exchange the code for tokens.
   */
  async handleCallback(code: string, returnedState: string): Promise<void> {
    const verifier = sessionStorage.getItem('pkce_verifier') || ''
    const savedState = sessionStorage.getItem('pkce_state') || ''

    if (returnedState !== savedState) {
      throw new Error('OAuth state mismatch — possible CSRF attack')
    }

    const body = new URLSearchParams({
      grant_type: 'authorization_code',
      client_id: this.clientId,
      redirect_uri: this.redirectUri,
      code,
      code_verifier: verifier,
    })

    const res = await fetch(this.tokenEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString(),
    })

    if (!res.ok) {
      const text = await res.text()
      throw new Error(`Token exchange failed: ${res.status} ${text}`)
    }

    const data = await res.json() as {
      access_token: string
      id_token?: string
      refresh_token?: string
      expires_in: number
    }
    saveTokens({
      accessToken: data.access_token,
      idToken: data.id_token,
      refreshToken: data.refresh_token,
      expiresAt: Date.now() + data.expires_in * 1000,
    })

    sessionStorage.removeItem('pkce_verifier')
    sessionStorage.removeItem('pkce_state')

    const user = await this.getCurrentUser()
    this.listeners.forEach((cb) => cb(user))
  }

  async signOut(): Promise<void> {
    const tokens = loadTokens()
    clearTokens()

    if (tokens?.idToken) {
      const params = new URLSearchParams({
        id_token_hint: tokens.idToken,
        post_logout_redirect_uri:
          typeof window !== 'undefined' ? window.location.origin : '',
      })
      window.location.href = `${this.endSessionEndpoint}?${params}`
    }

    this.listeners.forEach((cb) => cb(null))
  }

  async getAccessToken(): Promise<string | null> {
    const tokens = loadTokens()
    if (!tokens) return null

    // TODO: implement token refresh when tokens.expiresAt < Date.now()
    if (tokens.expiresAt < Date.now()) {
      // TODO: use tokens.refreshToken to get a new access token
      clearTokens()
      return null
    }

    return tokens.accessToken
  }

  async getCurrentUser(): Promise<AuthUser | null> {
    const token = await this.getAccessToken()
    if (!token) return null

    const res = await fetch(this.userInfoEndpoint, {
      headers: { Authorization: 'Bearer ' + token },
    })

    if (!res.ok) return null

    const data = await res.json() as {
      sub: string
      email?: string
      name?: string
      preferred_username?: string
      [key: string]: unknown
    }
    return {
      uid: data.sub,
      email: data.email ?? null,
      displayName: data.name ?? data.preferred_username ?? null,
      claims: data,
    }
  }

  onAuthStateChanged(callback: (user: AuthUser | null) => void): () => void {
    this.listeners.push(callback)

    // Emit current state immediately
    this.getCurrentUser()
      .then((user) => callback(user))
      .catch(() => callback(null))

    return () => {
      this.listeners = this.listeners.filter((l) => l !== callback)
    }
  }
}
