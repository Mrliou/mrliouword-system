#!/usr/bin/env python3
"""
MrLiou AI Supercomputer - FlowCore Loop with Judge Pattern
==========================================================

HTTP server with AI provider integration, Merkle chain audit trail,
and cost tracking. Zero external dependencies.

Author: MR.liou & Claude
Version: 1.0.0
Philosophy: 怎麼過去，就怎麼回來 (How you go, so you return)
"""

import json
import os
import sys
import hashlib
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional

# Import AI providers
from ai_providers import AIProviderManager


# Global state
MERKLE_STATE_FILE = "log/trace_state.json"
TRACE_LOG_FILE = "log/trace.jsonl"
COST_LOG_FILE = "log/ai_costs.jsonl"
AI_RESPONSES_DIR = "memory/ingest/ai_responses"

# Initialize directories
os.makedirs("log", exist_ok=True)
os.makedirs("memory/ingest/ai_responses", exist_ok=True)

# Global AI provider manager
ai_manager = None


class MerkleChain:
    """Simple Merkle chain for audit trail."""
    
    def __init__(self, state_file: str, log_file: str):
        self.state_file = state_file
        self.log_file = log_file
        self.load_state()
    
    def load_state(self):
        """Load Merkle state from file."""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                self.root = state.get("merkle_root", "0" * 64)
                self.count = state.get("trace_count", 0)
        else:
            self.root = "0" * 64
            self.count = 0
    
    def save_state(self):
        """Save Merkle state to file."""
        state = {
            "merkle_root": self.root,
            "trace_count": self.count,
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def emit_trace(self, event_type: str, data: Dict[str, Any]) -> str:
        """
        Emit a trace event to the Merkle chain.
        
        Args:
            event_type: Type of event (e.g., "ai_complete_pre", "ai_complete_post")
            data: Event data
            
        Returns:
            New Merkle root hash
        """
        trace_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "trace_id": self.count + 1,
            "event_type": event_type,
            "data": data,
            "prev_root": self.root
        }
        
        # Calculate new Merkle root
        trace_json = json.dumps(trace_entry, sort_keys=True)
        new_root = hashlib.sha256((self.root + trace_json).encode()).hexdigest()
        
        trace_entry["merkle_root"] = new_root
        
        # Append to log
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(trace_entry) + '\n')
        
        # Update state
        self.root = new_root
        self.count += 1
        self.save_state()
        
        return new_root


# Global Merkle chain
merkle_chain = MerkleChain(MERKLE_STATE_FILE, TRACE_LOG_FILE)


def log_cost(provider: str, model: str, usage: Dict[str, int], cost: float):
    """Log AI cost to cost tracking file."""
    cost_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "provider": provider,
        "model": model,
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
        "estimated_cost_usd": cost
    }
    
    with open(COST_LOG_FILE, 'a') as f:
        f.write(json.dumps(cost_entry) + '\n')


def snapshot_response(response_text: str, metadata: Dict[str, Any]) -> str:
    """Save AI response snapshot before it's returned."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{AI_RESPONSES_DIR}/response_{timestamp}.json"
    
    snapshot = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "response": response_text,
        "metadata": metadata
    }
    
    with open(filename, 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    return filename


def judge_ai_complete(prompt: str, provider: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Judge Loop AI completion with full audit trail.
    
    This function implements the Judge Loop pattern:
    1. Pre-trace emission (request logged to Merkle chain)
    2. Provider execution with fallback
    3. Response snapshotting (reversibility)
    4. Cost calculation and logging
    5. Post-trace emission (completion logged to Merkle chain)
    
    Args:
        prompt: User prompt
        provider: Optional provider name
        **kwargs: Additional parameters
        
    Returns:
        Dict with response, metadata, and merkle_root
    """
    request_id = f"req_{int(time.time() * 1000)}"
    
    # Step 1: Pre-trace emission
    pre_trace_data = {
        "request_id": request_id,
        "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
        "provider": provider or ai_manager.default_provider,
        "params": {k: v for k, v in kwargs.items() if k != "prompt"}
    }
    merkle_chain.emit_trace("ai_complete_pre", pre_trace_data)
    
    try:
        # Step 2: Provider execution
        result = ai_manager.complete(prompt, provider, **kwargs)
        
        response_text = result["text"]
        model_used = result["model"]
        usage = result["usage"]
        provider_used = provider or ai_manager.default_provider
        
        # Step 3: Response snapshotting
        snapshot_file = snapshot_response(response_text, {
            "request_id": request_id,
            "provider": provider_used,
            "model": model_used,
            "usage": usage
        })
        
        # Step 4: Cost calculation and logging
        cost = ai_manager.calculate_cost(usage, model_used, provider_used)
        log_cost(provider_used, model_used, usage, cost)
        
        # Step 5: Post-trace emission
        post_trace_data = {
            "request_id": request_id,
            "provider": provider_used,
            "model": model_used,
            "usage": usage,
            "cost_usd": cost,
            "snapshot": snapshot_file,
            "status": "success"
        }
        merkle_root = merkle_chain.emit_trace("ai_complete_post", post_trace_data)
        
        return {
            "response": response_text,
            "metadata": {
                "request_id": request_id,
                "provider": provider_used,
                "model": model_used,
                "usage": usage,
                "cost_usd": cost,
                "merkle_root": merkle_root
            }
        }
        
    except Exception as e:
        # Log error to Merkle chain
        error_trace_data = {
            "request_id": request_id,
            "error": str(e),
            "status": "failed"
        }
        merkle_root = merkle_chain.emit_trace("ai_complete_error", error_trace_data)
        
        raise


class FlowCoreHandler(BaseHTTPRequestHandler):
    """HTTP request handler for FlowCore Loop."""
    
    def log_message(self, format, *args):
        """Custom log message format."""
        sys.stderr.write(f"[{datetime.utcnow().isoformat()}] {format % args}\n")
    
    def _send_json_response(self, data: Any, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def _send_sse_response(self):
        """Initialize Server-Sent Events response."""
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    
    def _read_json_body(self) -> Dict[str, Any]:
        """Read and parse JSON body."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        return json.loads(body.decode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/ai/providers':
            # List available providers
            try:
                providers = ai_manager.list_providers()
                self._send_json_response({
                    "providers": providers,
                    "default": ai_manager.default_provider,
                    "fallback_enabled": ai_manager.fallback_enabled
                })
            except Exception as e:
                self._send_json_response({"error": str(e)}, 500)
        
        elif path == '/health':
            # Health check
            self._send_json_response({
                "status": "ok",
                "merkle_root": merkle_chain.root,
                "trace_count": merkle_chain.count
            })
        
        else:
            self._send_json_response({"error": "Not found"}, 404)
    
    def do_POST(self):
        """Handle POST requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/ai/complete':
            # Synchronous AI completion
            try:
                body = self._read_json_body()
                prompt = body.get("prompt", "")
                provider = body.get("provider")
                model = body.get("model")
                max_tokens = body.get("max_tokens", 1000)
                temperature = body.get("temperature", 0.7)
                
                if not prompt:
                    self._send_json_response({"error": "Prompt required"}, 400)
                    return
                
                kwargs = {}
                if model:
                    kwargs["model"] = model
                if max_tokens:
                    kwargs["max_tokens"] = max_tokens
                if temperature is not None:
                    kwargs["temperature"] = temperature
                
                result = judge_ai_complete(prompt, provider, **kwargs)
                self._send_json_response(result)
                
            except Exception as e:
                self._send_json_response({"error": str(e)}, 500)
        
        elif path == '/ai/stream':
            # Streaming AI completion
            try:
                body = self._read_json_body()
                prompt = body.get("prompt", "")
                provider = body.get("provider")
                model = body.get("model")
                max_tokens = body.get("max_tokens", 1000)
                temperature = body.get("temperature", 0.7)
                
                if not prompt:
                    self._send_json_response({"error": "Prompt required"}, 400)
                    return
                
                # Send SSE headers
                self._send_sse_response()
                
                # Pre-trace
                request_id = f"req_{int(time.time() * 1000)}"
                pre_trace_data = {
                    "request_id": request_id,
                    "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                    "provider": provider or ai_manager.default_provider,
                    "stream": True
                }
                merkle_chain.emit_trace("ai_stream_pre", pre_trace_data)
                
                # Stream response
                kwargs = {}
                if model:
                    kwargs["model"] = model
                if max_tokens:
                    kwargs["max_tokens"] = max_tokens
                if temperature is not None:
                    kwargs["temperature"] = temperature
                
                full_response = []
                for chunk in ai_manager.stream(prompt, provider, **kwargs):
                    full_response.append(chunk)
                    event_data = json.dumps({"chunk": chunk})
                    self.wfile.write(f"data: {event_data}\n\n".encode('utf-8'))
                    self.wfile.flush()
                
                # Send done
                self.wfile.write(b"data: [DONE]\n\n")
                
                # Post-trace
                response_text = "".join(full_response)
                snapshot_file = snapshot_response(response_text, {
                    "request_id": request_id,
                    "provider": provider or ai_manager.default_provider,
                    "stream": True
                })
                
                post_trace_data = {
                    "request_id": request_id,
                    "provider": provider or ai_manager.default_provider,
                    "snapshot": snapshot_file,
                    "status": "success",
                    "stream": True
                }
                merkle_chain.emit_trace("ai_stream_post", post_trace_data)
                
            except Exception as e:
                error_data = json.dumps({"error": str(e)})
                self.wfile.write(f"data: {error_data}\n\n".encode('utf-8'))
        
        else:
            self._send_json_response({"error": "Not found"}, 404)


def main():
    """Main server entry point."""
    global ai_manager
    
    # Load AI provider configuration
    config_path = os.path.join(os.path.dirname(__file__), "config", "ai_providers.json")
    
    if not os.path.exists(config_path):
        print(f"Error: Configuration file not found: {config_path}")
        print("Please create config/ai_providers.json")
        sys.exit(1)
    
    try:
        ai_manager = AIProviderManager(config_path)
        print(f"Loaded {len(ai_manager.providers)} AI providers")
        
        # Show provider status
        print("\nProvider Status:")
        print("-" * 50)
        for provider in ai_manager.list_providers():
            status = "✓ Available" if provider["available"] else "✗ Not available"
            print(f"  {provider['name']:15} {status}")
        print("-" * 50)
        
    except Exception as e:
        print(f"Error loading AI providers: {e}")
        sys.exit(1)
    
    # Start server
    port = int(os.environ.get("PORT", 8787))
    server = HTTPServer(('0.0.0.0', port), FlowCoreHandler)
    
    print(f"\n🚀 MrLiou AI Supercomputer v1.0")
    print(f"📡 Server running on http://127.0.0.1:{port}")
    print(f"🔗 Merkle Chain: {merkle_chain.root[:16]}...")
    print(f"📊 Trace Count: {merkle_chain.count}")
    print(f"\nEndpoints:")
    print(f"  GET  /ai/providers  - List available providers")
    print(f"  POST /ai/complete   - Synchronous completion")
    print(f"  POST /ai/stream     - Streaming completion")
    print(f"  GET  /health        - Health check")
    print(f"\nPhilosophy: 怎麼過去，就怎麼回來")
    print(f"\nPress Ctrl+C to stop the server\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        server.shutdown()
        print("Server stopped.")


if __name__ == "__main__":
    main()
