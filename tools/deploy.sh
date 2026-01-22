#!/bin/bash
# MrLiouWord 系統部署腳本
# 
# 用法: ./deploy.sh [component]
# 
# component:
#   cloudflare  - 部署 Cloudflare Workers
#   notion      - 同步到 Notion
#   all         - 部署全部
#
# origin_signature: MrLiouWord
# philosophy: 怎麼過去，就怎麼回來
# version: 4.0.0

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🌀 MrLiouWord 部署腳本 v4.0.0"
echo "=============================="
echo ""

deploy_cloudflare() {
    echo "☁️  部署 Cloudflare Workers..."
    
    # 版本檢查
    echo "檢查版本一致性..."
    if command -v jq &> /dev/null; then
        WRANGLER_VERSION=$(cat "$ROOT_DIR/cloudflare/mrliouword-private/wrangler.jsonc" | grep -v "^[[:space:]]*\/\/" | jq -r '.vars.VERSION' 2>/dev/null || echo "unknown")
        echo "wrangler.jsonc 版本: $WRANGLER_VERSION"
    fi
    
    cd "$ROOT_DIR/cloudflare/mrliouword-private"
    
    if [ ! -f "package.json" ]; then
        echo "初始化 package.json..."
        npm init -y
        npm install wrangler --save-dev
    fi
    
    # 確認資源綁定
    echo ""
    echo "檢查資源綁定配置..."
    if [ -f "wrangler.jsonc" ]; then
        echo "✓ wrangler.jsonc 存在"
        if command -v jq &> /dev/null; then
            KV_COUNT=$(cat wrangler.jsonc | grep -v "^[[:space:]]*\/\/" | jq -r '.kv_namespaces | length' 2>/dev/null || echo "0")
            R2_COUNT=$(cat wrangler.jsonc | grep -v "^[[:space:]]*\/\/" | jq -r '.r2_buckets | length' 2>/dev/null || echo "0")
            D1_COUNT=$(cat wrangler.jsonc | grep -v "^[[:space:]]*\/\/" | jq -r '.d1_databases | length' 2>/dev/null || echo "0")
            echo "  - KV Namespaces: $KV_COUNT"
            echo "  - R2 Buckets: $R2_COUNT"
            echo "  - D1 Databases: $D1_COUNT"
        fi
    else
        echo "⚠️  找不到 wrangler.jsonc"
    fi
    
    echo ""
    echo "執行部署..."
    npx wrangler deploy
    
    DEPLOY_STATUS=$?
    
    if [ $DEPLOY_STATUS -eq 0 ]; then
        echo ""
        echo "✅ Cloudflare 部署完成"
        
        # 部署後驗證
        echo ""
        echo "部署後驗證："
        read -p "請輸入 Worker URL 進行驗證 (留空跳過): " WORKER_URL
        
        if [ ! -z "$WORKER_URL" ] && command -v curl &> /dev/null; then
            echo "測試 /status 端點..."
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$WORKER_URL/status")
            if [ "$HTTP_CODE" = "200" ]; then
                echo "✓ Status 端點正常 (200)"
            else
                echo "⚠️  Status 端點異常 ($HTTP_CODE)"
            fi
            
            echo "測試 /heartbeat 端點..."
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$WORKER_URL/heartbeat")
            if [ "$HTTP_CODE" = "200" ]; then
                echo "✓ Heartbeat 端點正常 (200)"
            else
                echo "⚠️  Heartbeat 端點異常 ($HTTP_CODE)"
            fi
        fi
    else
        echo ""
        echo "❌ Cloudflare 部署失敗"
        exit 1
    fi
}

sync_notion() {
    echo "📝 同步到 Notion..."
    
    if [ -z "$NOTION_TOKEN" ]; then
        echo "⚠️  請設定 NOTION_TOKEN 環境變數"
        return 1
    fi
    
    cd "$ROOT_DIR/integrations/notion"
    
    python3 sync.py --sync-dict --dict-file "$ROOT_DIR/core/particle_dict.json"
    
    echo "✅ Notion 同步完成"
}

generate_kml() {
    echo "🌍 生成 KML..."
    
    cd "$ROOT_DIR/integrations/google"
    python3 integration.py
    
    echo "✅ KML 生成完成"
}

show_help() {
    echo "用法: $0 [component]"
    echo ""
    echo "Components:"
    echo "  cloudflare  - 部署 Cloudflare Workers"
    echo "  notion      - 同步到 Notion"
    echo "  kml         - 生成 Google Earth KML"
    echo "  all         - 部署全部"
    echo ""
    echo "環境變數:"
    echo "  CLOUDFLARE_API_TOKEN - Cloudflare API Token"
    echo "  NOTION_TOKEN         - Notion API Token"
}

case "${1:-all}" in
    cloudflare)
        deploy_cloudflare
        ;;
    notion)
        sync_notion
        ;;
    kml)
        generate_kml
        ;;
    all)
        deploy_cloudflare
        sync_notion
        generate_kml
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "未知組件: $1"
        show_help
        exit 1
        ;;
esac

echo ""
echo "🎉 部署完成！"
echo ""
echo "核心哲學：怎麼過去，就怎麼回來"
echo "版本: 4.0.0"
echo "origin_signature: MrLiouWord"
