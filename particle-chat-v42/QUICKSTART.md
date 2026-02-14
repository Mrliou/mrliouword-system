# 🚀 Quick Deployment Reference

## One-Time Setup (First Deployment)

```bash
# 1. Navigate to project
cd particle-chat-v42

# 2. Install dependencies
npm install

# 3. Login to Cloudflare
wrangler login

# 4. Set Anthropic API Key
wrangler secret put ANTHROPIC_API_KEY
# Paste your API key when prompted

# 5. Deploy
wrangler deploy
```

## Quick Redeploy (After Code Changes)

```bash
cd particle-chat-v42
wrangler deploy
```

## Testing

```bash
# Get your worker URL from deployment output, then:

# Test API info
curl https://particle-chat-v42.YOUR-ACCOUNT.workers.dev/

# Test health
curl https://particle-chat-v42.YOUR-ACCOUNT.workers.dev/health

# Test chat
curl -X POST https://particle-chat-v42.YOUR-ACCOUNT.workers.dev/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

## Local Development

```bash
# Start local server
npm run dev

# Test locally
curl http://localhost:8787/health
```

## Common Commands

```bash
# View logs
wrangler tail

# List secrets
wrangler secret list

# Check who's logged in
wrangler whoami

# Update API key
wrangler secret put ANTHROPIC_API_KEY
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Not logged in | `wrangler login` |
| API key missing | `wrangler secret put ANTHROPIC_API_KEY` |
| Command not found | `npm install -g wrangler` |
| Dependencies missing | `npm install` |

## Links

- 📖 Full docs: [DEPLOYMENT.md](DEPLOYMENT.md)
- 💡 Examples: [EXAMPLES.md](EXAMPLES.md)
- 📋 Overview: [README.md](README.md)
- 🔑 Get API key: https://console.anthropic.com/
- 📚 Cloudflare Docs: https://developers.cloudflare.com/workers/

---

**Origin**: MrLiouWord  
**Philosophy**: 怎麼過去，就怎麼回來
