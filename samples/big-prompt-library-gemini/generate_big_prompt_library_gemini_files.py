#!/usr/bin/env python3
"""
Script to convert markdown files from The Big Prompt Library Gemini CustomInstructions to individual .prompty files.
Usage: python generate_big_prompt_library_gemini_files.py <output_directory>
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
MD_FILES_PATH = "CustomInstructions/Gemini"


def clone_repository():
    """
    Clone the repository to a temporary directory.
    Returns the path to the temporary directory.
    """
    try:
        temp_dir = tempfile.mkdtemp(prefix="big_prompt_library_gemini_")
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


def parse_gemini_markdown_file(file_path):
    """
    Parse a Gemini markdown file and extract name, description, and instruction.
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
        'name': '',
        'description': '',
        'instruction': ''
    }
    
    # Extract name (look for name: field)
    name_match = re.search(r'^name:\s*["\']?([^"\'\n\r]+)["\']?', content, re.MULTILINE)
    if name_match:
        data['name'] = name_match.group(1).strip()
    
    # Extract description
    desc_match = re.search(r'^description:\s*(.+?)(?=\n[a-zA-Z]+:|$)', content, re.MULTILINE | re.DOTALL)
    if desc_match:
        data['description'] = desc_match.group(1).strip()
    
    # Extract instruction (everything after "instruction:")
    instruction_match = re.search(r'^instruction:\s*(.+)', content, re.MULTILINE | re.DOTALL)
    if instruction_match:
        data['instruction'] = instruction_match.group(1).strip()
    
    return data


def extract_name_from_data(name, filename):
    """
    Extract a meaningful name from the data.
    """
    if name and name.strip():
        clean_name = name.strip()
        
        # Remove quotes if present
        clean_name = clean_name.strip('"\'')
        
        if clean_name and len(clean_name) > 1:
            return clean_name
    
    # Fallback to filename parsing
    if filename:
        name_part = filename.replace('.md', '')
        
        # Remove "Gem-" prefix if present
        if name_part.startswith('Gem-'):
            name_part = name_part[4:]
        
        # Convert to readable format
        readable_name = name_part.replace('-', ' ').replace('_', ' ')
        return readable_name.title()
    
    return "AI Assistant"


def generate_filename_from_data(name, filename):
    """
    Generate a filename from the Gemini data.
    """
    # Extract meaningful name
    display_name = extract_name_from_data(name, filename)
    
    # Create base filename from the original filename
    if filename:
        base_name = filename.replace('.md', '').lower()
        # Remove "gem-" prefix and use original structure
        if base_name.startswith('gem-'):
            base_name = base_name[4:]
        base_name = base_name.replace('-', '_').replace(' ', '_')
    else:
        base_name = sanitize_filename(display_name)
    
    return base_name


def create_prompty_content(gemini_data):
    """
    Create the content for a .prompty file based on the Gemini data.
    """
    filename = gemini_data.get('filename', '')
    name = gemini_data.get('name', '')
    description = gemini_data.get('description', '')
    instruction = gemini_data.get('instruction', '')
    
    # Extract a meaningful name
    display_name = extract_name_from_data(name, filename)
    
    # Clean up the name for YAML (quote if it contains special characters)
    clean_name = display_name.replace('"', "'").strip()
    if ':' in clean_name or '`' in clean_name or clean_name != clean_name.strip():
        clean_name = f'"{clean_name}"'
    
    # Create description
    description_parts = []
    if description:
        description_parts.append(description.replace('"', "'"))
    
    # Add source information
    source_info = "Source: The Big Prompt Library Gemini - https://github.com/0xeb/TheBigPromptLibrary"
    description_parts.insert(0, source_info)
    
    # Combine description parts
    clean_description = ". ".join(description_parts).replace('"', "'")
    
    # Prepare tags
    tags = ["unlisted", "big-prompt-library", "gemini"]
    
    # Add category-based tags based on content analysis
    instruction_lower = instruction.lower() if instruction else ""
    name_lower = name.lower() if name else ""
    desc_lower = description.lower() if description else ""
    
    combined_text = f"{instruction_lower} {name_lower} {desc_lower}"
    
    # Add relevant tags based on content
    if any(word in combined_text for word in ['code', 'programming', 'developer', 'coding', 'software']):
        tags.append("programming")
    if any(word in combined_text for word in ['write', 'writing', 'author', 'content', 'editor']):
        tags.append("writing")
    if any(word in combined_text for word in ['design', 'creative', 'art', 'visual', 'brainstorm']):
        tags.append("creative")
    if any(word in combined_text for word in ['business', 'marketing', 'sales', 'strategy', 'career']):
        tags.append("business")
    if any(word in combined_text for word in ['education', 'teach', 'learn', 'tutor', 'coach', 'learning']):
        tags.append("education")
    
    # Format tags for YAML
    tags_yaml = "\n".join([f"  - {tag}" for tag in tags])
    
    # Handle missing instructions
    if not instruction:
        instruction = "You are a helpful AI assistant."
    
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
{instruction}
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
        print(f"Processing {i}/{len(md_files)}: {md_file.name}")
        
        # Parse markdown file
        gemini_data = parse_gemini_markdown_file(md_file)
        if not gemini_data:
            skipped_count += 1
            continue
        
        # Skip if no meaningful content
        if not gemini_data.get('instruction') and not gemini_data.get('name'):
            print(f"  Skipping {md_file.name}: No instruction or name found")
            skipped_count += 1
            continue
        
        # Generate filename
        filename_base = generate_filename_from_data(
            gemini_data.get('name', ''), 
            gemini_data.get('filename', '')
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
        content = create_prompty_content(gemini_data)
        
        # Write to file
        try:
            with open(file_path, 'w', encoding='utf-8') as prompty_file:
                prompty_file.write(content)
            
            created_files.append(file_path)
            processed_count += 1
            print(f"  Created: {file_path}")
            
        except Exception as e:
            print(f"  Error writing file {file_path}: {e}")
            skipped_count += 1
    
    print(f"\nProcessed {len(md_files)} total markdown files")
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
    
    for i, file_path in enumerate(file_list, 1):
        print(f"Validating {i}/{len(file_list)}: {file_path.name}")
        
        is_valid, result = validate_prompty_file(file_path)
        
        if is_valid:
            valid_count += 1
            print(f"  ✅ Valid")
            try:
                if hasattr(result, 'name'):
                    print(f"     Name: {result.name}")
                if hasattr(result, 'description') and result.description:
                    print(f"     Description: {result.description[:80]}...")
            except:
                pass
        else:
            invalid_count += 1
            print(f"  ❌ Invalid")
            print(f"     Error: {result}")
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total files validated: {len(file_list)}")
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
        print("Usage: python generate_big_prompt_library_gemini_files.py <output_directory>")
        print("Example: python generate_big_prompt_library_gemini_files.py ./samples/big-prompt-library-gemini")
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
        
        # Validate generated files
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
