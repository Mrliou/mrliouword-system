#!/usr/bin/env python3
"""
safe-pr-checkout.py
A safe wrapper for PR checkout that validates PR existence first using GitHub API
Usage: python3 tools/safe-pr-checkout.py <pr_number>
"""

import sys
import subprocess
import json
from urllib import request, error


def get_repo_info():
    """Extract repository owner and name from git remote"""
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            check=True
        )
        remote_url = result.stdout.strip()
        
        # Parse GitHub URL
        # Examples: 
        # - https://github.com/owner/repo.git
        # - git@github.com:owner/repo.git
        if 'github.com' in remote_url:
            parts = remote_url.replace('.git', '').split('/')
            if len(parts) >= 2:
                repo = parts[-1]
                owner = parts[-2].split(':')[-1]  # Handle git@ format
                return owner, repo
    except subprocess.CalledProcessError:
        pass
    
    return None, None


def check_pr_exists(owner, repo, pr_number):
    """Check if PR exists using GitHub API"""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    
    try:
        req = request.Request(url)
        req.add_header('Accept', 'application/vnd.github.v3+json')
        
        with request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return True, data
    except error.HTTPError as e:
        if e.code == 404:
            return False, None
        raise
    except Exception as e:
        print(f"⚠️  Warning: Could not verify PR via API: {e}")
        return None, None


def list_recent_prs(owner, repo, limit=5):
    """List recent PRs using GitHub API"""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all&per_page={limit}"
    
    try:
        req = request.Request(url)
        req.add_header('Accept', 'application/vnd.github.v3+json')
        
        with request.urlopen(req) as response:
            prs = json.loads(response.read().decode())
            return prs
    except Exception as e:
        print(f"⚠️  Warning: Could not fetch recent PRs: {e}")
        return []


def checkout_pr(pr_number):
    """Checkout PR using gh CLI or git fetch"""
    # Try gh CLI first
    try:
        result = subprocess.run(
            ['gh', 'pr', 'checkout', str(pr_number)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return True, "gh CLI"
    except FileNotFoundError:
        # gh CLI not installed
        pass
    
    # Fallback: Check if we can fetch the PR branch
    print("💡 Attempting alternative checkout method...")
    
    # Note: Without gh CLI auth, we'd need to know the branch name
    # For now, return false
    return False, None


def main():
    if len(sys.argv) < 2:
        print("❌ Error: PR number is required")
        print(f"Usage: {sys.argv[0]} <pr_number>")
        sys.exit(1)
    
    try:
        pr_number = int(sys.argv[1])
    except ValueError:
        print("❌ Error: PR number must be an integer")
        sys.exit(1)
    
    print(f"🔍 Validating PR #{pr_number}...")
    
    # Get repository information
    owner, repo = get_repo_info()
    
    if not owner or not repo:
        print("❌ Error: Could not determine repository information")
        print("Make sure you're in a git repository with a GitHub remote")
        sys.exit(1)
    
    print(f"📦 Repository: {owner}/{repo}")
    
    # Check if PR exists
    exists, pr_data = check_pr_exists(owner, repo, pr_number)
    
    if exists is False:
        print(f"❌ Error: PR #{pr_number} does not exist in {owner}/{repo}")
        print()
        print("📋 Recent pull requests:")
        
        recent_prs = list_recent_prs(owner, repo)
        if recent_prs:
            for pr in recent_prs:
                state_emoji = "🟢" if pr['state'] == 'open' else "🔴"
                print(f"  {state_emoji} #{pr['number']}: {pr['title'][:60]}")
        else:
            print("  (Could not fetch recent PRs)")
        
        print()
        print(f"💡 Tip: Visit https://github.com/{owner}/{repo}/pulls to see all pull requests")
        sys.exit(1)
    
    if exists is True:
        print(f"✅ PR #{pr_number} exists")
        print(f"   Title: {pr_data.get('title', 'N/A')}")
        print(f"   State: {pr_data.get('state', 'N/A')}")
        print(f"   Branch: {pr_data.get('head', {}).get('ref', 'N/A')}")
        print()
    
    print(f"📥 Attempting to checkout PR #{pr_number}...")
    
    success, method = checkout_pr(pr_number)
    
    if success:
        print(f"✅ Successfully checked out PR #{pr_number} using {method}")
    else:
        print(f"❌ Error: Could not checkout PR #{pr_number}")
        print()
        print("Possible solutions:")
        print("  1. Install and authenticate with GitHub CLI: https://cli.github.com/")
        print("  2. Manually checkout the PR branch:")
        if pr_data and pr_data.get('head', {}).get('ref'):
            branch = pr_data['head']['ref']
            print(f"     git fetch origin {branch}")
            print(f"     git checkout {branch}")
        sys.exit(1)


if __name__ == '__main__':
    main()
