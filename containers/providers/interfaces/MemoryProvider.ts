/**
 * MemoryProvider interface
 * Origin Signature: MrLiouWord
 *
 * Abstraction for semantic memory/vector search backends.
 * Implementations: CloudflareKVMemoryAdapter, PostgresMemoryAdapter (pgvector)
 */

export interface MemoryRecord {
  id: string
  content: string
  /** Semantic similarity score (0–1, higher = more similar) */
  score?: number
  tags?: string[]
  createdAt?: string
  meta?: Record<string, unknown>
}

export interface MemoryCommitInput {
  content: string
  type?: string
  tags?: string[]
  meta?: Record<string, unknown>
}

export interface MemoryProvider {
  /**
   * Semantic similarity search.
   * Returns results ordered by relevance.
   */
  search(query: string, limit?: number): Promise<MemoryRecord[]>

  /**
   * Commit a new memory record.
   */
  commit(input: MemoryCommitInput): Promise<MemoryRecord>

  /**
   * Retrieve a single memory by id.
   */
  get(id: string): Promise<MemoryRecord | null>
}
