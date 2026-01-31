# Particle Chat v42 - Deployment Guide

This guide walks you through deploying the Particle Chat v42 Cloudflare Worker with Anthropic Claude integration.

## Quick Start

Follow these exact steps to deploy:

### 1. Navigate to the project directory

```bash
cd particle-chat-v42
```

### 2. Login to Cloudflare

```bash
wrangler login
```

This will open your browser for authentication. Approve the access request.

### 3. Set the Anthropic API Key

```bash
wrangler secret put ANTHROPIC_API_KEY
```

When prompted, paste your Anthropic API key. You can get one from [Anthropic Console](https://console.anthropic.com/).

### 4. Deploy the Worker

```bash
wrangler deploy
```

That's it! Your worker is now deployed and running on Cloudflare's global network.

## Verify Deployment

After deployment, you'll see output like:

```
Total Upload: XX.XX KiB / gzip: XX.XX KiB
Uploaded particle-chat-v42 (X.XX sec)
Published particle-chat-v42 (X.XX sec)
  https://particle-chat-v42.<your-account>.workers.dev
```

Test your deployment:

```bash
# Get API info
curl https://particle-chat-v42.<your-account>.workers.dev/

# Check health
curl https://particle-chat-v42.<your-account>.workers.dev/health

# Send a chat message
curl -X POST https://particle-chat-v42.<your-account>.workers.dev/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

## Prerequisites

Before deploying, ensure you have:

1. **Node.js** (v18 or higher) - [Download here](https://nodejs.org/)
2. **Wrangler CLI** - Install with: `npm install -g wrangler`
3. **Cloudflare Account** - [Sign up here](https://dash.cloudflare.com/sign-up) (free tier works)
4. **Anthropic API Key** - [Get one here](https://console.anthropic.com/)

## Installing Dependencies

If you haven't already, install the project dependencies:

```bash
npm install
```

## Local Development

Test the worker locally before deploying:

```bash
# Start local development server
npm run dev

# In another terminal, test it
curl http://localhost:8787/health
```

Note: For local development, you'll need to set the ANTHROPIC_API_KEY as an environment variable or use a `.dev.vars` file:

```bash
# Create .dev.vars file
echo "ANTHROPIC_API_KEY=your-key-here" > .dev.vars
```

## Managing Secrets

### List secrets

```bash
wrangler secret list
```

### Update a secret

```bash
wrangler secret put ANTHROPIC_API_KEY
```

### Delete a secret

```bash
wrangler secret delete ANTHROPIC_API_KEY
```

## Troubleshooting

### Error: Not logged in

**Solution:** Run `wrangler login` and complete authentication in your browser.

### Error: ANTHROPIC_API_KEY not configured

**Solution:** Run `wrangler secret put ANTHROPIC_API_KEY` and paste your API key.

### Error: Command not found: wrangler

**Solution:** Install Wrangler globally: `npm install -g wrangler`

### Deployment fails with authentication error

**Solution:** 
1. Logout: `wrangler logout`
2. Login again: `wrangler login`
3. Try deploying again: `wrangler deploy`

## Updating the Worker

To update your deployed worker after making code changes:

```bash
# Make your changes to src/index.ts
# Then redeploy
wrangler deploy
```

## Viewing Logs

Monitor your worker's logs in real-time:

```bash
wrangler tail
```

## Configuration

The worker configuration is in `wrangler.jsonc`:

```jsonc
{
  "name": "particle-chat-v42",
  "main": "src/index.ts",
  "compatibility_date": "2024-12-01",
  "compatibility_flags": ["nodejs_compat"],
  "vars": {
    "ENVIRONMENT": "production",
    "VERSION": "1.0.0"
  }
}
```

## Support

For issues or questions:
- Check the [README.md](README.md) for API documentation
- See [EXAMPLES.md](EXAMPLES.md) for usage examples
- Visit [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- Visit [Anthropic API Docs](https://docs.anthropic.com/)

---

**Origin**: MrLiouWord  
**Philosophy**: 怎麼過去，就怎麼回來
