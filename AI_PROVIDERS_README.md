# MrLiou AI Providers - Multi-Provider AI Support
# MrLiou AI 提供者 - 多提供者人工智慧支持

> **Philosophy / 哲學**: 怎麼過去，就怎麼回來 (How you go, so you return)

---

## Overview / 概要

The MrLiou AI Supercomputer provides a unified abstraction layer for multiple AI providers, enabling seamless integration with various AI services while maintaining the Judge Loop pattern and Merkle chain audit trail.

MrLiou AI 超級電腦透過統一的抽象層支援多個 AI 供應商，實現了與各種 AI 服務的無縫集成，同時保持了 Judge Loop 模式和 Merkle 鏈審計追蹤。

**Zero External Dependencies** / **零外部依賴**: Pure Python standard library only

---

## Supported Providers / 支援的供應商

| Provider | Status | Features |
|----------|--------|----------|
| OpenAI | ✅ | GPT-4, GPT-3.5, Streaming, Chat API |
| Claude | ✅ | Claude 3 Opus/Sonnet/Haiku, Streaming |
| Gemini | ✅ | Gemini Pro, Streaming |
| Ollama | ✅ | Local models, Streaming |
| Azure OpenAI | ✅ | Custom endpoints, GPT models |

---

## Installation / 安裝

### 1. Prerequisites / 先決條件

```bash
# Python 3.7+ required
python3 --version

# For Ollama (optional)
# Install from: https://ollama.ai
ollama --version
```

### 2. Configuration / 配置

```bash
# Copy environment template
cp config/env_template.txt .env

# Edit .env and add your API keys
# 編輯 .env 並新增您的 API 金鑰
nano .env
```

**.env example**:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

### 3. Load Environment Variables / 載入環境變數

**Linux/Mac**:
```bash
export $(cat .env | xargs)
```

**Windows PowerShell**:
```powershell
Get-Content .env | ForEach-Object { 
    $var = $_.Split('='); 
    [Environment]::SetEnvironmentVariable($var[0], $var[1]) 
}
```

### 4. Start Server / 啟動伺服器

```bash
# Using run script
./run.sh

# Or directly
python3 flowcore_loop.py
```

---

## API Reference / API 參考

### Endpoints / 端點

#### 1. List Providers / 列出提供者

```http
GET /ai/providers
```

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

#### 2. Synchronous Completion / 同步完成

```http
POST /ai/complete
Content-Type: application/json

{
  "prompt": "Explain quantum computing",
  "provider": "openai",
  "model": "gpt-3.5-turbo",
  "max_tokens": 1000,
  "temperature": 0.7
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

#### 3. Streaming Completion / 串流完成

```http
POST /ai/stream
Content-Type: application/json

{
  "prompt": "Count to 10",
  "provider": "ollama"
}
```

**Response** (Server-Sent Events):
```
data: {"chunk":"1"}
data: {"chunk":" 2"}
data: {"chunk":" 3"}
...
data: [DONE]
```

---

## Usage Examples / 使用範例

### Python SDK

```python
from ai_providers import AIProviderManager

# Initialize manager
manager = AIProviderManager("config/ai_providers.json")

# List available providers
providers = manager.list_providers()
for p in providers:
    print(f"{p['name']}: {'✓' if p['available'] else '✗'}")

# Complete (synchronous)
result = manager.complete(
    "Explain quantum computing",
    provider="openai",
    model="gpt-3.5-turbo",
    max_tokens=1000
)
print(result["text"])

# Stream
for chunk in manager.stream("Count to 10", provider="ollama"):
    print(chunk, end="", flush=True)
```

### cURL Examples / cURL 範例

**List providers**:
```bash
curl http://127.0.0.1:8787/ai/providers
```

**Complete**:
```bash
curl -X POST http://127.0.0.1:8787/ai/complete \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing",
    "provider": "openai",
    "max_tokens": 500
  }'
```

**Stream**:
```bash
curl -X POST http://127.0.0.1:8787/ai/stream \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Count to 10",
    "provider": "ollama"
  }'
```

---

## Judge Loop Pattern / 評判循環模式

All AI operations follow the Judge Loop pattern:

所有人工智慧操作都遵循判斷循環模式：

```
1. Pre-trace emission   → Merkle chain logging
2. Provider execution   → With fallback support
3. Response snapshot    → Reversibility guarantee
4. Cost calculation     → Token usage tracking
5. Post-trace emission  → Complete audit trail
```

### Audit Trail / 審計追蹤

**Trace Log** (`log/trace.jsonl`):
```json
{
  "timestamp": "2026-02-18T12:00:00.000Z",
  "trace_id": 1,
  "event_type": "ai_complete_pre",
  "data": {"request_id": "req_123", "prompt": "..."},
  "merkle_root": "abc123..."
}
```

**Cost Log** (`log/ai_costs.jsonl`):
```json
{
  "timestamp": "2026-02-18T12:00:00.000Z",
  "provider": "openai",
  "model": "gpt-3.5-turbo",
  "input_tokens": 50,
  "output_tokens": 200,
  "total_tokens": 250,
  "estimated_cost_usd": 0.00050
}
```

**Response Snapshots** (`memory/ingest/ai_responses/`):
```json
{
  "timestamp": "2026-02-18T12:00:00.000Z",
  "response": "Quantum computing is...",
  "metadata": {
    "request_id": "req_123",
    "provider": "openai",
    "model": "gpt-3.5-turbo"
  }
}
```

---

## Fallback Mechanism / 備用機轉

When a provider is unavailable, the system automatically falls back to the next available provider:

當提供者不可用時，系統會自動故障轉移到下一個可用的提供者：

```json
{
  "fallback": {
    "enabled": true,
    "order": ["openai", "claude", "ollama"]
  }
}
```

**Example flow**:
1. Request OpenAI → Unavailable
2. Fall back to Claude → Unavailable
3. Fall back to Ollama → Success ✓

---

## Cost Tracking / 成本追蹤

Token pricing per 1M tokens (approximate):

| Provider | Model | Input | Output |
|----------|-------|-------|--------|
| OpenAI | GPT-4 | $30 | $60 |
| OpenAI | GPT-3.5 | $0.5 | $1.5 |
| Claude | Opus | $15 | $75 |
| Claude | Sonnet | $3 | $15 |
| Claude | Haiku | $0.25 | $1.25 |
| Gemini | Pro | $0.5 | $1.5 |
| Ollama | All | $0 | $0 (local) |

---

## Troubleshooting / 故障排除

### Problem: Provider not available / 問題：提供者不可用

**Solution**:
1. Check API key is set correctly
2. Verify network connectivity
3. Check provider status page

```bash
# Test provider availability
curl http://127.0.0.1:8787/ai/providers
```

### Problem: Ollama not responding / 問題：Ollama 無回應

**Solution**:
```bash
# Start Ollama service
ollama serve

# Pull a model
ollama pull llama2

# Test
curl http://localhost:11434/api/tags
```

### Problem: Import errors / 問題：匯入錯誤

**Solution**:
```bash
# Ensure ai_providers.py is in the same directory
ls -la ai_providers.py

# Check Python path
python3 -c "import sys; print(sys.path)"
```

---

## Architecture / 架構

```
┌─────────────────────────────────────────────────────────┐
│                   HTTP Endpoints                        │
│  /ai/complete  /ai/stream  /ai/providers               │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│              judge_ai_complete()                        │
│  • Pre-trace emission                                   │
│  • Provider selection with fallback                     │
│  • Response snapshotting                                │
│  • Cost tracking                                        │
│  • Post-trace emission                                  │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│            AIProviderManager                            │
│  • Configuration management                             │
│  • Provider registry                                    │
│  • Fallback orchestration                               │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│              Concrete Providers                         │
│  OpenAI │ Claude │ Gemini │ Ollama │ Azure             │
└─────────────────────────────────────────────────────────┘
```

---

## Testing / 測試

```bash
# Run integration tests
python3 test_ai_supercomputer.py

# Expected output:
# Results: 7/7 tests passed ✅
```

---

## Best Practices / 最佳實踐

1. **Always use environment variables** for API keys / 始終使用環境變數存儲 API 金鑰
2. **Enable fallback** for production / 在生產環境中啟用備用機制
3. **Monitor costs** via `log/ai_costs.jsonl` / 透過成本日誌監控費用
4. **Audit operations** via `log/trace.jsonl` / 透過追蹤日誌審計操作
5. **Snapshot responses** before returning / 在返回前快照回應（可逆性）

---

## License / 授權

MR.liou © 2026

**Philosophy**: 怎麼過去，就怎麼回來 (How you go, so you return)

---

## Support / 支援

For issues and questions:
- GitHub Issues: [dofaromg/mrliouword-system](https://github.com/dofaromg/mrliouword-system)
- Documentation: `docs/SUPERCOMPUTER_QUICKSTART.md`

---

**Version**: 1.0.0  
**Last Updated**: 2026-02-18
