import assert from 'node:assert/strict';
import { after, before, test } from 'node:test';
import {
  AccessTokenError,
  hasRole,
  tenantScopedVault,
  verifyAccessToken,
} from './auth.mjs';

const issuer = 'https://identity.example.test/';
const audience = 'mrliouword-api';
const jwksUrl = 'https://identity.example.test/keys';
const env = { AUTH_ISSUER: issuer, AUTH_AUDIENCE: audience, AUTH_JWKS_URL: jwksUrl };
const { privateKey, publicKey } = await crypto.subtle.generateKey(
  { name: 'RSASSA-PKCS1-v1_5', modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: 'SHA-256' },
  true,
  ['sign', 'verify'],
);
const jwk = await crypto.subtle.exportKey('jwk', publicKey);
jwk.kid = 'test-key';
jwk.alg = 'RS256';
jwk.use = 'sig';
const realFetch = globalThis.fetch;

function encode(value) {
  return Buffer.from(JSON.stringify(value)).toString('base64url');
}

async function createToken(claimOverrides = {}, signingKey = privateKey) {
  const header = encode({ alg: 'RS256', kid: 'test-key', typ: 'JWT' });
  const claims = encode({
    iss: issuer,
    aud: audience,
    sub: 'user-123',
    tenant_id: 'tenant-abc',
    exp: Math.floor(Date.now() / 1000) + 300,
    ...claimOverrides,
  });
  const signingInput = `${header}.${claims}`;
  const signature = await crypto.subtle.sign(
    'RSASSA-PKCS1-v1_5',
    signingKey,
    new TextEncoder().encode(signingInput),
  );
  return `${signingInput}.${Buffer.from(signature).toString('base64url')}`;
}

function request(token) {
  return new Request('https://api.example.test/api', {
    headers: { Authorization: 'Bearer '.concat(token) },
  });
}

before(() => {
  globalThis.fetch = async () => Response.json({ keys: [jwk] });
});

after(() => {
  globalThis.fetch = realFetch;
});

test('accepts signed tokens with matching issuer, audience, and tenant claims', async () => {
  const claims = await verifyAccessToken(request(await createToken()), env);
  assert.equal(claims.sub, 'user-123');
  assert.equal(claims.tenant_id, 'tenant-abc');
});

test('rejects invalid signatures and expired tokens', async () => {
  const otherKey = await crypto.subtle.generateKey(
    { name: 'RSASSA-PKCS1-v1_5', modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: 'SHA-256' },
    true,
    ['sign', 'verify'],
  );
  await assert.rejects(
    verifyAccessToken(request(await createToken({}, otherKey.privateKey)), env),
    AccessTokenError,
  );
  await assert.rejects(
    verifyAccessToken(
      request(await createToken({ exp: Math.floor(Date.now() / 1000) - 60 })),
      env,
    ),
    AccessTokenError,
  );
});

test('rejects incorrect issuer, audience, and missing tenant identity', async () => {
  for (const claims of [
    { iss: 'https://attacker.example.test/' },
    { aud: 'another-api' },
    { tenant_id: undefined },
  ]) {
    await assert.rejects(
      verifyAccessToken(request(await createToken(claims)), env),
      AccessTokenError,
    );
  }
});

test('fails closed when identity configuration or keys are unavailable', async () => {
  await assert.rejects(
    verifyAccessToken(request(await createToken()), {}),
    (error) => error instanceof AccessTokenError && error.status === 503,
  );

  globalThis.fetch = async () => new Response('unavailable', { status: 503 });
  await assert.rejects(
    verifyAccessToken(request(await createToken()), {
      ...env,
      AUTH_JWKS_URL: 'https://identity.example.test/unavailable',
    }),
    (error) => error instanceof AccessTokenError && error.status === 503,
  );
});

test('scopes KV keys to tenant and supports role claims', async () => {
  const values = new Map();
  const namespace = {
    get: async (key) => values.get(key) ?? null,
    put: async (key, value) => values.set(key, value),
    delete: async (key) => values.delete(key),
  };
  const tenantA = tenantScopedVault(namespace, 'tenant/a');
  const tenantB = tenantScopedVault(namespace, 'tenant-b');

  await tenantA.put('memory:head', 'a');
  await tenantB.put('memory:head', 'b');
  assert.equal(await tenantA.get('memory:head'), 'a');
  assert.equal(await tenantB.get('memory:head'), 'b');
  assert.equal(values.size, 2);
  assert.equal(hasRole({ roles: ['user', 'admin'] }, 'admin'), true);
  assert.equal(hasRole({ role: 'user' }, 'admin'), false);
});
