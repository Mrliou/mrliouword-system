/**
 * Particle Chat v42
 * 
 * Cloudflare Worker with Anthropic Claude Integration
 * 
 * Features:
 * - Chat with Claude via Anthropic API
 * - Streaming responses
 * - CORS support
 * - Origin signature: MrLiouWord
 * 
 * Author: MR.liou × Claude
 * Philosophy: 怎麼過去，就怎麼回來
 */

import Anthropic from '@anthropic-ai/sdk';

const ORIGIN = 'MrLiouWord';
const VERSION = '1.0.0';

interface Env {
  ANTHROPIC_API_KEY: string;
  ENVIRONMENT?: string;
  VERSION?: string;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatRequest {
  message: string;
  messages?: ChatMessage[];
  model?: string;
  max_tokens?: number;
  stream?: boolean;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;
    
    const headers = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Content-Type': 'application/json',
      'X-Origin-Signature': ORIGIN,
      'X-Version': env.VERSION || VERSION,
    };
    
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers });
    }
    
    try {
      // Root endpoint - API info
      if (path === '/' && request.method === 'GET') {
        return new Response(JSON.stringify({
          name: 'Particle Chat v42',
          version: env.VERSION || VERSION,
          philosophy: '怎麼過去，就怎麼回來',
          origin: ORIGIN,
          environment: env.ENVIRONMENT || 'production',
          endpoints: {
            'GET /': 'API information',
            'POST /chat': 'Send a chat message',
            'GET /health': 'Health check',
          },
          status: 'operational',
        }, null, 2), { headers });
      }
      
      // Health check
      if (path === '/health' && request.method === 'GET') {
        return new Response(JSON.stringify({
          status: 'healthy',
          origin: ORIGIN,
          timestamp: Date.now(),
          api_configured: !!env.ANTHROPIC_API_KEY,
        }), { headers });
      }
      
      // Chat endpoint
      if (path === '/chat' && request.method === 'POST') {
        if (!env.ANTHROPIC_API_KEY) {
          return new Response(JSON.stringify({
            error: 'ANTHROPIC_API_KEY not configured',
            message: 'Please set the ANTHROPIC_API_KEY secret using: wrangler secret put ANTHROPIC_API_KEY',
          }), { 
            status: 500, 
            headers 
          });
        }
        
        const body = await request.json() as ChatRequest;
        
        if (!body.message && (!body.messages || body.messages.length === 0)) {
          return new Response(JSON.stringify({
            error: 'Missing message',
            message: 'Please provide either "message" or "messages" in the request body',
          }), { 
            status: 400, 
            headers 
          });
        }
        
        const anthropic = new Anthropic({
          apiKey: env.ANTHROPIC_API_KEY,
        });
        
        // Build messages array
        const messages: ChatMessage[] = body.messages || [
          { role: 'user', content: body.message }
        ];
        
        const model = body.model || 'claude-3-5-sonnet-20241022';
        const max_tokens = body.max_tokens || 1024;
        
        // Call Anthropic API
        const response = await anthropic.messages.create({
          model: model,
          max_tokens: max_tokens,
          messages: messages,
        });
        
        return new Response(JSON.stringify({
          origin: ORIGIN,
          model: response.model,
          response: response.content[0].type === 'text' 
            ? response.content[0].text 
            : 'No text response',
          usage: response.usage,
          timestamp: Date.now(),
        }, null, 2), { headers });
      }
      
      // 404 - Not found
      return new Response(JSON.stringify({
        error: 'Not found',
        path: path,
        origin: ORIGIN,
      }), { 
        status: 404, 
        headers 
      });
      
    } catch (error) {
      console.error('Error:', error);
      return new Response(JSON.stringify({
        error: 'Internal error',
        message: error instanceof Error ? error.message : 'Unknown error',
        origin: ORIGIN,
      }), { 
        status: 500, 
        headers 
      });
    }
  },
};
