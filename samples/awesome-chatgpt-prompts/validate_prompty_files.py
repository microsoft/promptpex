#!/usr/bin/env python3
"""
Script to validate all .prompty files in a directory.
Usage: python validate_prompty_files.py <directory_path>
"""

import os
import sys
from pathlib import Path
import prompty


def validate_prompty_file(file_path):
    """
    Validate a single .prompty file using the prompty library.
    Returns (is_valid, error_message or prompty_object)
    """
    try:
        p = prompty.load(str(file_path))
        return True, p
    except Exception as e:
        return False, str(e)


def validate_directory(directory_path):
    """
    Validate all .prompty files in the given directory.
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        print(f"Error: Directory '{directory_path}' does not exist.")
        return False
    
    if not directory.is_dir():
        print(f"Error: '{directory_path}' is not a directory.")
        return False
    
    # Find all .prompty files
    prompty_files = list(directory.glob("*.prompty"))
    
    if not prompty_files:
        print(f"No .prompty files found in '{directory_path}'")
        return True
    
    print(f"Found {len(prompty_files)} .prompty files in '{directory_path}'")
    print("=" * 60)
    
    valid_count = 0
    invalid_count = 0
    
    for file_path in sorted(prompty_files):
        print(f"\nValidating: {file_path.name}")
        print("-" * 40)
        
        is_valid, result = validate_prompty_file(file_path)
        
        if is_valid:
            print("✅ Valid prompty file!")
            valid_count += 1
            
            # Print some basic info about the prompty file
            try:
                if hasattr(result, 'name'):
                    print(f"   Name: {result.name}")
                if hasattr(result, 'description'):
                    print(f"   Description: {result.description}")
                if hasattr(result, 'tags') and result.tags:
                    print(f"   Tags: {', '.join(result.tags)}")
            except:
                # If we can't access these attributes, just continue
                pass
                
        else:
            print("❌ Invalid prompty file!")
            print(f"   Error: {result}")
            invalid_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total files checked: {len(prompty_files)}")
    print(f"Valid files: {valid_count}")
    print(f"Invalid files: {invalid_count}")
    
    if invalid_count == 0:
        print("🎉 All .prompty files are valid!")
        return True
    else:
        print(f"⚠️  {invalid_count} file(s) have validation errors.")
        return False


def main():
    """
    Main function to handle command line arguments and execute the script.
    """
    if len(sys.argv) != 2:
        print("Usage: python validate_prompty_files.py <directory_path>")
        print("Example: python validate_prompty_files.py ./samples/awesome-chatgpt-prompts/")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    
    try:
        success = validate_directory(directory_path)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error during validation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 