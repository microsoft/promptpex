#!/usr/bin/env python3
"""
Test runner script for PromptPex Python implementation.

This script runs unit tests and optionally integration tests.

Usage:
  python run_tests.py               # Run unit tests only
  python run_tests.py --integration # Run unit and integration tests
  python run_tests.py --help        # Show help
"""

import sys
import os
import subprocess
import argparse


def run_unit_tests():
    """Run unit tests using pytest."""
    print("🧪 Running unit tests...")
    
    # Change to the Python directory
    python_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(python_dir)
    
    # Run pytest
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v", 
        "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


def run_integration_tests():
    """Run integration tests."""
    print("\n🔗 Running integration tests...")
    
    # Check if GitHub token is available
    if not os.getenv("GITHUB_TOKEN"):
        print("⚠️  GITHUB_TOKEN not set, skipping integration tests")
        print("   Set GITHUB_TOKEN to run integration tests with GitHub Models")
        return True
    
    # Run integration test
    python_dir = os.path.dirname(os.path.abspath(__file__))
    integration_script = os.path.join(python_dir, "integration_test.py")
    
    result = subprocess.run([sys.executable, integration_script], 
                          capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Run PromptPex Python tests")
    parser.add_argument("--integration", action="store_true", 
                       help="Run integration tests in addition to unit tests")
    parser.add_argument("--unit-only", action="store_true",
                       help="Run only unit tests (default)")
    
    args = parser.parse_args()
    
    print("🚀 PromptPex Python Test Runner")
    print("="*40)
    
    # Run unit tests
    unit_success = run_unit_tests()
    
    if not unit_success:
        print("\n❌ Unit tests failed!")
        return 1
    
    print("\n✅ Unit tests passed!")
    
    # Run integration tests if requested
    if args.integration:
        integration_success = run_integration_tests()
        
        if not integration_success:
            print("\n❌ Integration tests failed!")
            return 1
        
        print("\n✅ Integration tests passed!")
    
    print("\n🎉 All tests completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())