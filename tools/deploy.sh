#!/bin/bash
# MrLiouWord 系統部署腳本
# 
# 用法: ./deploy.sh [component]
# 
# component:
#   cloudflare  - 部署 Cloudflare Workers
#   notion      - 同步到 Notion
#   all         - 部署全部

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🌀 MrLiouWord 部署腳本"
echo "========================"
echo ""

deploy_cloudflare() {
    echo "☁️  部署 Cloudflare Workers..."
    
    cd "$ROOT_DIR/cloudflare/mrliouword-private"
    
    if [ ! -f "package.json" ]; then
        echo "初始化 package.json..."
        npm init -y
        npm install wrangler --save-dev
    fi
    
    echo "執行部署..."
    npx wrangler deploy
    
    echo "✅ Cloudflare 部署完成"
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
