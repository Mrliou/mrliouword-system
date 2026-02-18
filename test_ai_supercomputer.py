#!/usr/bin/env python3
"""
MrLiou AI Supercomputer - Integration Test Suite
=================================================

Comprehensive tests for multi-provider AI support.

Author: MR.liou & Claude
Version: 1.0.0
"""

import os
import sys
import json
import time
import subprocess
import urllib.request
from typing import Dict, Any


class TestResult:
    """Test result tracker."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add_test(self, name: str, passed: bool, message: str = ""):
        """Add test result."""
        self.tests.append({
            "name": name,
            "passed": passed,
            "message": message
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 70)
        print("TEST RESULTS")
        print("=" * 70)
        
        for test in self.tests:
            status = "✓ PASS" if test["passed"] else "✗ FAIL"
            print(f"{status:8} {test['name']}")
            if test["message"]:
                print(f"         {test['message']}")
        
        print("=" * 70)
        print(f"Results: {self.passed}/{self.passed + self.failed} tests passed")
        
        if self.failed == 0:
            print("✅ All tests passed!")
        else:
            print(f"❌ {self.failed} test(s) failed")
        print("=" * 70)
        
        return self.failed == 0


def test_file_structure(results: TestResult):
    """Test 1: File structure exists."""
    required_files = [
        "ai_providers.py",
        "flowcore_loop.py",
        "config/ai_providers.json",
        "config/env_template.txt"
    ]
    
    missing = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing.append(file_path)
    
    if missing:
        results.add_test(
            "File Structure",
            False,
            f"Missing files: {', '.join(missing)}"
        )
    else:
        results.add_test("File Structure", True, "All required files exist")


def test_ai_providers_import(results: TestResult):
    """Test 2: AI providers module can be imported."""
    try:
        import ai_providers
        
        # Check for required classes
        required_classes = [
            'BaseAIProvider',
            'OpenAIProvider',
            'ClaudeProvider',
            'GeminiProvider',
            'OllamaProvider',
            'AzureOpenAIProvider',
            'AIProviderManager'
        ]
        
        missing = []
        for class_name in required_classes:
            if not hasattr(ai_providers, class_name):
                missing.append(class_name)
        
        if missing:
            results.add_test(
                "AI Providers Import",
                False,
                f"Missing classes: {', '.join(missing)}"
            )
        else:
            results.add_test("AI Providers Import", True, "All provider classes found")
            
    except Exception as e:
        results.add_test("AI Providers Import", False, str(e))


def test_provider_manager_config(results: TestResult):
    """Test 3: Provider manager can load configuration."""
    try:
        from ai_providers import AIProviderManager
        
        config_path = "config/ai_providers.json"
        manager = AIProviderManager(config_path)
        
        # Check providers were loaded
        if len(manager.providers) == 0:
            results.add_test(
                "Provider Manager Config",
                False,
                "No providers loaded"
            )
        else:
            results.add_test(
                "Provider Manager Config",
                True,
                f"Loaded {len(manager.providers)} providers"
            )
            
    except Exception as e:
        results.add_test("Provider Manager Config", False, str(e))


def test_provider_availability(results: TestResult):
    """Test 4: Check provider availability."""
    try:
        from ai_providers import AIProviderManager
        
        manager = AIProviderManager("config/ai_providers.json")
        providers = manager.list_providers()
        
        available_count = sum(1 for p in providers if p["available"])
        
        results.add_test(
            "Provider Availability",
            True,
            f"{available_count}/{len(providers)} providers available"
        )
        
    except Exception as e:
        results.add_test("Provider Availability", False, str(e))


def test_environment_variables(results: TestResult):
    """Test 5: Environment variable substitution."""
    try:
        # Set test environment variable
        os.environ['TEST_API_KEY'] = 'test_key_123'
        
        from ai_providers import AIProviderManager
        
        manager = AIProviderManager()
        
        # Test config with env var
        test_config = {
            "default_provider": "test",
            "providers": [
                {
                    "name": "test",
                    "enabled": True,
                    "api_key": "${TEST_API_KEY}"
                }
            ]
        }
        
        manager.config = test_config
        manager._substitute_env_vars(manager.config)
        
        substituted_key = manager.config["providers"][0]["api_key"]
        
        if substituted_key == "test_key_123":
            results.add_test(
                "Environment Variables",
                True,
                "Substitution works correctly"
            )
        else:
            results.add_test(
                "Environment Variables",
                False,
                f"Expected 'test_key_123', got '{substituted_key}'"
            )
        
        # Cleanup
        del os.environ['TEST_API_KEY']
        
    except Exception as e:
        results.add_test("Environment Variables", False, str(e))


def test_cost_calculation(results: TestResult):
    """Test 6: Cost calculation accuracy."""
    try:
        from ai_providers import AIProviderManager
        
        manager = AIProviderManager()
        
        # Test OpenAI GPT-3.5 cost
        usage = {
            "input_tokens": 1000,
            "output_tokens": 1000,
            "total_tokens": 2000
        }
        
        cost = manager.calculate_cost(usage, "gpt-3.5-turbo", "openai")
        
        # Expected: (1000/1M * 0.5) + (1000/1M * 1.5) = 0.0005 + 0.0015 = 0.002
        expected_cost = 0.002
        
        if abs(cost - expected_cost) < 0.0001:
            results.add_test(
                "Cost Calculation",
                True,
                f"Calculated ${cost:.6f} (expected ${expected_cost:.6f})"
            )
        else:
            results.add_test(
                "Cost Calculation",
                False,
                f"Got ${cost:.6f}, expected ${expected_cost:.6f}"
            )
            
    except Exception as e:
        results.add_test("Cost Calculation", False, str(e))


def test_server_startup(results: TestResult):
    """Test 7: Server can start and respond."""
    server_process = None
    
    try:
        # Start server in background
        print("  Starting server...")
        server_process = subprocess.Popen(
            [sys.executable, "flowcore_loop.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "PORT": "8788"}  # Use different port for testing
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Test health endpoint
        url = "http://127.0.0.1:8788/health"
        req = urllib.request.Request(url)
        
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if "status" in data and data["status"] == "ok":
                results.add_test(
                    "Server Startup",
                    True,
                    "Server started and health check passed"
                )
            else:
                results.add_test(
                    "Server Startup",
                    False,
                    "Server started but health check failed"
                )
        
    except Exception as e:
        results.add_test("Server Startup", False, str(e))
    
    finally:
        # Stop server
        if server_process:
            print("  Stopping server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("MRLIOU AI SUPERCOMPUTER - INTEGRATION TEST SUITE")
    print("=" * 70)
    print("\nRunning tests...\n")
    
    results = TestResult()
    
    # Run tests
    test_file_structure(results)
    test_ai_providers_import(results)
    test_provider_manager_config(results)
    test_provider_availability(results)
    test_environment_variables(results)
    test_cost_calculation(results)
    test_server_startup(results)
    
    # Print summary
    all_passed = results.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
