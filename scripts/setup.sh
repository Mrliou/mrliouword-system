#!/bin/bash

# Mrliouword Agent SDK - 快速設定腳本

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " 開始設定 Mrliouword Agent SDK..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 檢查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 錯誤: Python 3 未安裝"
    exit 1
fi

python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python 版本: $python_version"

# 建立虛擬環境
if [ ! -d "venv" ]; then
    echo "📦 建立虛擬環境..."
    python3 -m venv venv
    echo "✓ 虛擬環境已建立"
else
    echo "✓ 虛擬環境已存在"
fi

# 啟動虛擬環境
echo "🔄 啟動虛擬環境..."
source venv/bin/activate

# 升級 pip
echo "⬆️  升級 pip..."
pip install --upgrade pip --quiet

# 安裝依賴
echo "📦 安裝依賴套件..."
pip install -r requirements.txt --quiet
pip install -r requirements-dev.txt --quiet
pip install -e . --quiet

# 建立必要目錄
echo "📁 建立目錄結構..."
mkdir -p data/input data/output data/cache logs

# 複製環境變數範例
if [ ! -f ".env" ]; then
    echo "📝 建立環境變數檔案..."
    cp .env.example .env
    echo "⚠️  請編輯 .env 檔案並填入你的 ANTHROPIC_API_KEY"
else
    echo "✓ .env 檔案已存在"
fi

# 設定 Git hooks（如果存在）
if [ -f ".pre-commit-config.yaml" ]; then
    echo "🪝 設定 Git hooks..."
    pre-commit install --quiet || echo "⚠️  pre-commit 安裝失敗（可選）"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 設定完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "下一步："
echo "1. 編輯 .env 檔案，填入你的 ANTHROPIC_API_KEY"
echo "2. 啟動虛擬環境: source venv/bin/activate"
echo "3. 執行範例: python examples/basic_usage.py"
echo "4. 或使用 CLI: mrliouword --help"
echo ""
