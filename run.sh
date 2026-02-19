#!/bin/bash
# MrLiou AI Supercomputer - Startup Script
# MrLiou AI 超級電腦 - 啟動腳本
#
# Philosophy: 怎麼過去，就怎麼回來 (How you go, so you return)

set -e

echo "=================================================="
echo "MrLiou AI Supercomputer v1.0"
echo "MrLiou AI 超級電腦 v1.0"
echo "=================================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python $PYTHON_VERSION"
echo ""

# Check required files
echo "Checking required files..."
REQUIRED_FILES=(
    "ai_providers.py"
    "flowcore_loop.py"
    "config/ai_providers.json"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Error: Required file not found: $file"
        exit 1
    fi
    echo "✓ $file"
done
echo ""

# Create directories if needed
echo "Creating directories..."
mkdir -p log
mkdir -p memory/ingest/ai_responses
echo "✓ Directories created"
echo ""

# Check environment variables
echo "Checking environment variables..."
ENV_VARS_SET=0
ENV_VARS_TOTAL=0

check_env() {
    ENV_VARS_TOTAL=$((ENV_VARS_TOTAL + 1))
    if [ -n "${!1}" ]; then
        echo "✓ $1 is set"
        ENV_VARS_SET=$((ENV_VARS_SET + 1))
    else
        echo "⚠️  $1 not set"
    fi
}

check_env "OPENAI_API_KEY"
check_env "ANTHROPIC_API_KEY"
check_env "GOOGLE_API_KEY"

echo ""
echo "Environment: $ENV_VARS_SET/$ENV_VARS_TOTAL API keys configured"
echo ""

if [ $ENV_VARS_SET -eq 0 ]; then
    echo "⚠️  Warning: No API keys configured"
    echo "Please set at least one API key in .env and load it:"
    echo "  export \$(cat .env | xargs)"
    echo ""
    echo "Or test with Ollama (local, no API key needed):"
    echo "  ollama serve"
    echo ""
fi

# Check if port is available
PORT="${PORT:-8787}"
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Warning: Port $PORT is already in use"
    echo "Trying port 8788 instead..."
    PORT=8788
    export PORT
fi

# Start server
echo "=================================================="
echo "Starting server on port $PORT..."
echo "=================================================="
echo ""

# Run the server
exec python3 flowcore_loop.py
