#!/bin/bash
# Deployment script for particle-chat-v42
# This script demonstrates the deployment process

set -e

echo "🚀 Particle Chat v42 Deployment"
echo "================================"
echo ""

# Navigate to project directory
cd "$(dirname "$0")"
echo "📁 Current directory: $(pwd)"
echo ""

# Check if logged in
echo "🔐 Step 1: Checking Cloudflare authentication..."
if ! npx wrangler whoami &>/dev/null; then
    echo "❌ Not logged in to Cloudflare"
    echo "Please run: npx wrangler login"
    exit 1
fi
echo "✅ Authenticated"
echo ""

# Check if ANTHROPIC_API_KEY is set
echo "🔑 Step 2: Checking for ANTHROPIC_API_KEY secret..."
echo "Note: If not set, run: npx wrangler secret put ANTHROPIC_API_KEY"
echo ""

# Deploy
echo "📦 Step 3: Deploying to Cloudflare Workers..."
npx wrangler deploy

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "   1. If you haven't set the ANTHROPIC_API_KEY secret yet, run:"
echo "      npx wrangler secret put ANTHROPIC_API_KEY"
echo ""
echo "   2. Test your deployment:"
echo "      curl https://particle-chat-v42.<your-account>.workers.dev/"
echo ""
