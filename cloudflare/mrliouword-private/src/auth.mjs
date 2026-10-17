const CLOCK_SKEW_SECONDS = 30;
const JWKS_CACHE_MS = 5 * 60 * 1000;
const jwksCache = new Map();

export class AccessTokenError extends Error {
  constructor(message, status = 401) {
    super(message);
    this.status = status;
  }
}

function decodeBase64Url(value) {
  const base64 = value.replace(/-/g, '+').replace(/_/g, '/');
  const padded = base64.padEnd(Math.ceil(base64.length / 4) * 4, '=');
  return Uint8Array.from(atob(padded), (character) => character.charCodeAt(0));
}

function decodeJsonSegment(segment) {
  return JSON.parse(new TextDecoder().decode(decodeBase64Url(segment)));
}

async function loadJwks(url, refresh = false) {
  const cached = jwksCache.get(url);
  if (!refresh && cached && cached.expiresAt > Date.now()) return cached.keys;

  let response;
  try {
    response = await fetch(url);
  } catch {
    throw new AccessTokenError('Identity provider unavailable', 503);
  }
  if (!response.ok) throw new AccessTokenError('Identity provider unavailable', 503);

  let body;
  try {
    body = await response.json();
  } catch {
    throw new AccessTokenError('Identity provider returned invalid keys', 503);
  }
  if (!Array.isArray(body.keys)) {
    throw new AccessTokenError('Identity provider returned invalid keys', 503);
  }

  jwksCache.set(url, { keys: body.keys, expiresAt: Date.now() + JWKS_CACHE_MS });
  return body.keys;
}

async function findSigningKey(url, kid) {
  let keys = await loadJwks(url);
  let key = keys.find((candidate) => candidate.kid === kid);
  if (!key) {
    keys = await loadJwks(url, true);
    key = keys.find((candidate) => candidate.kid === kid);
  }
  if (!key || key.kty !== 'RSA' || key.use === 'enc' || (key.alg && key.alg !== 'RS256')) {
    throw new AccessTokenError('Invalid access token');
  }

  try {
    return await crypto.subtle.importKey(
      'jwk',
      key,
      { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' },
      false,
      ['verify'],
    );
  } catch {
    throw new AccessTokenError('Invalid access token');
  }
}

export async function verifyAccessToken(request, env) {
  if (!env.AUTH_ISSUER || !env.AUTH_AUDIENCE || !env.AUTH_JWKS_URL) {
    throw new AccessTokenError('Authentication is not configured', 503);
  }

  let issuer;
  let jwksUrl;
  try {
    issuer = new URL(env.AUTH_ISSUER);
    jwksUrl = new URL(env.AUTH_JWKS_URL);
  } catch {
    throw new AccessTokenError('Authentication is not configured', 503);
  }
  if (issuer.protocol !== 'https:' || jwksUrl.protocol !== 'https:') {
    throw new AccessTokenError('Authentication is not configured', 503);
  }

  const authorization = request.headers.get('Authorization') || '';
  const match = /^Bearer\s+([A-Za-z0-9._~-]+)$/i.exec(authorization);
  if (!match) throw new AccessTokenError('Authentication required');

  const parts = match[1].split('.');
  if (parts.length !== 3) throw new AccessTokenError('Invalid access token');

  let header;
  let claims;
  let signature;
  try {
    header = decodeJsonSegment(parts[0]);
    claims = decodeJsonSegment(parts[1]);
    signature = decodeBase64Url(parts[2]);
  } catch {
    throw new AccessTokenError('Invalid access token');
  }
  if (header.alg !== 'RS256' || typeof header.kid !== 'string') {
    throw new AccessTokenError('Invalid access token');
  }

  const key = await findSigningKey(jwksUrl.href, header.kid);
  const signedContent = new TextEncoder().encode(`${parts[0]}.${parts[1]}`);
  let validSignature = false;
  try {
    validSignature = await crypto.subtle.verify(
      'RSASSA-PKCS1-v1_5',
      key,
      signature,
      signedContent,
    );
  } catch {
    throw new AccessTokenError('Invalid access token');
  }
  if (!validSignature) throw new AccessTokenError('Invalid access token');

  const now = Math.floor(Date.now() / 1000);
  const audience = claims.aud;
  const hasAudience = Array.isArray(audience)
    ? audience.includes(env.AUTH_AUDIENCE)
    : audience === env.AUTH_AUDIENCE;
  if (
    claims.iss !== issuer.href.replace(/\/$/, '') &&
    claims.iss !== issuer.href
  ) {
    throw new AccessTokenError('Invalid access token');
  }
  if (
    !hasAudience ||
    !Number.isFinite(claims.exp) ||
    claims.exp <= now - CLOCK_SKEW_SECONDS ||
    (claims.nbf !== undefined &&
      (!Number.isFinite(claims.nbf) || claims.nbf > now + CLOCK_SKEW_SECONDS))
  ) {
    throw new AccessTokenError('Invalid access token');
  }
  if (
    typeof claims.sub !== 'string' ||
    claims.sub.length === 0 ||
    claims.sub.length > 255 ||
    typeof claims.tenant_id !== 'string' ||
    !/^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/.test(claims.tenant_id)
  ) {
    throw new AccessTokenError('Token is missing required identity claims');
  }

  return claims;
}

export function hasRole(claims, role) {
  const roles = Array.isArray(claims.roles)
    ? claims.roles
    : typeof claims.role === 'string'
      ? [claims.role]
      : [];
  return roles.includes(role);
}

export function tenantScopedVault(namespace, tenantId) {
  const prefix = `tenant:${encodeURIComponent(tenantId)}:`;
  return {
    get: (key, options) => namespace.get(`${prefix}${key}`, options),
    put: (key, value, options) => namespace.put(`${prefix}${key}`, value, options),
    delete: (key) => namespace.delete(`${prefix}${key}`),
  };
}
