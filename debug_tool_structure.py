#!/usr/bin/env python3
"""
Debug script to see the structure of toolCallRounds
"""

import json

def find_tool_calls_recursively(obj, path=""):
    """Recursively find toolCallRounds in the structure"""
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_path = f"{path}.{key}" if path else key
            if key == "toolCallRounds":
                print(f"Found toolCallRounds at: {new_path}")
                if isinstance(value, list):
                    for i, round_data in enumerate(value):
                        tool_calls = round_data.get("toolCalls", [])
                        print(f"  Round {i + 1}: {len(tool_calls)} tool calls")
                        for j, tool_call in enumerate(tool_calls):
                            name = tool_call.get("name", "unknown")
                            args = tool_call.get("arguments", "{}")
                            print(f"    Tool {j + 1}: {name}")
                            # Parse and show key arguments
                            try:
                                parsed_args = json.loads(args)
                                key_args = {k: v for k, v in parsed_args.items() if k in ["filePath", "cellId", "command", "startLine", "endLine"]}
                                if key_args:
                                    print(f"      Args: {key_args}")
                            except:
                                print(f"      Raw args: {args[:50]}...")
            else:
                find_tool_calls_recursively(value, new_path)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            find_tool_calls_recursively(item, f"{path}[{i}]")

def debug_tool_call_structure(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Total requests: {len(data.get('requests', []))}")
    print("\nSearching for toolCallRounds...")
    find_tool_calls_recursively(data)

if __name__ == "__main__":
    debug_tool_call_structure("add-averages-chat.json")