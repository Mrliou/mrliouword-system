# Particle Chat v42 - Usage Examples

This file contains examples of how to interact with the deployed worker.

## Prerequisites

Replace `<your-worker-url>` with your actual worker URL, which will look like:
- `https://particle-chat-v42.<your-account>.workers.dev`

## Examples

### 1. Get API Information

```bash
curl https://<your-worker-url>/
```

**Response:**
```json
{
  "name": "Particle Chat v42",
  "version": "1.0.0",
  "philosophy": "怎麼過去，就怎麼回來",
  "origin": "MrLiouWord",
  "environment": "production",
  "endpoints": {
    "GET /": "API information",
    "POST /chat": "Send a chat message",
    "GET /health": "Health check"
  },
  "status": "operational"
}
```

### 2. Health Check

```bash
curl https://<your-worker-url>/health
```

**Response:**
```json
{
  "status": "healthy",
  "origin": "MrLiouWord",
  "timestamp": 1706695000000,
  "api_configured": true
}
```

### 3. Send a Chat Message

```bash
curl -X POST https://<your-worker-url>/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! Can you introduce yourself?"
  }'
```

**Response:**
```json
{
  "origin": "MrLiouWord",
  "model": "claude-3-5-sonnet-20241022",
  "response": "Hello! I'm Claude, an AI assistant created by Anthropic...",
  "usage": {
    "input_tokens": 12,
    "output_tokens": 45
  },
  "timestamp": 1706695000000
}
```

### 4. Chat with Custom Model and Max Tokens

```bash
curl -X POST https://<your-worker-url>/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Write a haiku about particles",
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 100
  }'
```

### 5. Multi-turn Conversation

```bash
curl -X POST https://<your-worker-url>/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is quantum mechanics?"},
      {"role": "assistant", "content": "Quantum mechanics is a fundamental theory in physics that describes the behavior of matter and energy at the atomic and subatomic scales."},
      {"role": "user", "content": "Can you explain wave-particle duality?"}
    ]
  }'
```

## Testing with JavaScript

```javascript
// Fetch API example
async function chatWithClaude(message) {
  const response = await fetch('https://<your-worker-url>/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });
  
  const data = await response.json();
  console.log('Claude says:', data.response);
  return data;
}

// Usage
chatWithClaude('Tell me about MrLiouWord philosophy');
```

## Testing with Python

```python
import requests
import json

def chat_with_claude(message):
    url = 'https://<your-worker-url>/chat'
    payload = {'message': message}
    
    response = requests.post(url, json=payload)
    data = response.json()
    
    print(f"Claude says: {data['response']}")
    return data

# Usage
chat_with_claude('Explain particle physics in simple terms')
```

## Error Handling

### API Key Not Configured

If you get an error about missing API key:

```json
{
  "error": "ANTHROPIC_API_KEY not configured",
  "message": "Please set the ANTHROPIC_API_KEY secret using: wrangler secret put ANTHROPIC_API_KEY"
}
```

**Solution:**
```bash
cd particle-chat-v42
npx wrangler secret put ANTHROPIC_API_KEY
# Then paste your Anthropic API key when prompted
```

### Missing Message

```json
{
  "error": "Missing message",
  "message": "Please provide either \"message\" or \"messages\" in the request body"
}
```

**Solution:** Include either `message` (string) or `messages` (array) in your request body.

## Available Models

- `claude-3-5-sonnet-20241022` (default, recommended)
- `claude-3-5-haiku-20241022` (faster, cheaper)
- `claude-3-opus-20240229` (most capable)

## Rate Limits

Rate limits depend on your Anthropic API tier. Check your [Anthropic Console](https://console.anthropic.com/) for details.

## CORS

CORS is enabled for all origins (`*`). For production use, consider:
1. Restricting origins in the worker code
2. Adding authentication
3. Implementing rate limiting

---

*Origin: MrLiouWord*  
*Philosophy: 怎麼過去，就怎麼回來*
