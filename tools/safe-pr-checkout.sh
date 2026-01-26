#!/bin/bash

# safe-pr-checkout.sh
# A safe wrapper for gh pr checkout that validates PR existence first
# Usage: ./tools/safe-pr-checkout.sh <pr_number>

set -e

PR_NUMBER=$1

if [ -z "$PR_NUMBER" ]; then
    echo "❌ Error: PR number is required"
    echo "Usage: $0 <pr_number>"
    exit 1
fi

echo "🔍 Validating PR #$PR_NUMBER..."

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed"
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if PR exists
if ! gh pr view "$PR_NUMBER" &> /dev/null; then
    echo "❌ Error: PR #$PR_NUMBER does not exist in this repository"
    echo ""
    echo "📋 Recent pull requests:"
    gh pr list --limit 5 --state all
    echo ""
    echo "💡 Tip: Use 'gh pr list' to see all available pull requests"
    exit 1
fi

echo "✅ PR #$PR_NUMBER exists"
echo "📥 Checking out PR #$PR_NUMBER..."

gh pr checkout "$PR_NUMBER"

echo "✅ Successfully checked out PR #$PR_NUMBER"
