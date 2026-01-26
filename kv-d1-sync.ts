/**
 * KV↔D1 Sync Engine v1.0.0 - Production-ready Single-file Closed Delivery
 * 
 * 核心規範：
 * - SoT: D1 為權威來源（白名單 prefix 除外）
 * - Monotonic Revision: rev 單調遞增，內容變更才 +1
 * - Idempotent: 同批重跑不增 rev、不重覆覆寫
 * - Resume: 可從 sync_state 續跑
 * - Observability: 每次同步寫 sync_runs
 * - Conflict Audit: 衝突必記 conflicts 表
 * 
 * @author MR.liou
 * @origin_signature MrLiouWord
 */

// ============================================================================
// 型別定義
// ============================================================================

export interface SyncConfig {
  /** 批次大小 (預設 100) */
  batch_size: number;
  /** KV 為權威的 prefix 白名單 */
  kv_authoritative_prefixes: string[];
  /** 衝突策略: latest_wins | d1_wins | kv_wins | manual */
  conflict_strategy: 'latest_wins' | 'd1_wins' | 'kv_wins' | 'manual';
  /** KV value 最大大小 (bytes) */
  kv_max_value_size: number;
  /** 是否啟用 inbox 模式 (推薦) */
  enable_inbox_mode: boolean;
}

export const DEFAULT_CONFIG: SyncConfig = {
  batch_size: 100,
  kv_authoritative_prefixes: ['cache:', 'session:', 'temp:'],
  conflict_strategy: 'latest_wins',
  kv_max_value_size: 25 * 1024 * 1024, // 25MB (Cloudflare KV limit)
  enable_inbox_mode: true,
};

/** KV Envelope 結構 */
export interface KVEnvelope<T = unknown> {
  rev: number;
  ts: number;
  checksum: string;
  source: 'kv' | 'd1' | 'api';
  payload: T;
}

/** 同步方向 */
export type SyncDirection = 'd1_to_kv' | 'kv_to_d1';

/** 錯誤分類 */
export type ErrorType = 'transient' | 'permanent' | 'data_conflict';

/** 同步錯誤 */
export interface SyncError {
  key: string;
  type: ErrorType;
  message: string;
  timestamp: number;
}

/** 同步運行結果 */
export interface SyncRunResult {
  run_id: string;
  direction: SyncDirection;
  started_at: number;
  finished_at: number;
  cursor_start: string | null;
  cursor_end: string | null;
  last_cursor_committed: string | null;
  scanned_count: number;
  applied_count: number;
  skipped_same_checksum_count: number;
  conflict_count: number;
  error_count: number;
  duration_ms: number;
  errors: SyncError[];
}

/** D1 record 結構 */
export interface D1Record {
  key: string;
  value: string;
  rev: number;
  checksum: string;
  updated_at: number;
}

/** Conflict 記錄 */
export interface ConflictRecord {
  conflict_id: string;
  run_id: string;
  key: string;
  d1_rev: number | null;
  kv_rev: number | null;
  d1_checksum: string | null;
  kv_checksum: string | null;
  d1_ts: number | null;
  kv_ts: number | null;
  chosen: 'd1' | 'kv' | 'none';
  strategy: string;
  reason: string;
  resolved_at: number | null;
}

/** Inbox 記錄 (用於 KV→D1 推送模式) */
export interface InboxRecord {
  inbox_id: string;
  key: string;
  action: 'put' | 'delete';
  envelope: string; // JSON serialized KVEnvelope
  created_at: number;
  processed_at: number | null;
  run_id: string | null;
}

// ============================================================================
// 工具函數
// ============================================================================

/**
 * 計算 checksum (SHA-256 hex)
 */
export async function computeChecksum(value: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(value);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * 產生 UUID v4
 */
export function generateUUID(): string {
  return crypto.randomUUID();
}

/**
 * 產生 run_id
 */
export function generateRunId(direction: SyncDirection): string {
  return `run_${direction}_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

/**
 * 產生 conflict_id
 */
export function generateConflictId(): string {
  return `conflict_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

/**
 * 產生 inbox_id
 */
export function generateInboxId(): string {
  return `inbox_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

/**
 * 封裝 KV Envelope
 */
export function wrapEnvelope<T>(
  payload: T,
  rev: number,
  source: 'kv' | 'd1' | 'api',
  checksum: string
): KVEnvelope<T> {
  return {
    rev,
    ts: Date.now(),
    checksum,
    source,
    payload,
  };
}

/**
 * 解析 KV Envelope
 */
export function unwrapEnvelope<T>(raw: string): KVEnvelope<T> | null {
  try {
    const parsed = JSON.parse(raw);
    if (
      typeof parsed.rev === 'number' &&
      typeof parsed.ts === 'number' &&
      typeof parsed.checksum === 'string' &&
      typeof parsed.source === 'string' &&
      'payload' in parsed
    ) {
      return parsed as KVEnvelope<T>;
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * 分類錯誤類型
 */
export function classifyError(error: unknown): ErrorType {
  const msg = error instanceof Error ? error.message : String(error);
  const lowerMsg = msg.toLowerCase();
  
  // Transient errors (可重試)
  if (
    lowerMsg.includes('timeout') ||
    lowerMsg.includes('rate limit') ||
    lowerMsg.includes('temporarily') ||
    lowerMsg.includes('503') ||
    lowerMsg.includes('429')
  ) {
    return 'transient';
  }
  
  // Data conflict
  if (
    lowerMsg.includes('conflict') ||
    lowerMsg.includes('constraint') ||
    lowerMsg.includes('duplicate')
  ) {
    return 'data_conflict';
  }
  
  // Permanent errors
  return 'permanent';
}

// ============================================================================
// SoT 判斷模組 (集中管理)
// ============================================================================

/**
 * 判斷指定 key 的 Source of Truth
 * 此函數為唯一權威判斷點，禁止在其他地方散落 SoT 邏輯
 */
export function determineSourceOfTruth(
  key: string,
  config: SyncConfig
): 'd1' | 'kv' {
  // 檢查是否在 KV 權威白名單中
  for (const prefix of config.kv_authoritative_prefixes) {
    if (key.startsWith(prefix)) {
      return 'kv';
    }
  }
  // 預設 D1 為權威
  return 'd1';
}

/**
 * 解決衝突：根據 SoT、rev、checksum、ts 決定勝出者
 */
export function resolveConflict(
  key: string,
  d1Record: { rev: number; checksum: string; ts: number } | null,
  kvEnvelope: { rev: number; checksum: string; ts: number } | null,
  config: SyncConfig
): { chosen: 'd1' | 'kv' | 'none'; reason: string } {
  const sot = determineSourceOfTruth(key, config);
  
  // 如果其中一方不存在
  if (!d1Record && !kvEnvelope) {
    return { chosen: 'none', reason: 'both_missing' };
  }
  if (!d1Record) {
    return { chosen: 'kv', reason: 'd1_missing' };
  }
  if (!kvEnvelope) {
    return { chosen: 'd1', reason: 'kv_missing' };
  }
  
  // Checksum 相同：無需同步
  if (d1Record.checksum === kvEnvelope.checksum) {
    return { chosen: 'none', reason: 'checksum_equal' };
  }
  
  // 強制策略
  if (config.conflict_strategy === 'd1_wins') {
    return { chosen: 'd1', reason: 'strategy_d1_wins' };
  }
  if (config.conflict_strategy === 'kv_wins') {
    return { chosen: 'kv', reason: 'strategy_kv_wins' };
  }
  if (config.conflict_strategy === 'manual') {
    return { chosen: 'none', reason: 'strategy_manual_required' };
  }
  
  // latest_wins 策略
  // 決策優先序：rev > checksum > ts
  if (d1Record.rev !== kvEnvelope.rev) {
    return d1Record.rev > kvEnvelope.rev
      ? { chosen: 'd1', reason: `rev_higher_d1:${d1Record.rev}>${kvEnvelope.rev}` }
      : { chosen: 'kv', reason: `rev_higher_kv:${kvEnvelope.rev}>${d1Record.rev}` };
  }
  
  // Rev 相同但 checksum 不同 = 真衝突
  // 使用 SoT 優先
  if (sot === 'kv') {
    return { chosen: 'kv', reason: `sot_kv_rev_equal` };
  }
  
  // 最後用 timestamp 輔助判斷
  if (d1Record.ts !== kvEnvelope.ts) {
    return d1Record.ts > kvEnvelope.ts
      ? { chosen: 'd1', reason: `ts_newer_d1:${d1Record.ts}>${kvEnvelope.ts}` }
      : { chosen: 'kv', reason: `ts_newer_kv:${kvEnvelope.ts}>${d1Record.ts}` };
  }
  
  // 完全無法判定，使用 SoT
  return { chosen: sot, reason: `sot_fallback_${sot}` };
}

// ============================================================================
// D1 操作模組
// ============================================================================

/**
 * 從 D1 讀取單筆記錄
 */
export async function getD1Record(
  db: D1Database,
  key: string
): Promise<D1Record | null> {
  const result = await db
    .prepare('SELECT key, value, rev, checksum, updated_at FROM records WHERE key = ?')
    .bind(key)
    .first<D1Record>();
  return result;
}

/**
 * 批次讀取 D1 記錄 (用於 d1_to_kv，支援 cursor 分頁)
 */
export async function batchGetD1Records(
  db: D1Database,
  cursor: number | null,
  batchSize: number,
  prefix?: string
): Promise<{ records: D1Record[]; nextCursor: number | null }> {
  const cursorValue = cursor ?? 0;
  
  let query: string;
  let stmt: D1PreparedStatement;
  
  if (prefix) {
    query = `
      SELECT key, value, rev, checksum, updated_at 
      FROM records 
      WHERE updated_at > ? AND key LIKE ?
      ORDER BY updated_at ASC
      LIMIT ?
    `;
    stmt = db.prepare(query).bind(cursorValue, `${prefix}%`, batchSize);
  } else {
    query = `
      SELECT key, value, rev, checksum, updated_at 
      FROM records 
      WHERE updated_at > ?
      ORDER BY updated_at ASC
      LIMIT ?
    `;
    stmt = db.prepare(query).bind(cursorValue, batchSize);
  }
  
  const result = await stmt.all<D1Record>();
  const records = result.results ?? [];
  
  // 計算下一個 cursor
  const nextCursor = records.length > 0 
    ? records[records.length - 1].updated_at 
    : null;
  
  return { records, nextCursor };
}

/**
 * 條件式更新 D1 記錄 (冪等)
 * 只有 checksum 不同時才更新，避免重跑 rev 重覆+1
 */
export async function upsertD1Record(
  db: D1Database,
  key: string,
  value: string,
  newChecksum: string,
  source: string
): Promise<{ action: 'inserted' | 'updated' | 'skipped'; newRev: number }> {
  const existing = await getD1Record(db, key);
  
  if (!existing) {
    // INSERT 新記錄
    const newRev = 1;
    await db
      .prepare(`
        INSERT INTO records (key, value, rev, checksum, updated_at)
        VALUES (?, ?, ?, ?, ?)
      `)
      .bind(key, value, newRev, newChecksum, Date.now())
      .run();
    return { action: 'inserted', newRev };
  }
  
  // Checksum 相同：跳過
  if (existing.checksum === newChecksum) {
    return { action: 'skipped', newRev: existing.rev };
  }
  
  // Checksum 不同：更新，rev+1
  const newRev = existing.rev + 1;
  await db
    .prepare(`
      UPDATE records 
      SET value = ?, rev = ?, checksum = ?, updated_at = ?
      WHERE key = ? AND checksum != ?
    `)
    .bind(value, newRev, newChecksum, Date.now(), key, newChecksum)
    .run();
  
  return { action: 'updated', newRev };
}

/**
 * 刪除 D1 記錄
 */
export async function deleteD1Record(db: D1Database, key: string): Promise<void> {
  await db.prepare('DELETE FROM records WHERE key = ?').bind(key).run();
}

// ============================================================================
// KV 操作模組
// ============================================================================

/**
 * 從 KV 讀取並解析 Envelope
 */
export async function getKVEnvelope<T = string>(
  kv: KVNamespace,
  key: string
): Promise<KVEnvelope<T> | null> {
  const raw = await kv.get(key);
  if (!raw) return null;
  return unwrapEnvelope<T>(raw);
}

/**
 * 寫入 KV (封裝為 Envelope)
 */
export async function putKVEnvelope<T>(
  kv: KVNamespace,
  key: string,
  payload: T,
  rev: number,
  source: 'kv' | 'd1' | 'api',
  config: SyncConfig
): Promise<void> {
  const payloadStr = typeof payload === 'string' ? payload : JSON.stringify(payload);
  const checksum = await computeChecksum(payloadStr);
  const envelope = wrapEnvelope(payload, rev, source, checksum);
  const envelopeStr = JSON.stringify(envelope);
  
  // 檢查大小限制
  if (envelopeStr.length > config.kv_max_value_size) {
    throw new Error(`KV value exceeds max size: ${envelopeStr.length} > ${config.kv_max_value_size}`);
  }
  
  await kv.put(key, envelopeStr);
}

/**
 * 刪除 KV 記錄
 */
export async function deleteKV(kv: KVNamespace, key: string): Promise<void> {
  await kv.delete(key);
}

// ============================================================================
// Inbox 模組 (KV→D1 推送模式)
// ============================================================================

/**
 * 寫入 Inbox (KV 寫入時同時呼叫)
 */
export async function writeToInbox(
  db: D1Database,
  key: string,
  action: 'put' | 'delete',
  envelope: KVEnvelope<unknown>
): Promise<string> {
  const inboxId = generateInboxId();
  await db
    .prepare(`
      INSERT INTO inbox (inbox_id, key, action, envelope, created_at, processed_at, run_id)
      VALUES (?, ?, ?, ?, ?, NULL, NULL)
    `)
    .bind(inboxId, key, action, JSON.stringify(envelope), Date.now())
    .run();
  return inboxId;
}

/**
 * 消費 Inbox (批次處理)
 */
export async function consumeInbox(
  db: D1Database,
  batchSize: number
): Promise<InboxRecord[]> {
  const result = await db
    .prepare(`
      SELECT inbox_id, key, action, envelope, created_at, processed_at, run_id
      FROM inbox
      WHERE processed_at IS NULL
      ORDER BY created_at ASC
      LIMIT ?
    `)
    .bind(batchSize)
    .all<InboxRecord>();
  return result.results ?? [];
}

/**
 * 標記 Inbox 已處理
 */
export async function markInboxProcessed(
  db: D1Database,
  inboxId: string,
  runId: string
): Promise<void> {
  await db
    .prepare(`
      UPDATE inbox 
      SET processed_at = ?, run_id = ?
      WHERE inbox_id = ?
    `)
    .bind(Date.now(), runId, inboxId)
    .run();
}

// ============================================================================
// Sync State 管理
// ============================================================================

/**
 * 讀取同步狀態 (cursor)
 */
export async function getSyncState(
  db: D1Database,
  direction: SyncDirection
): Promise<{ lastCursor: string | null; updatedAt: number | null }> {
  const result = await db
    .prepare('SELECT last_cursor_committed, updated_at FROM sync_state WHERE direction = ?')
    .bind(direction)
    .first<{ last_cursor_committed: string | null; updated_at: number }>();
  
  if (!result) {
    return { lastCursor: null, updatedAt: null };
  }
  return { lastCursor: result.last_cursor_committed, updatedAt: result.updated_at };
}

/**
 * 更新同步狀態
 */
export async function updateSyncState(
  db: D1Database,
  direction: SyncDirection,
  lastCursor: string
): Promise<void> {
  await db
    .prepare(`
      INSERT INTO sync_state (direction, last_cursor_committed, updated_at)
      VALUES (?, ?, ?)
      ON CONFLICT(direction) DO UPDATE SET
        last_cursor_committed = excluded.last_cursor_committed,
        updated_at = excluded.updated_at
    `)
    .bind(direction, lastCursor, Date.now())
    .run();
}

// ============================================================================
// Sync Runs 記錄
// ============================================================================

/**
 * 建立同步運行記錄
 */
export async function createSyncRun(
  db: D1Database,
  runId: string,
  direction: SyncDirection,
  cursorStart: string | null
): Promise<void> {
  await db
    .prepare(`
      INSERT INTO sync_runs (
        run_id, direction, started_at, finished_at,
        cursor_start, cursor_end, last_cursor_committed,
        scanned_count, applied_count, skipped_same_checksum_count,
        conflict_count, error_count, duration_ms
      ) VALUES (?, ?, ?, NULL, ?, NULL, NULL, 0, 0, 0, 0, 0, NULL)
    `)
    .bind(runId, direction, Date.now(), cursorStart)
    .run();
}

/**
 * 完成同步運行記錄
 */
export async function finishSyncRun(
  db: D1Database,
  result: SyncRunResult
): Promise<void> {
  await db
    .prepare(`
      UPDATE sync_runs SET
        finished_at = ?,
        cursor_end = ?,
        last_cursor_committed = ?,
        scanned_count = ?,
        applied_count = ?,
        skipped_same_checksum_count = ?,
        conflict_count = ?,
        error_count = ?,
        duration_ms = ?
      WHERE run_id = ?
    `)
    .bind(
      result.finished_at,
      result.cursor_end,
      result.last_cursor_committed,
      result.scanned_count,
      result.applied_count,
      result.skipped_same_checksum_count,
      result.conflict_count,
      result.error_count,
      result.duration_ms,
      result.run_id
    )
    .run();
}

// ============================================================================
// Conflict Audit 記錄
// ============================================================================

/**
 * 記錄衝突
 */
export async function recordConflict(
  db: D1Database,
  conflict: ConflictRecord
): Promise<void> {
  await db
    .prepare(`
      INSERT INTO conflicts (
        conflict_id, run_id, key,
        d1_rev, kv_rev, d1_checksum, kv_checksum, d1_ts, kv_ts,
        chosen, strategy, reason, resolved_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `)
    .bind(
      conflict.conflict_id,
      conflict.run_id,
      conflict.key,
      conflict.d1_rev,
      conflict.kv_rev,
      conflict.d1_checksum,
      conflict.kv_checksum,
      conflict.d1_ts,
      conflict.kv_ts,
      conflict.chosen,
      conflict.strategy,
      conflict.reason,
      conflict.resolved_at
    )
    .run();
}

// ============================================================================
// 核心同步函數
// ============================================================================

/**
 * D1 → KV 同步
 * SoT: D1 為權威，推送到 KV
 */
export async function syncD1ToKV(
  db: D1Database,
  kv: KVNamespace,
  config: SyncConfig = DEFAULT_CONFIG,
  prefix?: string
): Promise<SyncRunResult> {
  const direction: SyncDirection = 'd1_to_kv';
  const runId = generateRunId(direction);
  const startedAt = Date.now();
  
  // 取得上次 cursor
  const { lastCursor } = await getSyncState(db, direction);
  const cursorStart = lastCursor;
  
  // 建立 run 記錄
  await createSyncRun(db, runId, direction, cursorStart);
  
  const result: SyncRunResult = {
    run_id: runId,
    direction,
    started_at: startedAt,
    finished_at: 0,
    cursor_start: cursorStart,
    cursor_end: null,
    last_cursor_committed: null,
    scanned_count: 0,
    applied_count: 0,
    skipped_same_checksum_count: 0,
    conflict_count: 0,
    error_count: 0,
    duration_ms: 0,
    errors: [],
  };
  
  let currentCursor: number | null = cursorStart ? parseInt(cursorStart, 10) : null;
  let hasMore = true;
  
  while (hasMore) {
    const { records, nextCursor } = await batchGetD1Records(
      db,
      currentCursor,
      config.batch_size,
      prefix
    );
    
    result.scanned_count += records.length;
    
    for (const record of records) {
      try {
        // 判斷 SoT
        const sot = determineSourceOfTruth(record.key, config);
        
        // 如果 KV 是權威，跳過此 key (由 kv_to_d1 處理)
        if (sot === 'kv') {
          result.skipped_same_checksum_count++;
          continue;
        }
        
        // 讀取 KV 現有值
        const kvEnvelope = await getKVEnvelope<string>(kv, record.key);
        
        // 解決衝突
        const resolution = resolveConflict(
          record.key,
          { rev: record.rev, checksum: record.checksum, ts: record.updated_at },
          kvEnvelope ? { rev: kvEnvelope.rev, checksum: kvEnvelope.checksum, ts: kvEnvelope.ts } : null,
          config
        );
        
        // Checksum 相同，跳過
        if (resolution.reason === 'checksum_equal') {
          result.skipped_same_checksum_count++;
          continue;
        }
        
        // 記錄衝突 (如果 KV 有值且 checksum 不同)
        if (kvEnvelope && kvEnvelope.checksum !== record.checksum) {
          const conflictRecord: ConflictRecord = {
            conflict_id: generateConflictId(),
            run_id: runId,
            key: record.key,
            d1_rev: record.rev,
            kv_rev: kvEnvelope.rev,
            d1_checksum: record.checksum,
            kv_checksum: kvEnvelope.checksum,
            d1_ts: record.updated_at,
            kv_ts: kvEnvelope.ts,
            chosen: resolution.chosen === 'd1' ? 'd1' : resolution.chosen === 'kv' ? 'kv' : 'none',
            strategy: config.conflict_strategy,
            reason: resolution.reason,
            resolved_at: resolution.chosen !== 'none' ? Date.now() : null,
          };
          await recordConflict(db, conflictRecord);
          result.conflict_count++;
        }
        
        // 執行同步
        if (resolution.chosen === 'd1') {
          await putKVEnvelope(kv, record.key, record.value, record.rev, 'd1', config);
          result.applied_count++;
        }
        // KV wins 或 manual: 不覆寫 KV
        
      } catch (error) {
        const errType = classifyError(error);
        result.errors.push({
          key: record.key,
          type: errType,
          message: error instanceof Error ? error.message : String(error),
          timestamp: Date.now(),
        });
        result.error_count++;
        
        // Permanent error: 繼續處理下一筆
        // Transient error: 可考慮中斷，但這裡先繼續
      }
    }
    
    // 更新 cursor
    if (nextCursor !== null) {
      currentCursor = nextCursor;
      result.cursor_end = String(nextCursor);
      result.last_cursor_committed = String(nextCursor);
      await updateSyncState(db, direction, String(nextCursor));
    }
    
    // 判斷是否繼續
    hasMore = records.length >= config.batch_size && nextCursor !== null;
  }
  
  // 完成記錄
  result.finished_at = Date.now();
  result.duration_ms = result.finished_at - result.started_at;
  await finishSyncRun(db, result);
  
  return result;
}

/**
 * KV → D1 同步 (Inbox 模式)
 * 從 inbox 表消費變更，推送到 D1
 */
export async function syncKVToD1(
  db: D1Database,
  kv: KVNamespace,
  config: SyncConfig = DEFAULT_CONFIG
): Promise<SyncRunResult> {
  const direction: SyncDirection = 'kv_to_d1';
  const runId = generateRunId(direction);
  const startedAt = Date.now();
  
  // 取得上次 cursor (這裡用 inbox_id 作為 cursor)
  const { lastCursor } = await getSyncState(db, direction);
  const cursorStart = lastCursor;
  
  // 建立 run 記錄
  await createSyncRun(db, runId, direction, cursorStart);
  
  const result: SyncRunResult = {
    run_id: runId,
    direction,
    started_at: startedAt,
    finished_at: 0,
    cursor_start: cursorStart,
    cursor_end: null,
    last_cursor_committed: null,
    scanned_count: 0,
    applied_count: 0,
    skipped_same_checksum_count: 0,
    conflict_count: 0,
    error_count: 0,
    duration_ms: 0,
    errors: [],
  };
  
  // 消費 inbox
  const inboxRecords = await consumeInbox(db, config.batch_size);
  result.scanned_count = inboxRecords.length;
  
  for (const inbox of inboxRecords) {
    try {
      const envelope = unwrapEnvelope<string>(inbox.envelope);
      if (!envelope) {
        result.errors.push({
          key: inbox.key,
          type: 'permanent',
          message: 'Invalid envelope in inbox',
          timestamp: Date.now(),
        });
        result.error_count++;
        continue;
      }
      
      // 判斷 SoT
      const sot = determineSourceOfTruth(inbox.key, config);
      
      if (inbox.action === 'delete') {
        // 刪除操作
        await deleteD1Record(db, inbox.key);
        result.applied_count++;
      } else {
        // PUT 操作
        const d1Record = await getD1Record(db, inbox.key);
        
        // 解決衝突
        const resolution = resolveConflict(
          inbox.key,
          d1Record ? { rev: d1Record.rev, checksum: d1Record.checksum, ts: d1Record.updated_at } : null,
          { rev: envelope.rev, checksum: envelope.checksum, ts: envelope.ts },
          config
        );
        
        // Checksum 相同，跳過
        if (resolution.reason === 'checksum_equal') {
          result.skipped_same_checksum_count++;
          await markInboxProcessed(db, inbox.inbox_id, runId);
          continue;
        }
        
        // 記錄衝突
        if (d1Record && d1Record.checksum !== envelope.checksum) {
          const conflictRecord: ConflictRecord = {
            conflict_id: generateConflictId(),
            run_id: runId,
            key: inbox.key,
            d1_rev: d1Record.rev,
            kv_rev: envelope.rev,
            d1_checksum: d1Record.checksum,
            kv_checksum: envelope.checksum,
            d1_ts: d1Record.updated_at,
            kv_ts: envelope.ts,
            chosen: resolution.chosen === 'd1' ? 'd1' : resolution.chosen === 'kv' ? 'kv' : 'none',
            strategy: config.conflict_strategy,
            reason: resolution.reason,
            resolved_at: resolution.chosen !== 'none' ? Date.now() : null,
          };
          await recordConflict(db, conflictRecord);
          result.conflict_count++;
        }
        
        // 執行同步
        if (resolution.chosen === 'kv' || (sot === 'kv' && resolution.chosen !== 'd1')) {
          const payloadStr = typeof envelope.payload === 'string' 
            ? envelope.payload 
            : JSON.stringify(envelope.payload);
          const { action } = await upsertD1Record(db, inbox.key, payloadStr, envelope.checksum, 'kv');
          if (action !== 'skipped') {
            result.applied_count++;
          } else {
            result.skipped_same_checksum_count++;
          }
        } else if (resolution.chosen === 'd1') {
          // D1 wins，跳過
          result.skipped_same_checksum_count++;
        }
      }
      
      // 標記已處理
      await markInboxProcessed(db, inbox.inbox_id, runId);
      result.last_cursor_committed = inbox.inbox_id;
      
    } catch (error) {
      const errType = classifyError(error);
      result.errors.push({
        key: inbox.key,
        type: errType,
        message: error instanceof Error ? error.message : String(error),
        timestamp: Date.now(),
      });
      result.error_count++;
    }
  }
  
  // 更新 sync_state
  if (result.last_cursor_committed) {
    await updateSyncState(db, direction, result.last_cursor_committed);
  }
  
  // 完成記錄
  result.finished_at = Date.now();
  result.duration_ms = result.finished_at - result.started_at;
  result.cursor_end = result.last_cursor_committed;
  await finishSyncRun(db, result);
  
  return result;
}

/**
 * 雙向同步
 */
export async function bidirectionalSync(
  db: D1Database,
  kv: KVNamespace,
  config: SyncConfig = DEFAULT_CONFIG
): Promise<{ d1ToKv: SyncRunResult; kvToD1: SyncRunResult }> {
  // 先 D1 → KV (權威推送)
  const d1ToKv = await syncD1ToKV(db, kv, config);
  
  // 再 KV → D1 (inbox 消費)
  const kvToD1 = await syncKVToD1(db, kv, config);
  
  return { d1ToKv, kvToD1 };
}

// ============================================================================
// 輔助 API：供外部使用的包裝函數
// ============================================================================

/**
 * 寫入 KV 並同時記錄到 Inbox (推薦用法)
 */
export async function putWithInbox<T>(
  db: D1Database,
  kv: KVNamespace,
  key: string,
  payload: T,
  config: SyncConfig = DEFAULT_CONFIG
): Promise<{ inboxId: string; envelope: KVEnvelope<T> }> {
  const payloadStr = typeof payload === 'string' ? payload : JSON.stringify(payload);
  const checksum = await computeChecksum(payloadStr);
  
  // 讀取現有 envelope 以決定 rev
  const existing = await getKVEnvelope<T>(kv, key);
  const newRev = existing ? existing.rev + 1 : 1;
  
  // 封裝 envelope
  const envelope = wrapEnvelope(payload, newRev, 'api', checksum);
  
  // 寫入 KV
  const envelopeStr = JSON.stringify(envelope);
  if (envelopeStr.length > config.kv_max_value_size) {
    throw new Error(`KV value exceeds max size: ${envelopeStr.length} > ${config.kv_max_value_size}`);
  }
  await kv.put(key, envelopeStr);
  
  // 寫入 Inbox
  const inboxId = await writeToInbox(db, key, 'put', envelope as KVEnvelope<unknown>);
  
  return { inboxId, envelope };
}

/**
 * 刪除 KV 並同時記錄到 Inbox
 */
export async function deleteWithInbox(
  db: D1Database,
  kv: KVNamespace,
  key: string
): Promise<{ inboxId: string }> {
  // 讀取現有 envelope
  const existing = await getKVEnvelope(kv, key);
  const envelope = wrapEnvelope(null, existing ? existing.rev + 1 : 1, 'api', 'deleted');
  
  // 刪除 KV
  await kv.delete(key);
  
  // 寫入 Inbox
  const inboxId = await writeToInbox(db, key, 'delete', envelope);
  
  return { inboxId };
}

// ============================================================================
// Worker Entry Point (export default)
// ============================================================================

export interface Env {
  DB: D1Database;
  KV: KVNamespace;
  SYNC_CONFIG?: string; // JSON string of partial SyncConfig
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;
    
    // 解析配置
    let config: SyncConfig = { ...DEFAULT_CONFIG };
    if (env.SYNC_CONFIG) {
      try {
        const customConfig = JSON.parse(env.SYNC_CONFIG);
        config = { ...config, ...customConfig };
      } catch {
        // 忽略解析錯誤，使用預設配置
      }
    }
    
    // 路由
    try {
      // GET /health
      if (path === '/health' && request.method === 'GET') {
        return Response.json({ status: 'ok', timestamp: Date.now() });
      }
      
      // POST /sync/d1-to-kv
      if (path === '/sync/d1-to-kv' && request.method === 'POST') {
        const prefix = url.searchParams.get('prefix') ?? undefined;
        const result = await syncD1ToKV(env.DB, env.KV, config, prefix);
        return Response.json(result);
      }
      
      // POST /sync/kv-to-d1
      if (path === '/sync/kv-to-d1' && request.method === 'POST') {
        const result = await syncKVToD1(env.DB, env.KV, config);
        return Response.json(result);
      }
      
      // POST /sync/bidirectional
      if (path === '/sync/bidirectional' && request.method === 'POST') {
        const result = await bidirectionalSync(env.DB, env.KV, config);
        return Response.json(result);
      }
      
      // GET /sync/runs
      if (path === '/sync/runs' && request.method === 'GET') {
        const limit = parseInt(url.searchParams.get('limit') ?? '20', 10);
        const result = await env.DB
          .prepare('SELECT * FROM sync_runs ORDER BY started_at DESC LIMIT ?')
          .bind(limit)
          .all();
        return Response.json(result.results);
      }
      
      // GET /sync/runs/:run_id
      if (path.startsWith('/sync/runs/') && request.method === 'GET') {
        const runId = path.replace('/sync/runs/', '');
        const result = await env.DB
          .prepare('SELECT * FROM sync_runs WHERE run_id = ?')
          .bind(runId)
          .first();
        if (!result) {
          return Response.json({ error: 'Run not found' }, { status: 404 });
        }
        return Response.json(result);
      }
      
      // GET /sync/conflicts
      if (path === '/sync/conflicts' && request.method === 'GET') {
        const limit = parseInt(url.searchParams.get('limit') ?? '50', 10);
        const unresolvedOnly = url.searchParams.get('unresolved') === 'true';
        
        const query = unresolvedOnly
          ? 'SELECT * FROM conflicts WHERE resolved_at IS NULL ORDER BY conflict_id DESC LIMIT ?'
          : 'SELECT * FROM conflicts ORDER BY conflict_id DESC LIMIT ?';
        
        const result = await env.DB.prepare(query).bind(limit).all();
        return Response.json(result.results);
      }
      
      // GET /sync/state
      if (path === '/sync/state' && request.method === 'GET') {
        const result = await env.DB
          .prepare('SELECT * FROM sync_state')
          .all();
        return Response.json(result.results);
      }
      
      // PUT /kv/:key (寫入並記錄 inbox)
      if (path.startsWith('/kv/') && request.method === 'PUT') {
        const key = decodeURIComponent(path.replace('/kv/', ''));
        const body = await request.text();
        const { inboxId, envelope } = await putWithInbox(env.DB, env.KV, key, body, config);
        return Response.json({ inboxId, key, rev: envelope.rev, checksum: envelope.checksum });
      }
      
      // GET /kv/:key
      if (path.startsWith('/kv/') && request.method === 'GET') {
        const key = decodeURIComponent(path.replace('/kv/', ''));
        const envelope = await getKVEnvelope(env.KV, key);
        if (!envelope) {
          return Response.json({ error: 'Key not found' }, { status: 404 });
        }
        return Response.json(envelope);
      }
      
      // DELETE /kv/:key
      if (path.startsWith('/kv/') && request.method === 'DELETE') {
        const key = decodeURIComponent(path.replace('/kv/', ''));
        const { inboxId } = await deleteWithInbox(env.DB, env.KV, key);
        return Response.json({ inboxId, key, deleted: true });
      }
      
      // 404
      return Response.json({ error: 'Not found' }, { status: 404 });
      
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return Response.json({ error: message }, { status: 500 });
    }
  },
  
  // Scheduled handler (定時同步)
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext): Promise<void> {
    let config: SyncConfig = { ...DEFAULT_CONFIG };
    if (env.SYNC_CONFIG) {
      try {
        config = { ...config, ...JSON.parse(env.SYNC_CONFIG) };
      } catch {
        // 使用預設
      }
    }
    
    // 執行雙向同步
    ctx.waitUntil(bidirectionalSync(env.DB, env.KV, config));
  },
};
