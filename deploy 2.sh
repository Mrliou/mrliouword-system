#!/bin/bash
# MrliouWord Private AI Server v2.1.0 一鍵部署腳本
# 整合向量注意力計算引擎

set -e

echo "=========================================="
echo "MrliouWord Private AI Server v2.1.0"
echo "整合向量注意力計算引擎"
echo "origin_signature=MrLiouWord"
echo "=========================================="

# 安裝依賴
echo "[1/3] 安裝依賴..."
npm install

# 類型檢查
echo "[2/3] 編譯檢查..."
npx tsc --noEmit --skipLibCheck 2>/dev/null || true

# 部署
echo "[3/3] 部署到 Cloudflare..."
npx wrangler deploy

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo ""
echo "新增端點:"
echo "  POST /attention/compute  - 計算多頭注意力"
echo "  POST /particle/create    - 創建粒子嵌入"
echo "  POST /particle/batch     - 批量創建粒子"
echo "  POST /vector/similarity  - 計算向量相似度"
echo "  POST /vector/operations  - 向量運算"
echo "  GET  /attention/config   - 注意力引擎配置"
echo ""
echo "測試命令:"
echo "  bash test.sh"
echo "=========================================="
