#!/usr/bin/env python3
"""
MrLiou AI Supercomputer - Multi-Provider AI Abstraction Layer
================================================================

Zero external dependencies implementation using pure Python standard library.
Supports OpenAI, Claude, Gemini, Ollama, and Azure OpenAI providers.

Author: MR.liou & Claude
Version: 1.0.0
Philosophy: 怎麼過去，就怎麼回來 (How you go, so you return)
"""

import json
import os
import urllib.request
import urllib.error
import urllib.parse
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Iterator, List


class BaseAIProvider(ABC):
    """
    Abstract base class for AI providers.
    All providers must implement these methods.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize provider with configuration."""
        self.config = config
        self.name = config.get("name", "unknown")
        self.enabled = config.get("enabled", True)
        
    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Synchronous completion.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dict with keys: text, model, usage (input_tokens, output_tokens, total_tokens)
        """
        pass
    
    @abstractmethod
    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Streaming completion.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Text chunks as they arrive
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available and configured."""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get provider metadata."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "available": self.is_available(),
            "models": self.config.get("models", [])
        }


class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key", "")
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        self.default_model = config.get("default_model", "gpt-3.5-turbo")
        
    def is_available(self) -> bool:
        return bool(self.api_key and self.enabled)
    
    def complete(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """OpenAI chat completion."""
        if not self.is_available():
            raise ValueError(f"OpenAI provider not available")
        
        model = kwargs.get("model", self.default_model)
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            return {
                "text": result["choices"][0]["message"]["content"],
                "model": result["model"],
                "usage": {
                    "input_tokens": result["usage"]["prompt_tokens"],
                    "output_tokens": result["usage"]["completion_tokens"],
                    "total_tokens": result["usage"]["total_tokens"]
                }
            }
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise RuntimeError(f"OpenAI API error: {e.code} - {error_body}")
        except Exception as e:
            raise RuntimeError(f"OpenAI request failed: {str(e)}")
    
    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """OpenAI streaming completion."""
        if not self.is_available():
            raise ValueError(f"OpenAI provider not available")
        
        model = kwargs.get("model", self.default_model)
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                for line in response:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        line = line[6:]
                        if line == '[DONE]':
                            break
                        try:
                            chunk = json.loads(line)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    yield delta['content']
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            raise RuntimeError(f"OpenAI streaming failed: {str(e)}")


class ClaudeProvider(BaseAIProvider):
    """Anthropic Claude provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key", "")
        self.base_url = config.get("base_url", "https://api.anthropic.com/v1")
        self.default_model = config.get("default_model", "claude-3-sonnet-20240229")
        
    def is_available(self) -> bool:
        return bool(self.api_key and self.enabled)
    
    def complete(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Claude messages completion."""
        if not self.is_available():
            raise ValueError(f"Claude provider not available")
        
        model = kwargs.get("model", self.default_model)
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        
        url = f"{self.base_url}/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            return {
                "text": result["content"][0]["text"],
                "model": result["model"],
                "usage": {
                    "input_tokens": result["usage"]["input_tokens"],
                    "output_tokens": result["usage"]["output_tokens"],
                    "total_tokens": result["usage"]["input_tokens"] + result["usage"]["output_tokens"]
                }
            }
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise RuntimeError(f"Claude API error: {e.code} - {error_body}")
        except Exception as e:
            raise RuntimeError(f"Claude request failed: {str(e)}")
    
    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Claude streaming completion."""
        if not self.is_available():
            raise ValueError(f"Claude provider not available")
        
        model = kwargs.get("model", self.default_model)
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        
        url = f"{self.base_url}/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                for line in response:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        line = line[6:]
                        try:
                            chunk = json.loads(line)
                            if chunk.get('type') == 'content_block_delta':
                                delta = chunk.get('delta', {})
                                if delta.get('type') == 'text_delta':
                                    yield delta.get('text', '')
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            raise RuntimeError(f"Claude streaming failed: {str(e)}")


class GeminiProvider(BaseAIProvider):
    """Google Gemini provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key", "")
        self.base_url = config.get("base_url", "https://generativelanguage.googleapis.com/v1beta")
        self.default_model = config.get("default_model", "gemini-pro")
        
    def is_available(self) -> bool:
        return bool(self.api_key and self.enabled)
    
    def complete(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Gemini generateContent completion."""
        if not self.is_available():
            raise ValueError(f"Gemini provider not available")
        
        model = kwargs.get("model", self.default_model)
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        
        url = f"{self.base_url}/models/{model}:generateContent?key={self.api_key}"
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature
            }
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            # Gemini doesn't always provide token counts
            usage_metadata = result.get("usageMetadata", {})
            
            return {
                "text": text,
                "model": model,
                "usage": {
                    "input_tokens": usage_metadata.get("promptTokenCount", 0),
                    "output_tokens": usage_metadata.get("candidatesTokenCount", 0),
                    "total_tokens": usage_metadata.get("totalTokenCount", 0)
                }
            }
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise RuntimeError(f"Gemini API error: {e.code} - {error_body}")
        except Exception as e:
            raise RuntimeError(f"Gemini request failed: {str(e)}")
    
    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Gemini streaming completion."""
        if not self.is_available():
            raise ValueError(f"Gemini provider not available")
        
        model = kwargs.get("model", self.default_model)
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        
        url = f"{self.base_url}/models/{model}:streamGenerateContent?key={self.api_key}"
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature
            }
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                for line in response:
                    line = line.decode('utf-8').strip()
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "candidates" in chunk:
                                parts = chunk["candidates"][0]["content"]["parts"]
                                for part in parts:
                                    if "text" in part:
                                        yield part["text"]
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            raise RuntimeError(f"Gemini streaming failed: {str(e)}")


class OllamaProvider(BaseAIProvider):
    """Ollama local models provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.default_model = config.get("default_model", "llama2")
        
    def is_available(self) -> bool:
        """Check if Ollama server is running."""
        if not self.enabled:
            return False
        
        try:
            url = f"{self.base_url}/api/tags"
            req = urllib.request.Request(url, method='GET')
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except:
            return False
    
    def complete(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Ollama generate completion."""
        if not self.is_available():
            raise ValueError(f"Ollama provider not available")
        
        model = kwargs.get("model", self.default_model)
        temperature = kwargs.get("temperature", 0.7)
        
        url = f"{self.base_url}/api/generate"
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            return {
                "text": result["response"],
                "model": result["model"],
                "usage": {
                    "input_tokens": result.get("prompt_eval_count", 0),
                    "output_tokens": result.get("eval_count", 0),
                    "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
                }
            }
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise RuntimeError(f"Ollama API error: {e.code} - {error_body}")
        except Exception as e:
            raise RuntimeError(f"Ollama request failed: {str(e)}")
    
    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Ollama streaming completion."""
        if not self.is_available():
            raise ValueError(f"Ollama provider not available")
        
        model = kwargs.get("model", self.default_model)
        temperature = kwargs.get("temperature", 0.7)
        
        url = f"{self.base_url}/api/generate"
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature
            }
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                for line in response:
                    line = line.decode('utf-8').strip()
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "response" in chunk:
                                yield chunk["response"]
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            raise RuntimeError(f"Ollama streaming failed: {str(e)}")


class AzureOpenAIProvider(BaseAIProvider):
    """Azure OpenAI provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key", "")
        self.endpoint = config.get("endpoint", "")
        self.deployment = config.get("deployment", "")
        self.api_version = config.get("api_version", "2023-05-15")
        
    def is_available(self) -> bool:
        return bool(self.api_key and self.endpoint and self.deployment and self.enabled)
    
    def complete(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Azure OpenAI chat completion."""
        if not self.is_available():
            raise ValueError(f"Azure OpenAI provider not available")
        
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        
        url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            return {
                "text": result["choices"][0]["message"]["content"],
                "model": self.deployment,
                "usage": {
                    "input_tokens": result["usage"]["prompt_tokens"],
                    "output_tokens": result["usage"]["completion_tokens"],
                    "total_tokens": result["usage"]["total_tokens"]
                }
            }
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise RuntimeError(f"Azure OpenAI API error: {e.code} - {error_body}")
        except Exception as e:
            raise RuntimeError(f"Azure OpenAI request failed: {str(e)}")
    
    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Azure OpenAI streaming completion."""
        if not self.is_available():
            raise ValueError(f"Azure OpenAI provider not available")
        
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        
        url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                for line in response:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        line = line[6:]
                        if line == '[DONE]':
                            break
                        try:
                            chunk = json.loads(line)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    yield delta['content']
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            raise RuntimeError(f"Azure OpenAI streaming failed: {str(e)}")


class AIProviderManager:
    """
    Manager for multiple AI providers with fallback support.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize provider manager.
        
        Args:
            config_path: Path to ai_providers.json config file
        """
        self.providers: Dict[str, BaseAIProvider] = {}
        self.config = {}
        self.fallback_enabled = False
        self.fallback_order: List[str] = []
        
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str):
        """Load configuration from JSON file with environment variable substitution."""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Substitute environment variables
        self._substitute_env_vars(self.config)
        
        # Initialize providers
        for provider_config in self.config.get("providers", []):
            self._init_provider(provider_config)
        
        # Set fallback configuration
        fallback_config = self.config.get("fallback", {})
        self.fallback_enabled = fallback_config.get("enabled", False)
        self.fallback_order = fallback_config.get("order", [])
        
        # Set default provider
        self.default_provider = self.config.get("default_provider", "openai")
    
    def _substitute_env_vars(self, obj):
        """Recursively substitute environment variables in config."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    env_var = value[2:-1]
                    obj[key] = os.environ.get(env_var, "")
                elif isinstance(value, (dict, list)):
                    self._substitute_env_vars(value)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, str) and item.startswith("${") and item.endswith("}"):
                    env_var = item[2:-1]
                    obj[i] = os.environ.get(env_var, "")
                elif isinstance(item, (dict, list)):
                    self._substitute_env_vars(item)
    
    def _init_provider(self, config: Dict[str, Any]):
        """Initialize a provider from configuration."""
        provider_name = config.get("name", "").lower()
        
        provider_classes = {
            "openai": OpenAIProvider,
            "claude": ClaudeProvider,
            "gemini": GeminiProvider,
            "ollama": OllamaProvider,
            "azure": AzureOpenAIProvider
        }
        
        provider_class = provider_classes.get(provider_name)
        if provider_class:
            self.providers[provider_name] = provider_class(config)
    
    def get_provider(self, name: Optional[str] = None) -> BaseAIProvider:
        """Get a provider by name, with fallback support."""
        if name is None:
            name = self.default_provider
        
        name = name.lower()
        
        # Try requested provider first
        if name in self.providers:
            provider = self.providers[name]
            if provider.is_available():
                return provider
        
        # Try fallback if enabled
        if self.fallback_enabled:
            for fallback_name in self.fallback_order:
                if fallback_name in self.providers:
                    provider = self.providers[fallback_name]
                    if provider.is_available():
                        return provider
        
        raise ValueError(f"No available provider found (requested: {name})")
    
    def list_providers(self) -> List[Dict[str, Any]]:
        """List all providers and their status."""
        return [provider.get_info() for provider in self.providers.values()]
    
    def complete(self, prompt: str, provider: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Complete using specified or default provider."""
        selected_provider = self.get_provider(provider)
        return selected_provider.complete(prompt, **kwargs)
    
    def stream(self, prompt: str, provider: Optional[str] = None, **kwargs) -> Iterator[str]:
        """Stream completion using specified or default provider."""
        selected_provider = self.get_provider(provider)
        return selected_provider.stream(prompt, **kwargs)
    
    def calculate_cost(self, usage: Dict[str, int], model: str, provider_name: str) -> float:
        """
        Calculate estimated cost in USD based on token usage.
        
        Args:
            usage: Dict with input_tokens, output_tokens, total_tokens
            model: Model name used
            provider_name: Provider name
            
        Returns:
            Estimated cost in USD
        """
        # Pricing per 1M tokens (approximate as of 2024)
        pricing = {
            "openai": {
                "gpt-4": {"input": 30.0, "output": 60.0},
                "gpt-4-turbo": {"input": 10.0, "output": 30.0},
                "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
            },
            "claude": {
                "claude-3-opus": {"input": 15.0, "output": 75.0},
                "claude-3-sonnet": {"input": 3.0, "output": 15.0},
                "claude-3-haiku": {"input": 0.25, "output": 1.25},
            },
            "gemini": {
                "gemini-pro": {"input": 0.5, "output": 1.5},
            },
            "ollama": {
                "default": {"input": 0.0, "output": 0.0},  # Local, free
            },
            "azure": {
                "default": {"input": 10.0, "output": 30.0},  # Varies by deployment
            }
        }
        
        provider_pricing = pricing.get(provider_name.lower(), {})
        
        # Find matching model or use default
        model_pricing = None
        for model_key, prices in provider_pricing.items():
            if model_key in model.lower():
                model_pricing = prices
                break
        
        if not model_pricing:
            # Use first available pricing as default
            model_pricing = next(iter(provider_pricing.values()), {"input": 0.0, "output": 0.0})
        
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        
        input_cost = (input_tokens / 1_000_000) * model_pricing["input"]
        output_cost = (output_tokens / 1_000_000) * model_pricing["output"]
        
        return round(input_cost + output_cost, 6)


if __name__ == "__main__":
    # Simple test
    print("MrLiou AI Providers - Testing availability")
    print("=" * 50)
    
    # Create test config
    test_config = {
        "default_provider": "openai",
        "providers": [
            {
                "name": "openai",
                "enabled": True,
                "api_key": os.environ.get("OPENAI_API_KEY", ""),
                "models": ["gpt-3.5-turbo", "gpt-4"]
            },
            {
                "name": "ollama",
                "enabled": True,
                "base_url": "http://localhost:11434",
                "models": ["llama2", "mistral"]
            }
        ],
        "fallback": {
            "enabled": True,
            "order": ["openai", "ollama"]
        }
    }
    
    # Test providers
    manager = AIProviderManager()
    manager.config = test_config
    for provider_config in test_config["providers"]:
        manager._init_provider(provider_config)
    
    for provider_info in manager.list_providers():
        status = "✓ Available" if provider_info["available"] else "✗ Not available"
        print(f"{provider_info['name']:15} {status}")
    
    print("\nPhilosophy: 怎麼過去，就怎麼回來")
