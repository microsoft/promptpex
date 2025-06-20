#!/usr/bin/env python3
"""
Demo script for the basic Python PromptPex implementation.

This demonstrates the new implementation using:
- litellm for LLM inference (supports multiple providers)
- prompty package for parsing prompty files
- Simplified, idiomatic Python code

To run with actual LLM:
  export OPENAI_API_KEY=your_key_here
  python demo.py
"""

import sys
import os
sys.path.insert(0, '/home/runner/work/promptpex/promptpex/src/python')

from promptpex.core import PythonPromptPex

def create_demo_prompty():
    """Create a simple demo prompty file."""
    demo_content = """---
name: Text Sentiment Analyzer
description: Analyze the sentiment of input text
inputs:
  text: 
    type: string
    description: "The text to analyze for sentiment"
    default: "I love this product!"
instructions:
  outputRules: "The output should be one of: positive, negative, or neutral"
---
system:
You are a sentiment analysis expert. Analyze the sentiment of the provided text.
Return only one word: "positive", "negative", or "neutral".

user:
Analyze the sentiment of this text: {{text}}
"""
    
    demo_file = '/tmp/sentiment_analyzer.prompty'
    with open(demo_file, 'w') as f:
        f.write(demo_content)
    
    return demo_file

def main():
    """Main demo function."""
    print("🚀 PromptPex Python Layer Demo")
    print("=" * 50)
    
    # Check if API key is available
    has_api_key = bool(os.getenv('OPENAI_API_KEY'))
    if not has_api_key:
        print("ℹ️  No OPENAI_API_KEY found. Set it to run with real LLM.")
        print("   Demo will show the pipeline structure without LLM calls.")
        print()
    
    # Create demo prompty file
    demo_file = create_demo_prompty()
    print(f"📝 Created demo prompty file: {demo_file}")
    
    # Initialize PromptPex with the new simplified interface
    pex = PythonPromptPex(
        model="gpt-4o-mini",  # Uses litellm - supports many providers
        generate_tests=True,
        tests_per_rule=2,
        runs_per_test=1,
        models_to_test=["gpt-4o-mini"]  # Could test multiple models
    )
    
    print(f"🔧 Initialized PromptPex with model: gpt-4o-mini")
    print()
    
    # Show the prompty parsing capability
    from promptpex.utils.file_utils import parse_prompty_file, read_prompt_file
    
    content = read_prompt_file(demo_file)
    system_prompt, user_prompt = parse_prompty_file(content)
    
    print("📋 Parsed Prompty File:")
    print(f"   System prompt: {system_prompt[:100]}...")
    print(f"   User prompt: {user_prompt}")
    print()
    
    # Run the pipeline
    output_file = '/tmp/sentiment_demo_results.json'
    
    if has_api_key:
        print("🔄 Running full PromptPex pipeline with LLM...")
        try:
            results = pex.run(demo_file, output_file)
            
            print("✅ Pipeline completed successfully!")
            print(f"   Generated {len(results.get('rules', []))} output rules")
            print(f"   Generated {len(results.get('tests', []))} tests")
            print(f"   Results saved to: {output_file}")
            
            # Show some results
            if results.get('rules'):
                print("\n📏 Sample Output Rules:")
                for i, rule in enumerate(results['rules'][:3]):
                    print(f"   {i+1}. {rule}")
            
        except Exception as e:
            print(f"❌ Pipeline failed: {e}")
            if "authentication" in str(e).lower():
                print("   Try setting OPENAI_API_KEY environment variable")
    else:
        print("⚠️  Skipping LLM calls (no API key)")
        print("   Set OPENAI_API_KEY to run the full pipeline")
    
    print("\n✨ Demo completed!")
    print(f"📁 Demo files: {demo_file}, {output_file}")
    
    # Show the key benefits
    print("\n🎯 Key Features of this Implementation:")
    print("   ✅ Uses litellm (supports 100+ LLM providers)")
    print("   ✅ Uses prompty package for standard parsing")
    print("   ✅ Simplified, idiomatic Python code")
    print("   ✅ Minimal configuration required")
    print("   ✅ Compatible with existing PromptPex interface")

if __name__ == "__main__":
    main()