#!/usr/bin/env python3
"""
Sample test generation demo that works without external API keys.

This demonstrates the full PromptPex pipeline structure and output format.
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from promptpex.core import PythonPromptPex


def create_sample_prompty():
    """Create a sample prompty file for testing."""
    content = """---
name: Email Tone Classifier
description: Classify the tone of customer service emails
inputs:
  email:
    type: string
    description: Customer service email content
    default: "I'm very disappointed with the service. Please fix this immediately!"
instructions:
  outputRules: |
    - Output must be exactly one word: "friendly", "neutral", "urgent", or "angry"
    - Base classification on language, tone, and urgency indicators
    - Consider emotional words and punctuation
---
system:
You are an expert email tone classifier for customer service.

Classify the tone of customer emails to help route them appropriately.

Rules:
- Output exactly one word: "friendly", "neutral", "urgent", or "angry"
- "friendly" = positive, appreciative, polite language
- "neutral" = matter-of-fact, business-like tone
- "urgent" = time-sensitive but professional
- "angry" = frustrated, demanding, negative language

user:
Classify the tone of this customer email:

{{email}}
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.prompty', delete=False) as f:
        f.write(content)
        return f.name


def run_sample_demo():
    """Run the sample test generation demo."""
    print("🚀 PromptPex Sample Test Generation Demo")
    print("="*60)
    
    print("📝 Creating sample email tone classifier prompty...")
    sample_file = create_sample_prompty()
    
    try:
        # Show the prompt content
        with open(sample_file, 'r') as f:
            content = f.read()
        
        print(f"\n📋 Sample Prompty Content:")
        print("="*40)
        print(content[:400] + "..." if len(content) > 400 else content)
        print("="*40)
        
        # Initialize PromptPex
        print(f"\n🔧 Initializing PromptPex...")
        pex = PythonPromptPex(
            model="gpt-4o-mini",  # Will use mock responses since no API key
            generate_tests=True,
            tests_per_rule=2,
            runs_per_test=1,
            models_to_test=["gpt-4o-mini"]
        )
        
        print("✅ PromptPex initialized successfully")
        
        # Create output directory
        output_dir = tempfile.mkdtemp(prefix="promptpex_demo_")
        output_file = os.path.join(output_dir, "sample_results.json")
        
        print(f"\n📁 Output directory: {output_dir}")
        print("\n🔄 Running PromptPex pipeline...")
        print("   Note: Using mock LLM responses since no API key provided")
        
        # Run the pipeline (will use mock responses)
        results = pex.run(sample_file, output_file)
        
        # Show results
        if results.get("status") == "error":
            print(f"❌ Demo failed: {results.get('reason')}")
            return False
        
        print("✅ Pipeline completed successfully!")
        
        # Display pipeline structure
        print(f"\n📊 Pipeline Structure Demonstration:")
        print(f"   ✅ Step 1: Intent extracted - {len(results.get('intent', ''))>0}")
        print(f"   ✅ Step 2: Input spec generated - {len(results.get('input_spec', {}).get('input_constraints', []))}")
        print(f"   ✅ Step 3: Output rules extracted - {len(results.get('rules', []))}")
        print(f"   ✅ Step 4: Inverse rules generated - {len(results.get('inverse_rules', []))}")
        print(f"   ✅ Step 5: Rule evaluations - {len(results.get('rule_evaluations', []))}")
        print(f"   ✅ Step 6: Tests generated - {len(results.get('tests', []))}")
        print(f"   ✅ Step 7: Baseline tests - {len(results.get('baseline_tests', []))}")
        print(f"   ✅ Step 8: Test validity - {len(results.get('test_validity', []))}")
        print(f"   ✅ Step 9: Test results - {len(results.get('test_results', []))}")
        
        # Show sample outputs (these will be mock responses)
        print(f"\n🔍 Sample Outputs (mock responses):")
        
        if results.get("intent"):
            print(f"   Intent: {results['intent'][:100]}...")
        
        if results.get("rules"):
            print(f"   Rules ({len(results['rules'])}):")
            for i, rule in enumerate(results["rules"][:2], 1):
                print(f"     {i}. {rule[:80]}...")
        
        if results.get("tests"):
            print(f"   Tests ({len(results['tests'])}):")
            for i, test in enumerate(results["tests"][:2], 1):
                print(f"     {i}. Input: {test.get('testinput', '')[:50]}...")
        
        # Check output files
        if os.path.exists(output_file):
            print(f"\n📄 Results saved to: {output_file}")
            
            # Show file size
            file_size = os.path.getsize(output_file)
            print(f"   File size: {file_size:,} bytes")
            
            # Check component files
            components_dir = os.path.join(output_dir, "promptpex_components")
            if os.path.exists(components_dir):
                components = os.listdir(components_dir)
                print(f"   Component files: {', '.join(components)}")
        
        # Show summary
        summary = results.get("summary", {})
        if summary:
            print(f"\n📈 Summary:")
            print(f"   Total rules: {summary.get('total_rules', 0)}")
            print(f"   Total tests: {summary.get('total_tests', 0)}")
            print(f"   Test runs: {summary.get('test_results', 0)}")
        
        print(f"\n✨ Demo completed successfully!")
        print(f"📁 All files available in: {output_dir}")
        
        # Show next steps
        print(f"\n🎯 Next Steps for Real Usage:")
        print(f"   1. Set GITHUB_TOKEN environment variable")
        print(f"   2. Run: python integration_test.py")
        print(f"   3. Or use CLI: python -m promptpex.cli your_prompt.prompty results.json --model github:gpt-4o-mini")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up sample file
        try:
            os.unlink(sample_file)
        except:
            pass


if __name__ == "__main__":
    success = run_sample_demo()
    
    if success:
        print("\n🎉 Demo completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Demo failed!")
        sys.exit(1)