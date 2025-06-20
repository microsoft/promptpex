#!/usr/bin/env python3
"""
Integration test script that runs sample test generation using GitHub Models.

This script demonstrates the full PromptPex pipeline working end-to-end
with GitHub Models API.

Requirements:
- Set GITHUB_TOKEN environment variable for GitHub Models access
- Install requirements.txt dependencies

Usage:
  export GITHUB_TOKEN=your_github_token_here
  python integration_test.py
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from promptpex.core import PythonPromptPex
from promptpex.utils.llm_client import LiteLLMClient


def create_test_prompty():
    """Create a simple test prompty file for demonstration."""
    content = """---
name: Email Sentiment Classifier
description: Classify email sentiment as positive, negative, or neutral
inputs:
  email_text:
    type: string
    description: The email text to classify
    default: "Thank you for your excellent service!"
instructions:
  outputRules: |
    - Output must be exactly one word: "positive", "negative", or "neutral"
    - Base classification on overall tone and sentiment
    - Consider context and intent of the message
---
system:
You are an expert email sentiment classifier. Analyze the sentiment of email text.

Rules:
- Output exactly one word: "positive", "negative", or "neutral"
- Consider the overall tone and emotional content
- Neutral means no clear positive or negative sentiment

user:
Classify the sentiment of this email:

{{email_text}}
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.prompty', delete=False) as f:
        f.write(content)
        return f.name


def test_github_models_connection():
    """Test connection to GitHub Models."""
    print("🔍 Testing GitHub Models connection...")
    
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("❌ GITHUB_TOKEN environment variable not set")
        return False
    
    try:
        # Test with a simple GitHub Models call
        client = LiteLLMClient("github:gpt-4o-mini")
        response = client.call_llm(
            "You are a helpful assistant.",
            "Say 'Hello' if you can hear me."
        )
        
        content = response["choices"][0]["message"]["content"]
        if "hello" in content.lower():
            print("✅ GitHub Models connection successful")
            return True
        else:
            print(f"⚠️  Unexpected response: {content}")
            return False
            
    except Exception as e:
        print(f"❌ GitHub Models connection failed: {e}")
        return False


def run_integration_test():
    """Run the full integration test."""
    print("🚀 PromptPex Integration Test with GitHub Models")
    print("="*60)
    
    # Check GitHub Models connection
    if not test_github_models_connection():
        print("\n❌ Integration test failed - Cannot connect to GitHub Models")
        print("Please set GITHUB_TOKEN environment variable and try again.")
        return False
    
    # Create test prompty file
    test_file = create_test_prompty()
    print(f"\n📝 Created test prompty: {test_file}")
    
    try:
        # Initialize PromptPex with GitHub Models
        print("\n🔧 Initializing PromptPex with GitHub Models...")
        pex = PythonPromptPex(
            model="github:gpt-4o-mini",
            generate_tests=True,
            tests_per_rule=2,  # Reduced for faster testing
            runs_per_test=1,
            models_to_test=["github:gpt-4o-mini"]
        )
        
        # Create output directory
        output_dir = tempfile.mkdtemp(prefix="promptpex_test_")
        output_file = os.path.join(output_dir, "test_results.json")
        
        print(f"📁 Output directory: {output_dir}")
        print("\n🔄 Running PromptPex pipeline...")
        
        # Run the pipeline
        results = pex.run(test_file, output_file)
        
        # Check results
        if results.get("status") == "error":
            print(f"❌ Pipeline failed: {results.get('reason')}")
            return False
        
        print("✅ Pipeline completed successfully!")
        
        # Display results summary
        summary = results.get("summary", {})
        print(f"\n📊 Results Summary:")
        print(f"   Rules extracted: {summary.get('total_rules', 0)}")
        print(f"   Inverse rules: {summary.get('inverse_rules', 0)}")
        print(f"   Tests generated: {summary.get('total_tests', 0)}")
        print(f"   Test runs: {summary.get('test_results', 0)}")
        
        if summary.get('grounded_percentage'):
            print(f"   Rules grounded: {summary.get('grounded_percentage')}%")
        if summary.get('valid_percentage'):
            print(f"   Tests valid: {summary.get('valid_percentage')}%")
        if summary.get('compliant_percentage'):
            print(f"   Compliance rate: {summary.get('compliant_percentage')}%")
        
        # Show sample results
        if results.get("rules"):
            print(f"\n📏 Sample Rules:")
            for i, rule in enumerate(results["rules"][:3], 1):
                print(f"   {i}. {rule}")
        
        if results.get("tests"):
            print(f"\n🧪 Sample Tests:")
            for i, test in enumerate(results["tests"][:3], 1):
                print(f"   {i}. Input: {test.get('testinput', '')[:50]}...")
                print(f"      Expected: {test.get('expectedoutput', '')[:50]}...")
        
        # Check output files
        if os.path.exists(output_file):
            print(f"\n📄 Results saved to: {output_file}")
            
            # Check component files
            components_dir = os.path.join(output_dir, "promptpex_components")
            if os.path.exists(components_dir):
                components = os.listdir(components_dir)
                print(f"📁 Component files: {', '.join(components)}")
        
        print(f"\n✨ Integration test completed successfully!")
        print(f"📁 All files saved to: {output_dir}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up test file
        try:
            os.unlink(test_file)
        except:
            pass


if __name__ == "__main__":
    success = run_integration_test()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Tests failed!")
        sys.exit(1)