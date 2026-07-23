/**
 * MinIOStorageAdapter
 * Origin Signature: MrLiouWord
 *
 * File storage via the MRL API Gateway → MinIO.
 * The frontend NEVER exposes MinIO credentials; all file operations
 * go through the server-side API endpoint.
 *
 * API contract (must be implemented in mrl-api-gateway):
 *   POST   /api/mrl/files/upload          multipart/form-data → { ok, data: StorageObject }
 *   GET    /api/mrl/files/download/:key   → binary response
 *   DELETE /api/mrl/files/:key            → { ok }
 *   GET    /api/mrl/files/list            query: ?prefix=… → { ok, data: StorageObject[] }
 *   GET    /api/mrl/files/presign/:key    query: ?expires=… → { ok, data: { url } }
 *
 * TODO: implement gateway-side MinIO integration (see docs/MIGRATION.md Phase 3).
 */

import type {
  StorageProvider,
  StorageObject,
  UploadOptions,
} from '../interfaces/StorageProvider'

function getApiBase(): string {
  return (
    (typeof process !== 'undefined' &&
      process.env?.NEXT_PUBLIC_API_BASE_URL) ||
    'https://api.mrliouword.com'
  )
}

export class MinIOStorageAdapter implements StorageProvider {
  async upload(
    key: string,
    data: Uint8Array | ReadableStream | string,
    options: UploadOptions = {}
  ): Promise<StorageObject> {
    const form = new FormData()
    let blob: Blob

    if (typeof data === 'string') {
      blob = new Blob([data], { type: options.contentType || 'text/plain' })
    } else if (data instanceof Uint8Array) {
      blob = new Blob([data.buffer as ArrayBuffer], { type: options.contentType || 'application/octet-stream' })
    } else {
      // ReadableStream → collect
      const reader = (data as ReadableStream).getReader()
      const chunks: Uint8Array[] = []
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        if (value) chunks.push(value)
      }
      const merged = new Uint8Array(chunks.reduce((n, c) => n + c.length, 0))
      let offset = 0
      for (const c of chunks) {
        merged.set(c, offset)
        offset += c.length
      }
      blob = new Blob([merged.buffer as ArrayBuffer], { type: options.contentType || 'application/octet-stream' })
    }

    form.append('file', blob, key)
    form.append('key', key)
    if (options.contentType) form.append('contentType', options.contentType)
    if (options.meta) form.append('meta', JSON.stringify(options.meta))

    const res = await fetch(`${getApiBase()}/api/mrl/files/upload`, {
      method: 'POST',
      body: form,
    })

    if (!res.ok) {
      throw new Error(`Upload failed: ${res.status}`)
    }

    const json = await res.json() as { data: StorageObject }
    return json.data
  }

  async download(key: string): Promise<Uint8Array> {
    const res = await fetch(
      `${getApiBase()}/api/mrl/files/download/${encodeURIComponent(key)}`
    )
    if (!res.ok) throw new Error(`Download failed: ${res.status}`)
    const buf = await res.arrayBuffer()
    return new Uint8Array(buf)
  }

  async delete(key: string): Promise<void> {
    const res = await fetch(
      `${getApiBase()}/api/mrl/files/${encodeURIComponent(key)}`,
      { method: 'DELETE' }
    )
    if (!res.ok) throw new Error(`Delete failed: ${res.status}`)
  }

  async list(prefix = ''): Promise<StorageObject[]> {
    const url = `${getApiBase()}/api/mrl/files/list${prefix ? `?prefix=${encodeURIComponent(prefix)}` : ''}`
    const res = await fetch(url)
    if (!res.ok) throw new Error(`List failed: ${res.status}`)
    const json = await res.json() as { data: StorageObject[] }
    return json.data
  }

  async getPresignedUrl(
    key: string,
    expiresInSeconds = 3600
  ): Promise<string | null> {
    const res = await fetch(
      `${getApiBase()}/api/mrl/files/presign/${encodeURIComponent(key)}?expires=${expiresInSeconds}`
    )
    if (!res.ok) return null
    const json = await res.json() as { data?: { url?: string } }
    return json.data?.url ?? null
  }
}
