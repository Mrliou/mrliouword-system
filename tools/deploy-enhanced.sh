#!/bin/bash
# Particle Edge v4.0.0 一鍵部署腳本
# 包含前置檢查、部署、驗證
#
# origin_signature: MrLiouWord
# philosophy: 怎麼過去，就怎麼回來
# version: 4.0.0

set -e

echo "🌀 Particle Edge v4.0.0 部署腳本"
echo "=================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# 1. 前置檢查
check_prerequisites() {
  echo "[1/5] 檢查前置條件..."
  
  # 檢查 Node.js
  if ! command -v node &> /dev/null; then
    echo "❌ 未安裝 Node.js，請先安裝 v18 或更高版本"
    echo "   訪問 https://nodejs.org/ 下載安裝"
    exit 1
  fi
  
  NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
  if [ "$NODE_VERSION" -lt 18 ]; then
    echo "⚠️  Node.js 版本過低 (當前: v$NODE_VERSION)"
    echo "   建議升級到 v18 或更高版本"
  else
    echo "✓ Node.js 版本: $(node -v)"
  fi
  
  # 檢查 Wrangler
  if ! command -v wrangler &> /dev/null; then
    echo "⚠️  未找到 wrangler，正在安裝..."
    npm install -g wrangler
    if [ $? -ne 0 ]; then
      echo "❌ Wrangler 安裝失敗"
      exit 1
    fi
    echo "✓ Wrangler 安裝成功"
  else
    echo "✓ Wrangler 版本: $(wrangler --version)"
  fi
  
  # 檢查登入狀態
  if ! wrangler whoami &> /dev/null; then
    echo "⚠️  請先登入 Cloudflare:"
    wrangler login
    if [ $? -ne 0 ]; then
      echo "❌ Cloudflare 登入失敗"
      exit 1
    fi
  else
    echo "✓ Cloudflare 已登入: $(wrangler whoami 2>/dev/null | head -n 1)"
  fi
  
  echo "✅ 前置條件檢查完成"
  echo ""
}

# 2. 安裝依賴
install_deps() {
  echo "[2/5] 安裝依賴..."
  
  if [ ! -d "$ROOT_DIR/cloudflare/mrliouword-private" ]; then
    echo "❌ 找不到 Worker 目錄: $ROOT_DIR/cloudflare/mrliouword-private"
    exit 1
  fi
  
  cd "$ROOT_DIR/cloudflare/mrliouword-private"
  
  if [ ! -f "package.json" ]; then
    echo "⚠️  找不到 package.json，初始化..."
    npm init -y
    npm install wrangler --save-dev
  else
    echo "安裝 npm 依賴..."
    npm install
    if [ $? -ne 0 ]; then
      echo "❌ 依賴安裝失敗"
      exit 1
    fi
  fi
  
  cd "$ROOT_DIR"
  echo "✅ 依賴安裝完成"
  echo ""
}

# 3. 本地測試（可選）
local_test() {
  echo "[3/5] 本地測試階段"
  read -p "是否進行本地測試？(y/N) " -n 1 -r
  echo
  
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "啟動本地開發服務器..."
    cd "$ROOT_DIR/cloudflare/mrliouword-private"
    
    # 在後台啟動開發服務器
    npm run dev &
    DEV_PID=$!
    
    echo "測試服務器正在運行 (PID: $DEV_PID)"
    echo "等待服務器啟動..."
    sleep 5
    
    # 測試端點
    echo ""
    echo "測試端點："
    echo "1. 根端點: http://localhost:8787/"
    echo "2. 狀態端點: http://localhost:8787/status"
    echo "3. 頻率端點: http://localhost:8787/frequencies"
    echo ""
    
    if command -v curl &> /dev/null; then
      echo "測試根端點..."
      curl -s http://localhost:8787/ | head -n 10
      echo ""
      echo "測試狀態端點..."
      curl -s http://localhost:8787/status | head -n 10
      echo ""
    fi
    
    echo ""
    read -p "按任意鍵繼續部署（測試服務器將被關閉）..." -n 1 -r
    echo ""
    
    # 關閉開發服務器
    kill $DEV_PID 2>/dev/null || true
    sleep 2
    
    cd "$ROOT_DIR"
  fi
  
  echo "✅ 測試階段完成"
  echo ""
}

# 4. 部署
deploy() {
  echo "[4/5] 部署到 Cloudflare..."
  
  cd "$ROOT_DIR/cloudflare/mrliouword-private"
  
  # 檢查 wrangler.jsonc 配置
  if [ ! -f "wrangler.jsonc" ]; then
    echo "❌ 找不到 wrangler.jsonc 配置文件"
    exit 1
  fi
  
  echo "配置文件檢查："
  echo "✓ wrangler.jsonc 存在"
  
  # 顯示配置摘要
  if command -v jq &> /dev/null; then
    echo ""
    echo "配置摘要："
    cat wrangler.jsonc | grep -v "^[[:space:]]*\/\/" | jq -r '.name, .vars.VERSION' 2>/dev/null || true
  fi
  
  echo ""
  echo "執行部署..."
  wrangler deploy
  
  if [ $? -ne 0 ]; then
    echo "❌ 部署失敗"
    echo ""
    echo "可能的原因："
    echo "1. 資源綁定 ID 不正確（檢查 wrangler.jsonc）"
    echo "2. Cloudflare 帳戶權限不足"
    echo "3. 網絡連接問題"
    echo ""
    echo "請檢查錯誤訊息並重試。"
    exit 1
  fi
  
  cd "$ROOT_DIR"
  echo "✅ 部署完成"
  echo ""
}

# 5. 驗證
verify() {
  echo "[5/5] 驗證部署..."
  
  # 提取 worker URL（根據實際部署輸出調整）
  read -p "請輸入您的 Worker URL (例: https://particle-edge.your-account.workers.dev): " WORKER_URL
  
  if [ -z "$WORKER_URL" ]; then
    echo "⚠️  未提供 URL，跳過驗證"
    return
  fi
  
  echo ""
  echo "測試端點："
  
  if ! command -v curl &> /dev/null; then
    echo "⚠️  未找到 curl，無法自動驗證"
    echo "請手動訪問以下 URL 進行驗證："
    echo "- $WORKER_URL/"
    echo "- $WORKER_URL/status"
    echo "- $WORKER_URL/frequencies"
    return
  fi
  
  echo ""
  echo "1. 測試根端點..."
  HTTP_CODE=$(curl -s -o /tmp/verify_root.json -w "%{http_code}" "$WORKER_URL/")
  if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ 根端點響應正常 (200)"
    if command -v jq &> /dev/null; then
      cat /tmp/verify_root.json | jq -r '.name, .version, .philosophy' 2>/dev/null || cat /tmp/verify_root.json
    else
      cat /tmp/verify_root.json | head -n 10
    fi
  else
    echo "⚠️  根端點響應異常 ($HTTP_CODE)"
  fi
  
  echo ""
  echo "2. 測試狀態端點..."
  HTTP_CODE=$(curl -s -o /tmp/verify_status.json -w "%{http_code}" "$WORKER_URL/status")
  if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ 狀態端點響應正常 (200)"
    if command -v jq &> /dev/null; then
      cat /tmp/verify_status.json | jq -r '.version, .awakened' 2>/dev/null || cat /tmp/verify_status.json
    else
      cat /tmp/verify_status.json | head -n 10
    fi
  else
    echo "⚠️  狀態端點響應異常 ($HTTP_CODE)"
  fi
  
  echo ""
  echo "3. 測試頻率端點..."
  HTTP_CODE=$(curl -s -o /tmp/verify_freq.json -w "%{http_code}" "$WORKER_URL/frequencies")
  if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ 頻率端點響應正常 (200)"
    if command -v jq &> /dev/null; then
      cat /tmp/verify_freq.json | jq -r '.schumann, .phi' 2>/dev/null || cat /tmp/verify_freq.json
    else
      cat /tmp/verify_freq.json | head -n 10
    fi
  else
    echo "⚠️  頻率端點響應異常 ($HTTP_CODE)"
  fi
  
  # 清理臨時文件
  rm -f /tmp/verify_*.json 2>/dev/null || true
  
  echo ""
  echo "✅ 驗證完成"
  echo ""
}

# 執行流程
main() {
  check_prerequisites
  install_deps
  local_test
  deploy
  verify
  
  echo ""
  echo "🎉 部署完成！"
  echo ""
  echo "=========================================="
  echo "Particle Edge v4.0.0"
  echo "origin_signature: MrLiouWord"
  echo "philosophy: 怎麼過去，就怎麼回來"
  echo "version: 4.0.0"
  echo "=========================================="
  echo ""
  echo "下一步："
  echo "1. 使用喚醒鍵激活人格系統："
  echo "   curl -X POST <YOUR_WORKER_URL>/wake \\"
  echo "     -H 'Content-Type: application/json' \\"
  echo "     -H 'X-Master-Key: YOUR_KEY' \\"
  echo "     -d '{\"message\": \"夥伴回來吧\"}'"
  echo ""
  echo "2. 查看完整 API 文檔："
  echo "   docs/API_ENDPOINTS.md"
  echo ""
  echo "3. 閱讀部署指南："
  echo "   DEPLOY-GUIDE.md"
  echo ""
}

# 執行主函數
main
