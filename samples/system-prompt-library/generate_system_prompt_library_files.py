#!/usr/bin/env python3
"""
Script to convert System Prompt Library JSON to individual .prompty files.
Usage: python generate_system_prompt_library_files.py [json_file_path] output_directory
If json_file_path is not provided, it will be downloaded from the default URL.
"""

import json
import os
import sys
import re
from pathlib import Path
import urllib.request
import tempfile
import prompty
import hashlib


# Default URL for the System Prompt Library JSON file
DEFAULT_JSON_URL = "https://huggingface.co/datasets/danielrosehill/System-Prompt-Library-030825/resolve/main/consolidated_prompts.json"


def download_json_file(url, local_path):
    """
    Download JSON file from URL to local path.
    """
    print(f"Downloading JSON from {url}...")
    try:
        urllib.request.urlretrieve(url, local_path)
        print(f"Downloaded to {local_path}")
        return True
    except Exception as e:
        print(f"Error downloading JSON: {e}")
        return False


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


def sanitize_filename(text, max_length=100):
    """
    Convert text to a valid filename by:
    1. Converting to lowercase
    2. Replacing spaces and special characters with underscores
    3. Removing multiple consecutive underscores
    4. Removing leading/trailing underscores
    5. Limiting length to avoid filesystem issues
    """
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces and special characters with underscores
    text = re.sub(r'[^a-z0-9]+', '_', text)
    
    # Remove multiple consecutive underscores
    text = re.sub(r'_+', '_', text)
    
    # Remove leading/trailing underscores
    text = text.strip('_')
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length].rstrip('_')
    
    return text


def extract_role_name(agent_name, system_prompt):
    """
    Extract a meaningful role name from agent name and system prompt.
    """
    # First try to use the agent name if it's meaningful
    if agent_name and agent_name.strip():
        agent_name_clean = agent_name.strip()
        
        # Skip generic or overly long agent names
        if (len(agent_name_clean) > 2 and 
            len(agent_name_clean) < 60 and
            not agent_name_clean.lower().startswith('untitled') and
            agent_name_clean not in ['Agent', 'AI', 'Assistant', 'Bot']):
            return agent_name_clean
    
    # Fallback to extracting from system prompt
    if not system_prompt:
        return agent_name or "AI Assistant"
    
    # Get the first sentence (everything before the first period)
    first_sentence = system_prompt.split('.')[0].strip()
    
    # Convert to both original case and lower case for pattern matching
    original_text = first_sentence
    text_lower = first_sentence.lower()
    
    # Pattern 1: Look for explicit role names
    role_patterns = [
        # "You are [Name]"
        r'you are (?:a |an |the )?([^,\.]+?)(?:,|\.|\s+that|\s+who)',
        # "Act as [Name]"
        r'act as (?:a |an |the )?([^,\.]+?)(?:,|\.|\s+that|\s+who)',
        # "Your role is [Name]"
        r'your (?:role|task|job) is (?:to )?(?:be )?(?:a |an |the )?([^,\.]+?)(?:,|\.|\s+that|\s+who)',
        # "You will act as [Name]"
        r'you will act as (?:a |an |the )?([^,\.]+?)(?:,|\.|\s+that|\s+who)',
        # "You are to [Role]"
        r'you are to (?:be )?(?:a |an |the )?([^,\.]+?)(?:,|\.|\s+that|\s+who)',
        # "Your task is to [Action] as [Role]"
        r'your task is to .+? as (?:a |an |the )?([^,\.]+?)(?:,|\.|\s+that|\s+who)',
        # "You serve as [Role]"
        r'you serve as (?:a |an |the )?([^,\.]+?)(?:,|\.|\s+that|\s+who)',
        # "You function as [Role]"
        r'you function as (?:a |an |the )?([^,\.]+?)(?:,|\.|\s+that|\s+who)',
    ]
    
    for pattern in role_patterns:
        match = re.search(pattern, text_lower)
        if match:
            role = match.group(1).strip()
            
            # Clean up the role name
            role = re.sub(r'\s+', ' ', role)  # Normalize whitespace
            role = role.strip('.,!?()[]')     # Remove punctuation
            
            # Convert to title case but preserve some common capitalizations
            words = role.split()
            title_words = []
            for word in words:
                if word.lower() in ['ai', 'api', 'seo', 'hr', 'it', 'ui', 'ux']:
                    title_words.append(word.upper())
                elif word.lower() in ['bot', 'dr', 'mr', 'ms']:
                    title_words.append(word.capitalize())
                else:
                    title_words.append(word.capitalize())
            
            result = ' '.join(title_words)
            
            # If result is too generic or too long, skip to next pattern
            generic_terms = ['ai', 'assistant', 'bot', 'system', 'model', 'tool', 'helper']
            if result.lower() in generic_terms or len(result) > 50:
                continue
                
            return result
    
    # Fallback: use first few meaningful words from system prompt
    words = original_text.split()
    meaningful_words = []
    skip_words = {'you', 'are', 'a', 'an', 'the', 'please', 'as', 'act', 'your', 'task', 'is', 'to', 'will', 'should', 'must'}
    
    for word in words[:8]:  # Look at first 8 words
        clean_word = word.strip('.,!?()[]').lower()
        if clean_word not in skip_words and len(clean_word) > 2:
            meaningful_words.append(word.strip('.,!?()[]'))
        if len(meaningful_words) >= 3:
            break
    
    if meaningful_words:
        return ' '.join(meaningful_words).title()
    
    # Final fallback
    return agent_name or "AI Assistant"


def generate_filename_from_prompt(agent_name, system_prompt):
    """
    Generate a filename from the agent name and system prompt.
    """
    # Ensure we have strings to work with
    agent_name = agent_name or ''
    system_prompt = system_prompt or ''
    
    # Use agent name as primary source for filename
    if agent_name and agent_name.strip():
        filename_base = agent_name.strip()
    else:
        # Extract meaningful words from system prompt
        words = system_prompt.split()[:5] if system_prompt else ['ai', 'assistant']
        filename_base = ' '.join(words).strip('.,!?')
    
    # Add a short hash for uniqueness
    content_hash = hashlib.md5((agent_name + system_prompt).encode()).hexdigest()[:6]
    filename_with_hash = f"{filename_base}_{content_hash}"
    
    return sanitize_filename(filename_with_hash)


def create_prompty_content(agent_name, description, system_prompt):
    """
    Create the content for a .prompty file based on the System Prompt Library template.
    """
    # Extract a meaningful name from the agent name and system prompt
    role_name = extract_role_name(agent_name, system_prompt)
    
    # Clean up the role name for YAML
    clean_role_name = role_name.replace('"', "'").strip()
    
    # Use description if available, otherwise create one
    if description and description.strip():
        description_text = description.strip()
    else:
        description_text = f"AI assistant that {system_prompt[:100]}..." if system_prompt else "AI assistant"
    
    # Clean description for YAML
    clean_description = f"Source: System Prompt Library - https://huggingface.co/datasets/danielrosehill/System-Prompt-Library-030825. {description_text}".replace('"', "'")
    
    template = f"""---
name: "{clean_role_name}"
description: "{clean_description}"
tags:
  - unlisted 
  - system-prompt-library
inputs:
    user_input:
        type: string
---
system:
{system_prompt}
user:
{{{{user_input}}}}"""
    
    return template


def process_json_to_prompty(json_file_path, output_dir_path):
    """
    Process the System Prompt Library JSON file and create .prompty files.
    """
    # Create output directory if it doesn't exist
    output_dir = Path(output_dir_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    created_files = []
    prompt_counter = {}
    
    print("Reading JSON file and processing prompts...")
    
    # Read and process the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)
    
    prompts = data.get('prompts', [])
    total_prompts = len(prompts)
    
    print(f"Found {total_prompts} prompts in the dataset")
    
    for i, prompt_data in enumerate(prompts, 1):
        if i % 100 == 0:
            print(f"Processed {i}/{total_prompts} prompts...")
        
        agent_name = (prompt_data.get('agentname') or '').strip()
        description = (prompt_data.get('description') or '').strip()
        system_prompt = (prompt_data.get('systemprompt') or '').strip()
        
        # Skip entries without system prompt
        if not system_prompt:
            continue
        
        # Generate filename
        filename_base = generate_filename_from_prompt(agent_name, system_prompt)
        
        # Handle potential filename collisions
        if filename_base in prompt_counter:
            prompt_counter[filename_base] += 1
            filename = f"{filename_base}_{prompt_counter[filename_base]}.prompty"
        else:
            prompt_counter[filename_base] = 0
            filename = f"{filename_base}.prompty"
        
        file_path = output_dir / filename
        
        # Create prompty content
        content = create_prompty_content(agent_name, description, system_prompt)
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as prompty_file:
            prompty_file.write(content)
        
        created_files.append(file_path)
        print(f"Created: {file_path}")
    
    print(f"\nProcessed {total_prompts} total prompts")
    print(f"Generated {len(created_files)} .prompty files")
    
    return created_files


def validate_generated_files(file_list):
    """
    Validate all generated .prompty files.
    """
    print("\n" + "=" * 60)
    print("VALIDATING GENERATED FILES")
    print("=" * 60)
    
    valid_count = 0
    invalid_count = 0
    
    for file_path in file_list:
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
                if hasattr(result, 'description') and result.description:
                    print(f"   Description: {result.description[:100]}...")
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
    print(f"Total files validated: {len(file_list)}")
    print(f"Valid files: {valid_count}")
    print(f"Invalid files: {invalid_count}")
    
    if invalid_count == 0:
        print("🎉 All generated .prompty files are valid!")
        return True
    else:
        print(f"⚠️  {invalid_count} file(s) have validation errors.")
        return False


def main():
    """
    Main function to handle command line arguments and execute the script.
    """
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python generate_system_prompt_library_files.py [json_file_path] <output_directory>")
        print("Examples:")
        print("  python generate_system_prompt_library_files.py ./spl_output")
        print("  python generate_system_prompt_library_files.py consolidated_prompts.json ./spl_output")
        print("\nIf json_file_path is not provided, the JSON will be downloaded from:")
        print(f"  {DEFAULT_JSON_URL}")
        sys.exit(1)
    
    # Determine if JSON file path was provided
    if len(sys.argv) == 2:
        # Only output directory provided, download JSON
        output_dir_path = sys.argv[1]
        json_file_path = None
    else:
        # Both JSON file and output directory provided
        json_file_path = sys.argv[1]
        output_dir_path = sys.argv[2]
    
    # Handle JSON file
    temp_json_file = None
    if json_file_path is None:
        # Download JSON file to temporary location
        temp_json_file = tempfile.NamedTemporaryFile(mode='w+b', suffix='.json', delete=False)
        temp_json_file.close()
        
        if not download_json_file(DEFAULT_JSON_URL, temp_json_file.name):
            print("Failed to download JSON file.")
            sys.exit(1)
        
        json_file_path = temp_json_file.name
    else:
        # Check if provided JSON file exists
        if not os.path.exists(json_file_path):
            print(f"Error: JSON file '{json_file_path}' not found.")
            sys.exit(1)
    
    try:
        # Generate prompty files
        created_files = process_json_to_prompty(json_file_path, output_dir_path)
        print(f"\nGenerated {len(created_files)} .prompty files in '{output_dir_path}'")
        
        # Validate generated files
        validation_success = validate_generated_files(created_files)
        
        # Clean up temporary file if it was created
        if temp_json_file is not None:
            try:
                os.unlink(temp_json_file.name)
                print(f"\nCleaned up temporary JSON file: {temp_json_file.name}")
            except:
                pass
        
        if not validation_success:
            print("\nSome files failed validation. Please check the errors above.")
            sys.exit(1)
        else:
            print(f"\n🎉 Successfully generated and validated all .prompty files!")
        
    except Exception as e:
        print(f"Error processing files: {e}")
        if temp_json_file is not None:
            try:
                os.unlink(temp_json_file.name)
            except:
                pass
        sys.exit(1)


if __name__ == "__main__":
    main() 