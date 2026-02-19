# MrLiou AI Supercomputer - Quick Start Guide
# MrLiou AI 超級電腦 - 快速入門指南

> **Philosophy / 哲學**: 怎麼過去，就怎麼回來 (How you go, so you return)

---

## Overview / 概要

The MrLiou AI Supercomputer provides a unified HTTP API for accessing multiple AI providers with built-in audit trails, cost tracking, and fallback support.

MrLiou AI 超級電腦提供統一的 HTTP API 來訪問多個 AI 提供者，內建審計追蹤、成本追蹤和備用支援。

**Key Features / 主要特性**:
- ✅ Multi-provider support (OpenAI, Claude, Gemini, Ollama, Azure)
- ✅ Zero external dependencies (pure Python stdlib)
- ✅ Merkle chain audit trail
- ✅ Automatic cost tracking
- ✅ Response snapshotting (reversibility)
- ✅ Fallback mechanism
- ✅ Streaming support (SSE)

---

## Quick Start / 快速開始

### 1. Install Dependencies / 安裝依賴

```bash
# Python 3.7+ required
python3 --version

# No external packages needed!
# 無需外部套件！
```

### 2. Configure API Keys / 配置 API 金鑰

```bash
# Copy environment template
cp config/env_template.txt .env

# Edit .env and add your keys
nano .env
```

**Example .env**:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

### 3. Load Environment / 載入環境

**Linux/Mac**:
```bash
export $(cat .env | xargs)
```

**Windows**:
```powershell
Get-Content .env | ForEach-Object { 
    $var = $_.Split('='); 
    [Environment]::SetEnvironmentVariable($var[0], $var[1]) 
}
```

### 4. Start Server / 啟動伺服器

```bash
# Method 1: Using run script
chmod +x run.sh
./run.sh

# Method 2: Direct execution
python3 flowcore_loop.py

# Method 3: With custom port
PORT=8888 python3 flowcore_loop.py
```

### 5. Test Server / 測試伺服器

```bash
# Health check
curl http://127.0.0.1:8787/health

# List providers
curl http://127.0.0.1:8787/ai/providers

# Test completion
curl -X POST http://127.0.0.1:8787/ai/complete \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, AI!", "max_tokens": 20}'
```

---

## API Endpoints / API 端點

### GET /health

Health check endpoint.

**Response**:
```json
{
  "status": "ok",
  "merkle_root": "abc123...",
  "trace_count": 42
}
```

### GET /ai/providers

List all available AI providers.

**Response**:
```json
{
  "providers": [
    {
      "name": "openai",
      "enabled": true,
      "available": true,
      "models": ["gpt-4", "gpt-3.5-turbo"]
    }
  ],
  "default": "openai",
  "fallback_enabled": true
}
```

### POST /ai/complete

Synchronous AI completion.

**Request**:
```json
{
  "prompt": "Explain quantum computing",
  "provider": "openai",          // Optional, uses default if not specified
  "model": "gpt-3.5-turbo",      // Optional
  "max_tokens": 1000,            // Optional, default: 1000
  "temperature": 0.7             // Optional, default: 0.7
}
```

**Response**:
```json
{
  "response": "Quantum computing is...",
  "metadata": {
    "request_id": "req_1234567890",
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "usage": {
      "input_tokens": 50,
      "output_tokens": 200,
      "total_tokens": 250
    },
    "cost_usd": 0.00050,
    "merkle_root": "abc123..."
  }
}
```

### POST /ai/stream

Streaming AI completion using Server-Sent Events (SSE).

**Request**:
```json
{
  "prompt": "Count to 10",
  "provider": "ollama",
  "max_tokens": 100
}
```

**Response** (text/event-stream):
```
data: {"chunk":"1"}
data: {"chunk":" 2"}
data: {"chunk":" 3"}
...
data: [DONE]
```

---

## Configuration / 配置

### Provider Configuration / 提供者配置

Edit `config/ai_providers.json`:

```json
{
  "default_provider": "openai",
  "providers": [
    {
      "name": "openai",
      "enabled": true,
      "api_key": "${OPENAI_API_KEY}",
      "default_model": "gpt-3.5-turbo"
    }
  ],
  "fallback": {
    "enabled": true,
    "order": ["openai", "claude", "ollama"]
  }
}
```

### Environment Variables / 環境變數

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | For OpenAI |
| `ANTHROPIC_API_KEY` | Anthropic API key | For Claude |
| `GOOGLE_API_KEY` | Google API key | For Gemini |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI key | For Azure |
| `AZURE_OPENAI_ENDPOINT` | Azure endpoint URL | For Azure |
| `AZURE_OPENAI_DEPLOYMENT` | Azure deployment name | For Azure |
| `PORT` | Server port | Optional (default: 8787) |

---

## Judge Loop Pattern / 評判循環模式

All AI operations follow the Judge Loop pattern for full audit trail:

```
1. Pre-trace Emission
   └─→ Log request to Merkle chain
   
2. Provider Execution
   └─→ Execute with fallback support
   
3. Response Snapshot
   └─→ Save to memory/ingest/ai_responses/
   
4. Cost Calculation
   └─→ Log to log/ai_costs.jsonl
   
5. Post-trace Emission
   └─→ Log completion to Merkle chain
```

### Audit Files / 審計檔案

**Merkle Chain** (`log/trace.jsonl`):
```json
{
  "timestamp": "2026-02-18T12:00:00Z",
  "trace_id": 1,
  "event_type": "ai_complete_pre",
  "data": {...},
  "merkle_root": "abc123..."
}
```

**Cost Tracking** (`log/ai_costs.jsonl`):
```json
{
  "timestamp": "2026-02-18T12:00:00Z",
  "provider": "openai",
  "model": "gpt-3.5-turbo",
  "total_tokens": 250,
  "estimated_cost_usd": 0.00050
}
```

**Response Snapshots** (`memory/ingest/ai_responses/`):
- Files: `response_YYYYMMDD_HHMMSS_microseconds.json`
- Purpose: Reversibility guarantee

---

## Local Development / 本地開發

### Run Tests / 運行測試

```bash
# Full integration test suite
python3 test_ai_supercomputer.py

# Expected output:
# Results: 7/7 tests passed ✅
```

### Demo Script / 演示腳本

```bash
# Interactive demonstration
python3 demo_ai_providers.py
```

### cURL Examples / cURL 範例

```bash
# Run all examples
chmod +x examples_curl.sh
./examples_curl.sh
```

---

## Ollama Setup / Ollama 設定

For local model execution:

```bash
# 1. Install Ollama
# Visit: https://ollama.ai

# 2. Start Ollama service
ollama serve

# 3. Pull a model
ollama pull llama2

# 4. Test
curl http://localhost:11434/api/tags
```

---

## Cost Monitoring / 成本監控

### View Cost Log / 查看成本日誌

```bash
# View all costs
cat log/ai_costs.jsonl | python3 -m json.tool

# Calculate total cost
cat log/ai_costs.jsonl | \
  python3 -c "import sys, json; print(sum(json.loads(l)['estimated_cost_usd'] for l in sys.stdin))"
```

### Pricing (approximate) / 定價（約）

| Provider | Model | Per 1M Input | Per 1M Output |
|----------|-------|--------------|---------------|
| OpenAI | GPT-4 | $30 | $60 |
| OpenAI | GPT-3.5 | $0.50 | $1.50 |
| Claude | Opus | $15 | $75 |
| Claude | Sonnet | $3 | $15 |
| Claude | Haiku | $0.25 | $1.25 |
| Gemini | Pro | $0.50 | $1.50 |
| Ollama | All | **FREE** | **FREE** |

---

## Troubleshooting / 故障排除

### Problem: "No providers available"

**Solution**:
1. Check API keys are set: `echo $OPENAI_API_KEY`
2. Verify config: `cat config/ai_providers.json`
3. Test provider: `curl http://127.0.0.1:8787/ai/providers`

### Problem: "Connection refused"

**Solution**:
1. Check if server is running: `ps aux | grep flowcore_loop`
2. Check port: `netstat -an | grep 8787`
3. Start server: `python3 flowcore_loop.py`

### Problem: "Ollama not responding"

**Solution**:
```bash
# Check Ollama status
ollama list

# Start Ollama
ollama serve

# Test Ollama
curl http://localhost:11434/api/tags
```

### Problem: "Import error"

**Solution**:
```bash
# Ensure files are in place
ls -la ai_providers.py flowcore_loop.py

# Check Python version
python3 --version  # Should be 3.7+

# Run from correct directory
cd /path/to/mrliouword-system
python3 flowcore_loop.py
```

---

## Architecture / 架構

```
HTTP Client
    ↓
FlowCore Loop (HTTP Server)
    ↓
judge_ai_complete() [Judge Loop Pattern]
    ├─→ Pre-trace (Merkle chain)
    ├─→ AIProviderManager
    │   ├─→ OpenAI
    │   ├─→ Claude
    │   ├─→ Gemini
    │   ├─→ Ollama
    │   └─→ Azure
    ├─→ Response Snapshot
    ├─→ Cost Tracking
    └─→ Post-trace (Merkle chain)
```

---

## Security Best Practices / 安全最佳實踐

1. ✅ **Never commit** `.env` files to Git
2. ✅ **Use environment variables** for all secrets
3. ✅ **Rotate API keys** regularly
4. ✅ **Monitor costs** via `log/ai_costs.jsonl`
5. ✅ **Review audit trail** in `log/trace.jsonl`
6. ✅ **Limit max_tokens** to prevent runaway costs
7. ✅ **Use fallback** for production reliability

---

## Support / 支援

- **Documentation**: `AI_PROVIDERS_README.md`
- **GitHub**: [dofaromg/mrliouword-system](https://github.com/dofaromg/mrliouword-system)
- **Issues**: GitHub Issues
- **Tests**: `python3 test_ai_supercomputer.py`

---

## Philosophy / 哲學

> **怎麼過去，就怎麼回來**  
> *How you go, so you return*

Every AI operation is:
- **Tracked** (Merkle chain)
- **Reversible** (Response snapshots)
- **Auditable** (Complete logs)
- **Transparent** (Cost tracking)

---

**Version**: 1.0.0  
**Author**: MR.liou & Claude  
**Updated**: 2026-02-18
