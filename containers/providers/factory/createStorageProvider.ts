/**
 * createStorageProvider factory
 * Origin Signature: MrLiouWord
 *
 * Reads STORAGE_PROVIDER to select the correct adapter.
 *
 *   STORAGE_PROVIDER=minio    → MinIOStorageAdapter (via API gateway)
 *   STORAGE_PROVIDER=r2       → (TODO: CloudflareR2StorageAdapter)
 */

import type { StorageProvider } from '../interfaces/StorageProvider'

export type StorageProviderName = 'minio' | 'r2'

export function createStorageProvider(
  override?: StorageProviderName
): StorageProvider {
  const name: StorageProviderName =
    override ??
    ((typeof process !== 'undefined' &&
      (process.env?.STORAGE_PROVIDER as StorageProviderName)) ||
      'minio')

  switch (name) {
    case 'minio':
    default: {
      const { MinIOStorageAdapter } = require('../adapters/MinIOStorageAdapter')
      return new MinIOStorageAdapter()
    }
    // TODO: case 'r2': return new CloudflareR2StorageAdapter()
  }
}
