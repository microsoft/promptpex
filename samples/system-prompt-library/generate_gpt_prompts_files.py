#!/usr/bin/env python3
"""
Script to convert GPT system prompts from GitHub repository to individual .prompty files.
Usage: python generate_gpt_prompts_files.py <repository_path> <output_directory>
"""

import os
import sys
import re
from pathlib import Path
import prompty
import hashlib


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


def parse_gpt_markdown_file(file_path):
    """
    Parse a GPT markdown file and extract the relevant information.
    Returns a dictionary with parsed data.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None
    
    # Initialize data dictionary
    data = {
        'url': '',
        'title': '',
        'description': '',
        'instructions': '',
        'filename': file_path.name
    }
    
    # Extract GPT URL
    url_match = re.search(r'GPT URL: (https://[^\n]+)', content)
    if url_match:
        data['url'] = url_match.group(1).strip()
    
    # Extract GPT Title
    title_match = re.search(r'GPT Title: (.+)', content)
    if title_match:
        data['title'] = title_match.group(1).strip()
    
    # Extract GPT Description
    desc_match = re.search(r'GPT Description: (.+)', content)
    if desc_match:
        data['description'] = desc_match.group(1).strip()
    
    # Extract GPT instructions (everything after "GPT instructions:")
    instructions_match = re.search(r'GPT instructions:\s*```(?:markdown)?\s*(.*?)```', content, re.DOTALL)
    if instructions_match:
        data['instructions'] = instructions_match.group(1).strip()
    else:
        # Fallback: try to find instructions without markdown code blocks
        instructions_match = re.search(r'GPT instructions:\s*(.+)', content, re.DOTALL)
        if instructions_match:
            data['instructions'] = instructions_match.group(1).strip()
    
    # If no instructions found, skip this file
    if not data['instructions']:
        return None
    
    return data


def extract_name_from_title_or_filename(title, filename):
    """
    Extract a meaningful name from the GPT title or filename.
    """
    if title and title.strip():
        # Clean up the title
        clean_title = title.strip()
        
        # Remove common prefixes and special characters
        clean_title = re.sub(r'^@', '', clean_title)  # Remove @ prefix
        clean_title = re.sub(r'GPT$', '', clean_title, flags=re.IGNORECASE)  # Remove GPT suffix
        clean_title = re.sub(r'\s*-\s*By\s+.+$', '', clean_title, flags=re.IGNORECASE)  # Remove "By Author"
        clean_title = clean_title.strip(' -~')
        
        if clean_title and len(clean_title) > 2:
            return clean_title
    
    # Fallback to filename parsing
    if filename:
        # Remove file extension
        name_part = filename.replace('.md', '')
        
        # Try to extract readable name from filename
        # Format is usually: ID_Name_With_Underscores.md
        parts = name_part.split('_', 1)  # Split on first underscore
        if len(parts) > 1:
            readable_name = parts[1].replace('_', ' ')
            return readable_name.title()
    
    return "GPT Assistant"


def generate_filename_from_data(title, filename):
    """
    Generate a filename from the GPT data.
    """
    # Use title as primary source for filename
    if title and title.strip():
        # Extract the clean name for filename
        clean_name = extract_name_from_title_or_filename(title, filename)
        filename_base = clean_name
    else:
        # Extract meaningful words from filename
        name_part = filename.replace('.md', '')
        parts = name_part.split('_', 1)
        if len(parts) > 1:
            filename_base = parts[1].replace('_', ' ')
        else:
            filename_base = name_part
    
    # Add a short hash for uniqueness
    content_hash = hashlib.md5((title + filename).encode()).hexdigest()[:6]
    filename_with_hash = f"{filename_base}_{content_hash}"
    
    return sanitize_filename(filename_with_hash)


def create_prompty_content(gpt_data):
    """
    Create the content for a .prompty file based on the GPT data.
    """
    # Extract a meaningful name
    name = extract_name_from_title_or_filename(gpt_data['title'], gpt_data['filename'])
    
    # Clean up the name for YAML
    clean_name = name.replace('"', "'").strip()
    
    # Create description
    if gpt_data['description']:
        description_text = gpt_data['description']
    else:
        description_text = f"Custom GPT assistant from {gpt_data['filename']}"
    
    # Clean description for YAML and add source info
    clean_description = f"Source: ChatGPT Custom GPTs - https://github.com/LouisShark/chatgpt_system_prompt. {description_text}".replace('"', "'")
    
    # Add URL if available
    url_info = ""
    if gpt_data['url']:
        url_info = f"\n# Original GPT URL: {gpt_data['url']}"
    
    template = f"""---
name: "{clean_name}"
description: "{clean_description}"
tags:
  - unlisted 
  - chatgpt-custom-gpts
inputs:
    user_input:
        type: string
---{url_info}
system:
{gpt_data['instructions']}
user:
{{{{user_input}}}}"""
    
    return template


def process_gpt_files_to_prompty(repo_path, output_dir_path):
    """
    Process GPT markdown files and create .prompty files.
    """
    # Path to the gpts folder
    gpts_path = Path(repo_path) / "prompts" / "gpts"
    
    if not gpts_path.exists():
        print(f"Error: GPTs folder not found at {gpts_path}")
        return []
    
    # Create output directory if it doesn't exist
    output_dir = Path(output_dir_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    created_files = []
    prompt_counter = {}
    
    print(f"Processing GPT files from {gpts_path}...")
    
    # Get all markdown files
    md_files = list(gpts_path.glob("*.md"))
    total_files = len(md_files)
    
    print(f"Found {total_files} markdown files")
    
    processed_count = 0
    skipped_count = 0
    
    for i, md_file in enumerate(md_files, 1):
        if i % 100 == 0:
            print(f"Processed {i}/{total_files} files...")
        
        # Parse the markdown file
        gpt_data = parse_gpt_markdown_file(md_file)
        
        if not gpt_data:
            skipped_count += 1
            continue
        
        # Generate filename
        filename_base = generate_filename_from_data(gpt_data['title'], gpt_data['filename'])
        
        # Handle potential filename collisions
        if filename_base in prompt_counter:
            prompt_counter[filename_base] += 1
            filename = f"{filename_base}_{prompt_counter[filename_base]}.prompty"
        else:
            prompt_counter[filename_base] = 0
            filename = f"{filename_base}.prompty"
        
        file_path = output_dir / filename
        
        # Create prompty content
        content = create_prompty_content(gpt_data)
        
        # Write to file
        try:
            with open(file_path, 'w', encoding='utf-8') as prompty_file:
                prompty_file.write(content)
            
            created_files.append(file_path)
            processed_count += 1
            print(f"Created: {file_path}")
            
        except Exception as e:
            print(f"Error writing file {file_path}: {e}")
            skipped_count += 1
    
    print(f"\nProcessed {total_files} total files")
    print(f"Generated {processed_count} .prompty files")
    print(f"Skipped {skipped_count} files")
    
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
    if len(sys.argv) != 3:
        print("Usage: python generate_gpt_prompts_files.py <repository_path> <output_directory>")
        print("Example: python generate_gpt_prompts_files.py /tmp/chatgpt_system_prompt ./samples/chatgpt-custom-gpts")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    output_dir_path = sys.argv[2]
    
    # Check if repository path exists
    if not os.path.exists(repo_path):
        print(f"Error: Repository path '{repo_path}' not found.")
        sys.exit(1)
    
    try:
        # Generate prompty files
        created_files = process_gpt_files_to_prompty(repo_path, output_dir_path)
        print(f"\nGenerated {len(created_files)} .prompty files in '{output_dir_path}'")
        
        # Validate generated files
        validation_success = validate_generated_files(created_files)
        
        if not validation_success:
            print("\nSome files failed validation. Please check the errors above.")
            sys.exit(1)
        else:
            print(f"\n🎉 Successfully generated and validated all .prompty files!")
        
    except Exception as e:
        print(f"Error processing files: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 