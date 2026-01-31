# Particle Chat v42

> **Origin**: MrLiouWord  
> **Philosophy**: 怎麼過去，就怎麼回來  
> **Version**: 1.0.0

A Cloudflare Worker that provides chat functionality using Anthropic's Claude API.

## Features

- 💬 Chat with Claude AI via Anthropic API
- 🚀 Deployed on Cloudflare Workers for global low-latency access
- 🔒 Secure API key management using Wrangler secrets
- 🌐 CORS enabled for web integration
- ⚡ Fast, serverless architecture

## Prerequisites

1. **Node.js** v18 or higher
2. **Wrangler CLI** - Cloudflare Workers CLI tool
3. **Cloudflare Account** - Free tier works
4. **Anthropic API Key** - Get one from [Anthropic Console](https://console.anthropic.com/)

## Installation

```bash
# Navigate to the project directory
cd particle-chat-v42

# Install dependencies
npm install
```

## Configuration

### 1. Login to Cloudflare

```bash
wrangler login
```

This will open a browser window for authentication.

### 2. Set the Anthropic API Key

```bash
wrangler secret put ANTHROPIC_API_KEY
```

When prompted, paste your Anthropic API key.

## Development

Run the worker locally:

```bash
npm run dev
```

The worker will be available at `http://localhost:8787`

## Deployment

Deploy to Cloudflare Workers:

```bash
npm run deploy
# or
wrangler deploy
```

After deployment, you'll receive a URL like:
```
https://particle-chat-v42.<your-account>.workers.dev
```

## API Endpoints

### GET `/`

Returns API information and available endpoints.

**Example:**
```bash
curl https://particle-chat-v42.<your-account>.workers.dev/
```

### GET `/health`

Health check endpoint.

**Example:**
```bash
curl https://particle-chat-v42.<your-account>.workers.dev/health
```

### POST `/chat`

Send a message to Claude and get a response.

**Request Body:**
```json
{
  "message": "Hello, how are you?",
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 1024
}
```

**Example:**
```bash
curl -X POST https://particle-chat-v42.<your-account>.workers.dev/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, Claude!"}'
```

**Response:**
```json
{
  "origin": "MrLiouWord",
  "model": "claude-3-5-sonnet-20241022",
  "response": "Hello! I'm doing well, thank you for asking...",
  "usage": {
    "input_tokens": 10,
    "output_tokens": 25
  },
  "timestamp": 1234567890
}
```

## Environment Variables

- `ANTHROPIC_API_KEY` (secret) - Your Anthropic API key
- `ENVIRONMENT` - Environment name (defaults to "production")
- `VERSION` - Version string (defaults to "1.0.0")

## Project Structure

```
particle-chat-v42/
├── src/
│   └── index.ts          # Main worker code
├── package.json          # Project dependencies
├── wrangler.jsonc        # Wrangler configuration
└── README.md            # This file
```

## Security Notes

- Never commit your `ANTHROPIC_API_KEY` to version control
- Use Wrangler secrets to manage sensitive data
- The API key is stored securely in Cloudflare's infrastructure
- CORS is enabled - consider adding authentication for production use

## Troubleshooting

### Error: ANTHROPIC_API_KEY not configured

Make sure you've set the secret:
```bash
wrangler secret put ANTHROPIC_API_KEY
```

### Error: Module not found

Install dependencies:
```bash
npm install
```

### Authentication errors

Verify your API key is valid at [Anthropic Console](https://console.anthropic.com/)

## License

MIT

## Author

MR.liou × Claude

---

*怎麼過去，就怎麼回來*
