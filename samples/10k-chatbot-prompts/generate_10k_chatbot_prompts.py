#!/usr/bin/env python3
"""
Script to convert 10k chatbot prompts from echohive42 repository to individual .prompty files.
Usage: python generate_10k_chatbot_prompts.py [json_file_path] <output_directory>
"""

import os
import sys
import re
import json
import tempfile
from pathlib import Path
import urllib.request
import prompty
import hashlib


DEFAULT_JSON_URL = "https://raw.githubusercontent.com/echohive42/10-000-chatbot-prompts/refs/heads/main/10_000_chatbot_prompts.json"


def download_json_file(url):
    """
    Download JSON file from URL to a temporary file.
    Returns the path to the temporary file.
    """
    try:
        print(f"Downloading JSON from: {url}")
        temp_file = tempfile.NamedTemporaryFile(mode='w+b', suffix='.json', delete=False)
        urllib.request.urlretrieve(url, temp_file.name)
        print(f"Downloaded to: {temp_file.name}")
        return temp_file.name
    except Exception as e:
        print(f"Error downloading JSON file: {e}")
        return None


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


def extract_name_from_categories(parent_category, subcategory):
    """
    Extract a meaningful name from the parent category and subcategory.
    """
    if subcategory and subcategory.strip():
        # Use subcategory as primary name since it's more specific
        return subcategory.strip()
    elif parent_category and parent_category.strip():
        # Fallback to parent category
        return parent_category.strip()
    else:
        return "AI Assistant"


def generate_filename_from_data(prompt_id, parent_category, subcategory):
    """
    Generate a filename from the prompt data.
    """
    # Use subcategory as primary source for filename
    if subcategory and subcategory.strip():
        filename_base = subcategory.strip()
    elif parent_category and parent_category.strip():
        filename_base = parent_category.strip()
    else:
        filename_base = f"prompt_{prompt_id}"
    
    # Add prompt ID for uniqueness
    filename_with_id = f"{filename_base}_{prompt_id}"
    
    return sanitize_filename(filename_with_id)


def create_prompty_content(prompt_data):
    """
    Create the content for a .prompty file based on the prompt data.
    """
    # Extract fields safely
    prompt_id = prompt_data.get('id', '')
    parent_category = prompt_data.get('parent_category', '')
    subcategory = prompt_data.get('subcategory', '')
    system_message = prompt_data.get('system_message', '')
    keywords = prompt_data.get('keywords', [])
    
    # Extract a meaningful name
    name = extract_name_from_categories(parent_category, subcategory)
    
    # Clean up the name for YAML
    clean_name = name.replace('"', "'").strip()
    
    # Create description
    if parent_category and subcategory:
        description_text = f"AI assistant specializing in {subcategory} within {parent_category}"
    elif subcategory:
        description_text = f"AI assistant specializing in {subcategory}"
    elif parent_category:
        description_text = f"AI assistant specializing in {parent_category}"
    else:
        description_text = f"AI assistant from 10k chatbot prompts collection (ID: {prompt_id})"
    
    # Clean description for YAML and add source info
    clean_description = f"Source: 10k Chatbot Prompts - https://github.com/echohive42/10-000-chatbot-prompts. {description_text}".replace('"', "'")
    
    # Prepare tags
    tags = ["unlisted", "synthetic", "10k-chatbot-prompts"]
    
    # Add category-based tags
    if parent_category:
        tags.append(sanitize_filename(parent_category.lower()))
    if subcategory and subcategory != parent_category:
        tags.append(sanitize_filename(subcategory.lower()))
    
    # Format tags for YAML
    tags_yaml = "\n".join([f"  - {tag}" for tag in tags])
    
    # Create keywords comment if available
    keywords_info = ""
    if keywords:
        keywords_str = ", ".join(keywords[:10])  # Limit to first 10 keywords
        keywords_info = f"\n# Keywords: {keywords_str}"
    
    template = f"""---
name: "{clean_name}"
description: "{clean_description}"
tags:
{tags_yaml}
inputs:
    user_input:
        type: string
---
# Prompt ID: {prompt_id}
# Category: {parent_category} > {subcategory}{keywords_info}
system:
{system_message}
user:
{{{{user_input}}}}"""
    
    return template


def process_json_to_prompty(json_file_path, output_dir_path):
    """
    Process JSON file and create .prompty files.
    """
    # Load JSON data
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            prompts_data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON file {json_file_path}: {e}")
        return []
    
    # Create output directory if it doesn't exist
    output_dir = Path(output_dir_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    created_files = []
    prompt_counter = {}
    
    print(f"Processing {len(prompts_data)} prompts...")
    
    processed_count = 0
    skipped_count = 0
    
    for i, prompt_data in enumerate(prompts_data, 1):
        if i % 1000 == 0:
            print(f"Processed {i}/{len(prompts_data)} prompts...")
        
        # Validate required fields
        system_message = prompt_data.get('system_message', '').strip()
        if not system_message:
            skipped_count += 1
            continue
        
        prompt_id = prompt_data.get('id', f'prompt_{i}')
        parent_category = prompt_data.get('parent_category', '')
        subcategory = prompt_data.get('subcategory', '')
        
        # Generate filename
        filename_base = generate_filename_from_data(prompt_id, parent_category, subcategory)
        
        # Handle potential filename collisions
        if filename_base in prompt_counter:
            prompt_counter[filename_base] += 1
            filename = f"{filename_base}_{prompt_counter[filename_base]}.prompty"
        else:
            prompt_counter[filename_base] = 0
            filename = f"{filename_base}.prompty"
        
        file_path = output_dir / filename
        
        # Create prompty content
        content = create_prompty_content(prompt_data)
        
        # Write to file
        try:
            with open(file_path, 'w', encoding='utf-8') as prompty_file:
                prompty_file.write(content)
            
            created_files.append(file_path)
            processed_count += 1
            
            if i <= 10:  # Show first 10 files being created
                print(f"Created: {file_path}")
            
        except Exception as e:
            print(f"Error writing file {file_path}: {e}")
            skipped_count += 1
    
    print(f"\nProcessed {len(prompts_data)} total prompts")
    print(f"Generated {processed_count} .prompty files")
    print(f"Skipped {skipped_count} prompts")
    
    return created_files


def validate_generated_files(file_list, sample_size=100):
    """
    Validate a sample of generated .prompty files.
    """
    print("\n" + "=" * 60)
    print("VALIDATING GENERATED FILES (SAMPLE)")
    print("=" * 60)
    
    # If we have many files, validate a sample
    if len(file_list) > sample_size:
        import random
        sample_files = random.sample(file_list, sample_size)
        print(f"Validating {sample_size} random files out of {len(file_list)} total files...")
    else:
        sample_files = file_list
        print(f"Validating all {len(file_list)} files...")
    
    valid_count = 0
    invalid_count = 0
    
    for i, file_path in enumerate(sample_files, 1):
        if i % 20 == 0:
            print(f"Validated {i}/{len(sample_files)} files...")
        
        is_valid, result = validate_prompty_file(file_path)
        
        if is_valid:
            valid_count += 1
            
            # Print info for first few files
            if i <= 5:
                print(f"\n✅ Valid: {file_path.name}")
                try:
                    if hasattr(result, 'name'):
                        print(f"   Name: {result.name}")
                    if hasattr(result, 'description') and result.description:
                        print(f"   Description: {result.description[:100]}...")
                except:
                    pass
        else:
            invalid_count += 1
            print(f"\n❌ Invalid: {file_path.name}")
            print(f"   Error: {result}")
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Sample files validated: {len(sample_files)}")
    print(f"Valid files: {valid_count}")
    print(f"Invalid files: {invalid_count}")
    
    if invalid_count == 0:
        print("🎉 All sampled .prompty files are valid!")
        return True
    else:
        print(f"⚠️  {invalid_count} file(s) have validation errors.")
        return False


def main():
    """
    Main function to handle command line arguments and execute the script.
    """
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python generate_10k_chatbot_prompts.py [json_file_path] <output_directory>")
        print("If json_file_path is not provided, will download from:")
        print(f"  {DEFAULT_JSON_URL}")
        print("Example: python generate_10k_chatbot_prompts.py ./samples/10k-chatbot-prompts")
        print("Example: python generate_10k_chatbot_prompts.py /path/to/local.json ./samples/10k-chatbot-prompts")
        sys.exit(1)
    
    if len(sys.argv) == 2:
        # Only output directory provided, download JSON
        json_file_path = None
        output_dir_path = sys.argv[1]
    else:
        # Both JSON file and output directory provided
        json_file_path = sys.argv[1]
        output_dir_path = sys.argv[2]
    
    # Download JSON if not provided locally
    temp_json_file = None
    if not json_file_path:
        temp_json_file = download_json_file(DEFAULT_JSON_URL)
        if not temp_json_file:
            print("Failed to download JSON file.")
            sys.exit(1)
        json_file_path = temp_json_file
    elif not os.path.exists(json_file_path):
        print(f"Error: JSON file '{json_file_path}' not found.")
        sys.exit(1)
    
    try:
        # Generate prompty files
        created_files = process_json_to_prompty(json_file_path, output_dir_path)
        print(f"\nGenerated {len(created_files)} .prompty files in '{output_dir_path}'")
        
        # Validate generated files (sample)
        validation_success = validate_generated_files(created_files)
        
        if not validation_success:
            print("\nSome files failed validation. Please check the errors above.")
        else:
            print(f"\n🎉 Successfully generated and validated .prompty files!")
        
    except Exception as e:
        print(f"Error processing files: {e}")
        sys.exit(1)
    
    finally:
        # Clean up temporary file if we downloaded it
        if temp_json_file and os.path.exists(temp_json_file):
            os.unlink(temp_json_file)
            print(f"\nCleaned up temporary file: {temp_json_file}")


if __name__ == "__main__":
    main() 