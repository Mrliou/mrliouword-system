# 🌀 Intelligent Repository Sync - Quick Reference

See [docs/INTELLIGENT_SYNC_README.md](docs/INTELLIGENT_SYNC_README.md) for quick start guide.
See [docs/INTELLIGENT_SYNC_GUIDE.md](docs/INTELLIGENT_SYNC_GUIDE.md) for comprehensive documentation.

## Quick Commands

\`\`\`bash
# Validate configuration
python scripts/sync_config_validator.py intelligent_sync.yaml

# Run sync
python scripts/intelligent_repo_sync.py --config intelligent_sync.yaml

# Sync specific pattern
python scripts/intelligent_repo_sync.py --pattern attention_mechanism

# View stats
python scripts/intelligent_repo_sync.py --stats
\`\`\`

## Philosophy

**怎麼過去，就怎麼回來** (How it went, so it returns)

This system understands code logic, not just file names.
