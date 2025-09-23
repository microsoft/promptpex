#!/usr/bin/env python3
"""
Script to convert markdown files from The Big Prompt Library ChatGPT CustomInstructions to individual .prompty files.
Usage: python generate_big_prompt_library_files.py <output_directory>
"""

import os
import sys
import re
import tempfile
import shutil
from pathlib import Path
import subprocess
import prompty


REPO_URL = "https://github.com/0xeb/TheBigPromptLibrary.git"
MD_FILES_PATH = "CustomInstructions/ChatGPT"


def clone_repository():
    """
    Clone the repository to a temporary directory.
    Returns the path to the temporary directory.
    """
    try:
        temp_dir = tempfile.mkdtemp(prefix="big_prompt_library_")
        print(f"Cloning repository to: {temp_dir}")
        
        result = subprocess.run(
            ["git", "clone", REPO_URL, temp_dir],
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"Successfully cloned repository")
        return temp_dir
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")
        print(f"Git error output: {e.stderr}")
        return None
    except Exception as e:
        print(f"Error cloning repository: {e}")
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


def parse_markdown_file(file_path):
    """
    Parse a markdown file and extract GPT metadata and instructions.
    Returns a dictionary with extracted data.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None
    
    data = {
        'file_path': str(file_path),
        'filename': Path(file_path).name,
        'gpt_url': '',
        'gpt_title': '',
        'gpt_description': '',
        'gpt_instructions': ''
    }
    
    # Extract GPT URL
    url_match = re.search(r'GPT URL:\s*(https://[^\n\r]+)', content)
    if url_match:
        data['gpt_url'] = url_match.group(1).strip()
    
    # Extract GPT Title
    title_match = re.search(r'GPT Title:\s*([^\n\r]+)', content)
    if title_match:
        data['gpt_title'] = title_match.group(1).strip()
    
    # Extract GPT Description
    desc_match = re.search(r'GPT Description:\s*([^\n\r]+)', content)
    if desc_match:
        data['gpt_description'] = desc_match.group(1).strip()
    
    # Extract GPT Instructions (look for content within markdown code blocks)
    instructions_patterns = [
        r'GPT instructions?:\s*```(?:markdown)?\s*(.*?)```',
        r'GPT Instructions?:\s*```(?:markdown)?\s*(.*?)```',
        r'instructions?:\s*```(?:markdown)?\s*(.*?)```',
        r'Instructions?:\s*```(?:markdown)?\s*(.*?)```'
    ]
    
    for pattern in instructions_patterns:
        instructions_match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if instructions_match:
            data['gpt_instructions'] = instructions_match.group(1).strip()
            break
    
    # If no instructions found in code blocks, try to find plain text instructions
    if not data['gpt_instructions']:
        # Look for instructions after "GPT instructions:" without code blocks
        instructions_text_match = re.search(
            r'GPT instructions?:\s*\n\n(.*?)(?=\n\n[A-Z]|\nGPT|\Z)', 
            content, 
            re.DOTALL | re.IGNORECASE
        )
        if instructions_text_match:
            data['gpt_instructions'] = instructions_text_match.group(1).strip()
    
    return data


def extract_name_from_title_or_filename(title, filename):
    """
    Extract a meaningful name from the GPT title or filename.
    """
    if title and title.strip():
        clean_title = title.strip()
        
        # Remove common suffixes and prefixes
        clean_title = re.sub(r'^@', '', clean_title)
        clean_title = re.sub(r'GPT$', '', clean_title, flags=re.IGNORECASE)
        clean_title = re.sub(r'\s*-\s*By\s+.+$', '', clean_title, flags=re.IGNORECASE)
        clean_title = clean_title.strip(' -~')
        
        if clean_title and len(clean_title) > 2:
            return clean_title
    
    # Fallback to filename parsing
    if filename:
        name_part = filename.replace('.md', '')
        
        # Remove the ID prefix (e.g., "00GrDoGJY_")
        parts = name_part.split('_', 1)
        if len(parts) > 1:
            readable_name = parts[1].replace('_', ' ')
            # Clean up common patterns
            readable_name = re.sub(r'\s*-\s*', ' - ', readable_name)
            return readable_name.title()
        else:
            return name_part.replace('_', ' ').title()
    
    return "AI Assistant"


def generate_filename_from_data(title, filename):
    """
    Generate a filename from the GPT data.
    """
    # Extract meaningful name
    name = extract_name_from_title_or_filename(title, filename)
    
    # Get ID from original filename
    file_id = ""
    if filename:
        id_match = re.match(r'^([^_]+)_', filename.replace('.md', ''))
        if id_match:
            file_id = id_match.group(1).lower()
    
    # Create base filename
    if file_id:
        filename_with_id = f"{name}_{file_id}"
    else:
        filename_with_id = name
    
    return sanitize_filename(filename_with_id)


def create_prompty_content(gpt_data):
    """
    Create the content for a .prompty file based on the GPT data.
    """
    filename = gpt_data.get('filename', '')
    gpt_title = gpt_data.get('gpt_title', '')
    gpt_description = gpt_data.get('gpt_description', '')
    gpt_instructions = gpt_data.get('gpt_instructions', '')
    gpt_url = gpt_data.get('gpt_url', '')
    
    # Extract a meaningful name
    name = extract_name_from_title_or_filename(gpt_title, filename)
    
    # Clean up the name for YAML (quote if it contains special characters)
    clean_name = name.replace('"', "'").strip()
    if ':' in clean_name or '`' in clean_name or clean_name != clean_name.strip():
        clean_name = f'"{clean_name}"'
    
    # Create description
    description_parts = []
    if gpt_description:
        description_parts.append(gpt_description.replace('"', "'"))
    
    # Add source information
    source_info = "Source: The Big Prompt Library - https://github.com/0xeb/TheBigPromptLibrary"
    description_parts.insert(0, source_info)
    
    # Combine description parts
    clean_description = ". ".join(description_parts).replace('"', "'")
    
    # Prepare tags
    tags = ["unlisted", "big-prompt-library", "chatgpt"]
    
    # Add category-based tags based on content analysis
    instructions_lower = gpt_instructions.lower() if gpt_instructions else ""
    title_lower = gpt_title.lower() if gpt_title else ""
    
    # Add relevant tags based on content
    if any(word in instructions_lower + title_lower for word in ['code', 'programming', 'developer', 'coding']):
        tags.append("programming")
    if any(word in instructions_lower + title_lower for word in ['write', 'writing', 'author', 'content']):
        tags.append("writing")
    if any(word in instructions_lower + title_lower for word in ['design', 'creative', 'art', 'visual']):
        tags.append("creative")
    if any(word in instructions_lower + title_lower for word in ['business', 'marketing', 'sales', 'strategy']):
        tags.append("business")
    if any(word in instructions_lower + title_lower for word in ['education', 'teach', 'learn', 'tutor']):
        tags.append("education")
    
    # Format tags for YAML
    tags_yaml = "\n".join([f"  - {tag}" for tag in tags])
    
    # Handle missing instructions
    if not gpt_instructions:
        gpt_instructions = "You are a helpful AI assistant."
    
    template = f"""---
name: {clean_name}
description: "{clean_description}"
tags:
{tags_yaml}
inputs:
    user_input:
        type: string
---
system:
{gpt_instructions}
user:
{{{{user_input}}}}"""
    
    return template


def process_markdown_files_to_prompty(repo_path, output_dir_path):
    """
    Process markdown files and create .prompty files.
    """
    md_files_dir = Path(repo_path) / MD_FILES_PATH
    
    if not md_files_dir.exists():
        print(f"Error: Directory {md_files_dir} not found in cloned repository")
        return []
    
    # Find all markdown files
    md_files = list(md_files_dir.glob("*.md"))
    print(f"Found {len(md_files)} markdown files to process")
    
    # Create output directory if it doesn't exist
    output_dir = Path(output_dir_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    created_files = []
    filename_counter = {}
    
    processed_count = 0
    skipped_count = 0
    
    for i, md_file in enumerate(md_files, 1):
        if i % 100 == 0:
            print(f"Processed {i}/{len(md_files)} files...")
        
        # Parse markdown file
        gpt_data = parse_markdown_file(md_file)
        if not gpt_data:
            skipped_count += 1
            continue
        
        # Skip if no meaningful content
        if not gpt_data.get('gpt_instructions') and not gpt_data.get('gpt_title'):
            skipped_count += 1
            continue
        
        # Generate filename
        filename_base = generate_filename_from_data(
            gpt_data.get('gpt_title', ''), 
            gpt_data.get('filename', '')
        )
        
        # Handle potential filename collisions
        if filename_base in filename_counter:
            filename_counter[filename_base] += 1
            filename = f"{filename_base}_{filename_counter[filename_base]}.prompty"
        else:
            filename_counter[filename_base] = 0
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
            
            if i <= 10:  # Show first 10 files being created
                print(f"Created: {file_path}")
            
        except Exception as e:
            print(f"Error writing file {file_path}: {e}")
            skipped_count += 1
    
    print(f"\nProcessed {len(md_files)} total markdown files")
    print(f"Generated {processed_count} .prompty files")
    print(f"Skipped {skipped_count} files")
    
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
    if len(sys.argv) != 2:
        print("Usage: python generate_big_prompt_library_files.py <output_directory>")
        print("Example: python generate_big_prompt_library_files.py ./samples/big-prompt-library-chatgpt")
        sys.exit(1)
    
    output_dir_path = sys.argv[1]
    
    # Clone repository
    repo_path = clone_repository()
    if not repo_path:
        print("Failed to clone repository.")
        sys.exit(1)
    
    try:
        # Generate prompty files
        created_files = process_markdown_files_to_prompty(repo_path, output_dir_path)
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
        # Clean up temporary directory
        if repo_path and os.path.exists(repo_path):
            shutil.rmtree(repo_path)
            print(f"\nCleaned up temporary directory: {repo_path}")


if __name__ == "__main__":
    main()
