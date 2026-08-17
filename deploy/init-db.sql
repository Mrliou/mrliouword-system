-- MrLiouWord PostgreSQL 初始化腳本
-- Origin Signature: MrLiouWord
-- 執行於容器首次啟動時

-- 啟用 pgvector 擴充
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 使用者資料表
CREATE TABLE IF NOT EXISTS users (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    uid         TEXT UNIQUE NOT NULL,   -- 對應 auth provider uid
    email       TEXT,
    display_name TEXT,
    provider    TEXT NOT NULL DEFAULT 'firebase',  -- 'firebase' | 'authentik'
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- UI 偏好/狀態
CREATE TABLE IF NOT EXISTS ui_preferences (
    user_id     TEXT PRIMARY KEY,
    theme       TEXT DEFAULT 'system',
    language    TEXT DEFAULT 'zh-TW',
    sidebar_open BOOLEAN DEFAULT true,
    preferences JSONB DEFAULT '{}',
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 記憶文件
CREATE TABLE IF NOT EXISTS memory_documents (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content     TEXT NOT NULL,
    type        TEXT DEFAULT 'semantic',
    tags        TEXT[] DEFAULT '{}',
    simhash     TEXT,
    merkle      TEXT,
    embedding   VECTOR(1536),          -- pgvector 欄位，調整維度以符合模型
    meta        JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 向量相似度索引
CREATE INDEX IF NOT EXISTS memory_embedding_idx
    ON memory_documents USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- 審計事件記錄
CREATE TABLE IF NOT EXISTS audit_events (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type  TEXT NOT NULL,
    user_id     TEXT,
    resource    TEXT,
    action      TEXT,
    status      TEXT,
    meta        JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 工具執行記錄
CREATE TABLE IF NOT EXISTS tool_calls (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tool_name   TEXT NOT NULL,
    user_id     TEXT,
    input       JSONB DEFAULT '{}',
    output      JSONB DEFAULT '{}',
    status      TEXT DEFAULT 'pending',
    error       TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- 對話線程
CREATE TABLE IF NOT EXISTS chat_threads (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     TEXT NOT NULL,
    title       TEXT,
    model       TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 對話訊息
CREATE TABLE IF NOT EXISTS chat_messages (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    thread_id   UUID NOT NULL REFERENCES chat_threads(id) ON DELETE CASCADE,
    role        TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content     TEXT NOT NULL,
    meta        JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS chat_messages_thread_idx ON chat_messages(thread_id);
