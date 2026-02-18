#!/usr/bin/env python3
"""
MrLiou AI Supercomputer - Interactive Demo Script
==================================================

Demonstrates all AI provider features with live testing.
展示所有 AI 提供者功能，並進行即時測試。

Author: MR.liou & Claude
Version: 1.0.0
"""

import os
import sys
import json
from ai_providers import AIProviderManager


def print_header(text: str, en: str = ""):
    """Print bilingual header."""
    print("\n" + "=" * 70)
    if en:
        print(f"{text} / {en}")
    else:
        print(text)
    print("=" * 70)


def print_section(text: str):
    """Print section header."""
    print(f"\n{text}")
    print("-" * 70)


def demo_list_providers(manager: AIProviderManager):
    """Demo: List all providers."""
    print_header("提供者列表", "Provider List")
    
    providers = manager.list_providers()
    
    print(f"\nTotal providers: {len(providers)}")
    print(f"Default provider: {manager.default_provider}")
    print(f"Fallback enabled: {manager.fallback_enabled}")
    
    if manager.fallback_enabled:
        print(f"Fallback order: {' → '.join(manager.fallback_order)}")
    
    print_section("Provider Status:")
    
    for provider in providers:
        status = "✓ Available" if provider["available"] else "✗ Not available"
        models = ", ".join(provider.get("models", [])[:3])
        print(f"  {provider['name']:15} {status:15} Models: {models}")


def demo_complete(manager: AIProviderManager):
    """Demo: Synchronous completion."""
    print_header("同步完成", "Synchronous Completion")
    
    # Find first available provider
    available_providers = [p for p in manager.list_providers() if p["available"]]
    
    if not available_providers:
        print("❌ No providers available. Please configure API keys.")
        return
    
    provider_name = available_providers[0]["name"]
    
    print(f"\nUsing provider: {provider_name}")
    print("Prompt: 'What is 2+2?'")
    
    try:
        result = manager.complete(
            "What is 2+2? Answer in one sentence.",
            provider=provider_name,
            max_tokens=50
        )
        
        print_section("Response:")
        print(result["text"])
        
        print_section("Usage:")
        usage = result["usage"]
        print(f"  Input tokens:  {usage['input_tokens']}")
        print(f"  Output tokens: {usage['output_tokens']}")
        print(f"  Total tokens:  {usage['total_tokens']}")
        
        # Calculate cost
        cost = manager.calculate_cost(usage, result["model"], provider_name)
        print(f"  Estimated cost: ${cost:.6f} USD")
        
        print("\n✓ Completion successful!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_stream(manager: AIProviderManager):
    """Demo: Streaming completion."""
    print_header("串流完成", "Streaming Completion")
    
    # Find first available provider
    available_providers = [p for p in manager.list_providers() if p["available"]]
    
    if not available_providers:
        print("❌ No providers available. Please configure API keys.")
        return
    
    provider_name = available_providers[0]["name"]
    
    print(f"\nUsing provider: {provider_name}")
    print("Prompt: 'Count from 1 to 5'")
    
    print_section("Streaming response:")
    
    try:
        full_response = []
        for chunk in manager.stream(
            "Count from 1 to 5, one number at a time.",
            provider=provider_name,
            max_tokens=50
        ):
            print(chunk, end="", flush=True)
            full_response.append(chunk)
        
        print("\n\n✓ Streaming completed!")
        print(f"Total characters: {len(''.join(full_response))}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_fallback(manager: AIProviderManager):
    """Demo: Fallback mechanism."""
    print_header("備用機轉測試", "Fallback Mechanism Test")
    
    print(f"Fallback enabled: {manager.fallback_enabled}")
    
    if not manager.fallback_enabled:
        print("❌ Fallback is disabled in configuration")
        return
    
    print(f"Fallback order: {' → '.join(manager.fallback_order)}")
    
    print_section("Testing fallback:")
    
    # Try to get a provider that might not be available
    print("Requesting non-existent provider 'test_provider'...")
    
    try:
        provider = manager.get_provider("test_provider")
        print(f"✓ Fallback successful! Using: {provider.name}")
    except Exception as e:
        print(f"❌ Fallback failed: {e}")


def demo_cost_calculation(manager: AIProviderManager):
    """Demo: Cost calculation."""
    print_header("成本計算", "Cost Calculation")
    
    test_cases = [
        ("openai", "gpt-4", {"input_tokens": 1000, "output_tokens": 1000}),
        ("openai", "gpt-3.5-turbo", {"input_tokens": 1000, "output_tokens": 1000}),
        ("claude", "claude-3-sonnet", {"input_tokens": 1000, "output_tokens": 1000}),
        ("ollama", "llama2", {"input_tokens": 1000, "output_tokens": 1000}),
    ]
    
    print("\nEstimated costs for 1000 input + 1000 output tokens:\n")
    
    for provider, model, usage in test_cases:
        cost = manager.calculate_cost(usage, model, provider)
        print(f"  {provider:10} {model:25} ${cost:.6f}")
    
    print("\n💡 Note: Ollama is free (local execution)")


def demo_error_handling(manager: AIProviderManager):
    """Demo: Error handling."""
    print_header("錯誤處理", "Error Handling")
    
    print("Testing error scenarios:\n")
    
    # Test 1: Empty prompt
    print("1. Empty prompt:")
    try:
        result = manager.complete("", provider="openai")
        print("  ✓ Handled gracefully")
    except Exception as e:
        print(f"  ✓ Caught error: {type(e).__name__}")
    
    # Test 2: Invalid provider
    print("\n2. Invalid provider:")
    try:
        result = manager.complete("test", provider="invalid_provider")
        print("  ✓ Handled gracefully")
    except Exception as e:
        print(f"  ✓ Caught error: {type(e).__name__}")
    
    print("\n✓ Error handling working correctly!")


def demo_configuration(manager: AIProviderManager):
    """Demo: Configuration details."""
    print_header("配置詳情", "Configuration Details")
    
    print("\nLoaded configuration:")
    print(f"  Config file: config/ai_providers.json")
    print(f"  Total providers: {len(manager.providers)}")
    print(f"  Default provider: {manager.default_provider}")
    print(f"  Fallback enabled: {manager.fallback_enabled}")
    
    print_section("Environment Variables:")
    
    env_vars = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "AZURE_OPENAI_API_KEY"
    ]
    
    for var in env_vars:
        value = os.environ.get(var, "")
        status = "✓ Set" if value else "✗ Not set"
        masked = value[:10] + "..." if value else ""
        print(f"  {var:25} {status:10} {masked}")


def main():
    """Run interactive demo."""
    print_header("MRLIOU AI SUPERCOMPUTER - INTERACTIVE DEMO")
    print("MrLiou AI 超級電腦 - 互動式簡報")
    print("\nPhilosophy: 怎麼過去，就怎麼回來")
    print("(How you go, so you return)")
    
    # Load configuration
    config_path = "config/ai_providers.json"
    
    if not os.path.exists(config_path):
        print(f"\n❌ Error: Configuration file not found: {config_path}")
        print("Please create config/ai_providers.json first.")
        sys.exit(1)
    
    try:
        manager = AIProviderManager(config_path)
    except Exception as e:
        print(f"\n❌ Error loading configuration: {e}")
        sys.exit(1)
    
    # Run demos
    demos = [
        ("Configuration", demo_configuration),
        ("List Providers", demo_list_providers),
        ("Cost Calculation", demo_cost_calculation),
        ("Fallback Mechanism", demo_fallback),
        ("Error Handling", demo_error_handling),
        ("Synchronous Completion", demo_complete),
        ("Streaming Completion", demo_stream),
    ]
    
    for name, demo_func in demos:
        try:
            demo_func(manager)
        except KeyboardInterrupt:
            print("\n\n⚠️  Demo interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Demo '{name}' failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print_header("演示完成", "Demo Complete")
    print("\n✓ All demonstrations completed!")
    print("\nNext steps:")
    print("  1. Configure your API keys in .env")
    print("  2. Start the server: python3 flowcore_loop.py")
    print("  3. Test with curl: see examples_curl.sh")
    print("  4. Run tests: python3 test_ai_supercomputer.py")
    print("\nDocumentation: AI_PROVIDERS_README.md")
    print("\nPhilosophy: 怎麼過去，就怎麼回來\n")


if __name__ == "__main__":
    main()
