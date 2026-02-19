#!/bin/bash
# MrLiou AI Supercomputer - cURL Examples
# MrLiou AI 超級電腦 - cURL 指令範例
# 
# Philosophy: 怎麼過去，就怎麼回來 (How you go, so you return)

# Configuration
BASE_URL="http://127.0.0.1:8787"

echo "=================================================="
echo "MrLiou AI Supercomputer - cURL Examples"
echo "MrLiou AI 超級電腦 - cURL 指令範例"
echo "=================================================="
echo ""

# ========================================
# 1. Health Check / 健康檢查
# ========================================
echo "1. Health Check / 健康檢查"
echo "--------------------------------------------------"
echo "Command:"
echo "  curl ${BASE_URL}/health"
echo ""
echo "Response:"
curl -s ${BASE_URL}/health | python3 -m json.tool
echo ""
echo ""

# ========================================
# 2. List Providers / 列出提供者
# ========================================
echo "2. List Providers / 列出提供者"
echo "--------------------------------------------------"
echo "Command:"
echo "  curl ${BASE_URL}/ai/providers"
echo ""
echo "Response:"
curl -s ${BASE_URL}/ai/providers | python3 -m json.tool
echo ""
echo ""

# ========================================
# 3. AI Completion (OpenAI) / AI 完成 (OpenAI)
# ========================================
echo "3. AI Completion (OpenAI) / AI 完成 (OpenAI)"
echo "--------------------------------------------------"
echo "Command:"
cat << 'EOF'
curl -X POST http://127.0.0.1:8787/ai/complete \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is 2+2? Answer in one sentence.",
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "max_tokens": 50,
    "temperature": 0.7
  }'
EOF
echo ""
echo "Response:"
curl -s -X POST ${BASE_URL}/ai/complete \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is 2+2? Answer in one sentence.",
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "max_tokens": 50,
    "temperature": 0.7
  }' 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "⚠️  OpenAI not configured or unavailable"
echo ""
echo ""

# ========================================
# 4. AI Completion (Claude) / AI 完成 (Claude)
# ========================================
echo "4. AI Completion (Claude) / AI 完成 (Claude)"
echo "--------------------------------------------------"
echo "Command:"
cat << 'EOF'
curl -X POST http://127.0.0.1:8787/ai/complete \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in one sentence.",
    "provider": "claude",
    "model": "claude-3-haiku-20240307",
    "max_tokens": 100
  }'
EOF
echo ""
echo "Response:"
curl -s -X POST ${BASE_URL}/ai/complete \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in one sentence.",
    "provider": "claude",
    "model": "claude-3-haiku-20240307",
    "max_tokens": 100
  }' 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "⚠️  Claude not configured or unavailable"
echo ""
echo ""

# ========================================
# 5. AI Completion (Gemini) / AI 完成 (Gemini)
# ========================================
echo "5. AI Completion (Gemini) / AI 完成 (Gemini)"
echo "--------------------------------------------------"
echo "Command:"
cat << 'EOF'
curl -X POST http://127.0.0.1:8787/ai/complete \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is the capital of France?",
    "provider": "gemini",
    "max_tokens": 50
  }'
EOF
echo ""
echo "Response:"
curl -s -X POST ${BASE_URL}/ai/complete \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is the capital of France?",
    "provider": "gemini",
    "max_tokens": 50
  }' 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "⚠️  Gemini not configured or unavailable"
echo ""
echo ""

# ========================================
# 6. AI Completion (Ollama) / AI 完成 (Ollama)
# ========================================
echo "6. AI Completion (Ollama - Local) / AI 完成 (Ollama - 本地)"
echo "--------------------------------------------------"
echo "Command:"
cat << 'EOF'
curl -X POST http://127.0.0.1:8787/ai/complete \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Say hello in one word.",
    "provider": "ollama",
    "model": "llama2",
    "max_tokens": 10
  }'
EOF
echo ""
echo "Response:"
curl -s -X POST ${BASE_URL}/ai/complete \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Say hello in one word.",
    "provider": "ollama",
    "model": "llama2",
    "max_tokens": 10
  }' 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "⚠️  Ollama not running or unavailable"
echo ""
echo ""

# ========================================
# 7. AI Streaming (Ollama) / AI 串流 (Ollama)
# ========================================
echo "7. AI Streaming (Ollama) / AI 串流 (Ollama)"
echo "--------------------------------------------------"
echo "Command:"
cat << 'EOF'
curl -X POST http://127.0.0.1:8787/ai/stream \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Count from 1 to 5",
    "provider": "ollama",
    "max_tokens": 50
  }'
EOF
echo ""
echo "Response (streaming):"
curl -s -X POST ${BASE_URL}/ai/stream \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Count from 1 to 5",
    "provider": "ollama",
    "max_tokens": 50
  }' 2>/dev/null || echo "⚠️  Ollama not running or unavailable"
echo ""
echo ""

# ========================================
# 8. Default Provider / 預設提供者
# ========================================
echo "8. Default Provider (no provider specified) / 預設提供者（未指定提供者）"
echo "--------------------------------------------------"
echo "Command:"
cat << 'EOF'
curl -X POST http://127.0.0.1:8787/ai/complete \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, AI!",
    "max_tokens": 20
  }'
EOF
echo ""
echo "Response:"
curl -s -X POST ${BASE_URL}/ai/complete \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, AI!",
    "max_tokens": 20
  }' 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "⚠️  No providers available"
echo ""
echo ""

# ========================================
# Summary
# ========================================
echo "=================================================="
echo "Examples Complete / 範例完成"
echo "=================================================="
echo ""
echo "✓ All cURL examples demonstrated"
echo "✓ 所有 cURL 範例已展示"
echo ""
echo "Notes / 注意事項:"
echo "  • Ensure server is running: python3 flowcore_loop.py"
echo "  • 確保伺服器正在運行: python3 flowcore_loop.py"
echo "  • Configure API keys in .env file"
echo "  • 在 .env 檔案中配置 API 金鑰"
echo "  • Check logs: log/trace.jsonl, log/ai_costs.jsonl"
echo "  • 檢查日誌: log/trace.jsonl, log/ai_costs.jsonl"
echo ""
echo "Philosophy: 怎麼過去，就怎麼回來"
echo "(How you go, so you return)"
echo ""
