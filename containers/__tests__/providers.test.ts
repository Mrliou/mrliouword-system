/**
 * Provider factory unit tests
 * Origin Signature: MrLiouWord
 *
 * Tests the factory functions return correctly-typed adapters
 * and that env-variable-based switching works.
 */

import { createAuthProvider } from '../providers/factory/createAuthProvider'
import { createAIProvider } from '../providers/factory/createAIProvider'
import { createMemoryProvider } from '../providers/factory/createMemoryProvider'
import { createStorageProvider } from '../providers/factory/createStorageProvider'
import { createUIStateProvider } from '../providers/factory/createUIStateProvider'

/* ------------------------------------------------------------------ */
/*  createAuthProvider                                                  */
/* ------------------------------------------------------------------ */

describe('createAuthProvider', () => {
  it('returns FirebaseAuthAdapter by default', () => {
    delete process.env.NEXT_PUBLIC_AUTH_PROVIDER
    const provider = createAuthProvider()
    expect(provider).toBeDefined()
    expect(typeof provider.signIn).toBe('function')
    expect(typeof provider.signOut).toBe('function')
    expect(typeof provider.getAccessToken).toBe('function')
    expect(typeof provider.getCurrentUser).toBe('function')
    expect(typeof provider.onAuthStateChanged).toBe('function')
  })

  it('returns FirebaseAuthAdapter when override="firebase"', () => {
    const provider = createAuthProvider('firebase')
    expect(provider.constructor.name).toBe('FirebaseAuthAdapter')
  })

  it('returns AuthentikAuthAdapter when override="authentik"', () => {
    const provider = createAuthProvider('authentik')
    expect(provider.constructor.name).toBe('AuthentikAuthAdapter')
  })

  it('respects NEXT_PUBLIC_AUTH_PROVIDER env var', () => {
    process.env.NEXT_PUBLIC_AUTH_PROVIDER = 'authentik'
    const provider = createAuthProvider()
    expect(provider.constructor.name).toBe('AuthentikAuthAdapter')
    delete process.env.NEXT_PUBLIC_AUTH_PROVIDER
  })

  it('exposes all required interface methods', () => {
    const p = createAuthProvider('firebase')
    expect(typeof p.signIn).toBe('function')
    expect(typeof p.signOut).toBe('function')
    expect(typeof p.getAccessToken).toBe('function')
    expect(typeof p.getCurrentUser).toBe('function')
    expect(typeof p.onAuthStateChanged).toBe('function')
  })
})

/* ------------------------------------------------------------------ */
/*  createAIProvider                                                    */
/* ------------------------------------------------------------------ */

describe('createAIProvider', () => {
  it('returns MRLiouLocalProvider by default', () => {
    delete process.env.AI_PROVIDER
    const provider = createAIProvider()
    expect(provider).toBeDefined()
    expect(provider.constructor.name).toBe('MRLiouLocalProvider')
  })

  it('returns MRLiouLocalProvider when override="local"', () => {
    const provider = createAIProvider('local')
    expect(provider.constructor.name).toBe('MRLiouLocalProvider')
  })

  it('exposes all required interface methods', () => {
    const p = createAIProvider('local')
    expect(typeof p.listModels).toBe('function')
    expect(typeof p.generate).toBe('function')
    expect(typeof p.health).toBe('function')
  })

  it('generate returns an AsyncIterable', () => {
    const p = createAIProvider('local')
    const iter = p.generate({
      model: 'test-model',
      messages: [{ role: 'user', content: 'hello' }],
    })
    expect(iter[Symbol.asyncIterator]).toBeDefined()
  })
})

/* ------------------------------------------------------------------ */
/*  createMemoryProvider                                                */
/* ------------------------------------------------------------------ */

describe('createMemoryProvider', () => {
  it('returns api adapter by default', () => {
    delete process.env.MEMORY_PROVIDER
    const provider = createMemoryProvider()
    expect(provider).toBeDefined()
    expect(typeof provider.search).toBe('function')
    expect(typeof provider.commit).toBe('function')
    expect(typeof provider.get).toBe('function')
  })

  it('exposes all required interface methods via override', () => {
    const p = createMemoryProvider('api')
    expect(typeof p.search).toBe('function')
    expect(typeof p.commit).toBe('function')
    expect(typeof p.get).toBe('function')
  })
})

/* ------------------------------------------------------------------ */
/*  createStorageProvider                                               */
/* ------------------------------------------------------------------ */

describe('createStorageProvider', () => {
  it('returns MinIOStorageAdapter by default', () => {
    delete process.env.STORAGE_PROVIDER
    const provider = createStorageProvider()
    expect(provider).toBeDefined()
    expect(provider.constructor.name).toBe('MinIOStorageAdapter')
  })

  it('exposes all required interface methods', () => {
    const p = createStorageProvider('minio')
    expect(typeof p.upload).toBe('function')
    expect(typeof p.download).toBe('function')
    expect(typeof p.delete).toBe('function')
    expect(typeof p.list).toBe('function')
    expect(typeof p.getPresignedUrl).toBe('function')
  })
})

/* ------------------------------------------------------------------ */
/*  createUIStateProvider                                               */
/* ------------------------------------------------------------------ */

describe('createUIStateProvider', () => {
  it('returns FirestoreUIStateAdapter by default', () => {
    delete process.env.UI_STATE_PROVIDER
    const provider = createUIStateProvider()
    expect(provider).toBeDefined()
    expect(provider.constructor.name).toBe('FirestoreUIStateAdapter')
  })

  it('returns PostgresUIStateAdapter when override="postgres"', () => {
    const provider = createUIStateProvider('postgres')
    expect(provider.constructor.name).toBe('PostgresUIStateAdapter')
  })

  it('respects UI_STATE_PROVIDER env var', () => {
    process.env.UI_STATE_PROVIDER = 'postgres'
    const provider = createUIStateProvider()
    expect(provider.constructor.name).toBe('PostgresUIStateAdapter')
    delete process.env.UI_STATE_PROVIDER
  })

  it('exposes all required interface methods', () => {
    const p = createUIStateProvider('firestore')
    expect(typeof p.load).toBe('function')
    expect(typeof p.save).toBe('function')
    expect(typeof p.clear).toBe('function')
  })
})
