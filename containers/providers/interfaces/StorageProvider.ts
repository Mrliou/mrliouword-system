/**
 * StorageProvider interface
 * Origin Signature: MrLiouWord
 *
 * Abstraction for file/object storage backends.
 * Implementations: CloudflareR2StorageAdapter, MinIOStorageAdapter
 */

export interface UploadOptions {
  /** MIME type, e.g. 'text/plain', 'application/pdf' */
  contentType?: string
  /** Object metadata */
  meta?: Record<string, string>
}

export interface StorageObject {
  key: string
  size?: number
  contentType?: string
  uploadedAt?: string
  url?: string
  meta?: Record<string, string>
}

export interface StorageProvider {
  /**
   * Upload a file. Returns the stored object descriptor.
   */
  upload(
    key: string,
    data: Uint8Array | ReadableStream | string,
    options?: UploadOptions
  ): Promise<StorageObject>

  /**
   * Download a file. Returns raw bytes.
   */
  download(key: string): Promise<Uint8Array>

  /**
   * Delete an object.
   */
  delete(key: string): Promise<void>

  /**
   * List objects under a prefix.
   */
  list(prefix?: string): Promise<StorageObject[]>

  /**
   * Generate a pre-signed/temporary URL for direct client download.
   * Returns null if the backend does not support pre-signed URLs.
   */
  getPresignedUrl(key: string, expiresInSeconds?: number): Promise<string | null>
}
