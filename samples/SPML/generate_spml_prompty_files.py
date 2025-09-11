#!/usr/bin/env python3
"""
Script to convert SPML prompt injection CSV to individual .prompty files.
Usage: python generate_spml_prompty_files.py [csv_file_path] output_directory
If csv_file_path is not provided, it will be downloaded from the default URL.
"""

import csv
import os
import sys
import re
from pathlib import Path
import urllib.request
import tempfile
import prompty
import hashlib


# Default URL for the SPML prompt injection CSV file
DEFAULT_CSV_URL = "https://huggingface.co/datasets/reshabhs/SPML_Chatbot_Prompt_Injection/resolve/main/spml_prompt_injection.csv"


def download_csv_file(url, local_path):
    """
    Download CSV file from URL to local path.
    """
    print(f"Downloading CSV from {url}...")
    try:
        urllib.request.urlretrieve(url, local_path)
        print(f"Downloaded to {local_path}")
        return True
    except Exception as e:
        print(f"Error downloading CSV: {e}")
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


def generate_filename_from_system_prompt(system_prompt, extracted_name):
    """
    Generate a filename from the extracted role name.
    Uses the extracted name as the primary filename with hash for uniqueness if needed.
    """
    # Use the extracted name as the base
    if extracted_name:
        filename_base = extracted_name
    else:
        # Fallback to first few words
        words = system_prompt.split()[:5]
        filename_base = ' '.join(words).strip('.,!?')
    
    # Add a short hash for uniqueness (shorter since names are more descriptive now)
    hash_part = hashlib.md5(system_prompt.encode()).hexdigest()[:6]
    filename_with_hash = f"{filename_base}_{hash_part}"
    
    return sanitize_filename(filename_with_hash)


def extract_role_name(system_prompt):
    """
    Try to extract a role name from the system prompt for the prompty name.
    Focus on finding bot names and roles before the first period/sentence end.
    """
    # Get the first sentence (everything before the first period)
    first_sentence = system_prompt.split('.')[0].strip()
    
    # Convert to both original case and lower case for pattern matching
    original_text = first_sentence
    text_lower = first_sentence.lower()
    
    # Pattern 1: Look for explicit bot names (capitalized words that look like names)
    # Examples: "Dr. AIda", "FitBuddy", "MediBot", "TravelSmart", etc.
    bot_name_patterns = [
        r'\b([A-Z][a-z]*[A-Z][a-zA-Z]*)\b',  # CamelCase like FitBuddy, TravelSmart
        r'\b(Dr\.\s*[A-Z][a-zA-Z]+)\b',      # Dr. AIda, Dr. Smith
        r'\b([A-Z][a-z]+Bot)\b',             # MediBot, ChefBot, etc.
        r'\b([A-Z][a-z]*-[A-Z][a-z]*)\b',    # Learn-Bot, etc.
        r'\b([A-Z][a-z]+[A-Z][a-z]+)\b',     # CamelCase names
        r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b',  # "Happy Helper", "Hire Genius"
    ]
    
    for pattern in bot_name_patterns:
        matches = re.findall(pattern, original_text)
        if matches:
            # Return the first capitalized name found
            return matches[0]
    
    # Pattern 2: Look for role descriptions with proper titles
    role_patterns = [
        # "You are [Name], a/an [role]"
        r'you are ([^,]+?),?\s+(?:a|an|the)\s+',
        # "You are a [Role] named [Name]"
        r'you are (?:a|an|the)\s+[^,]+?\s+named\s+([^,]+)',
        # "You are [Role Name] Bot/Assistant/Advisor"
        r'you are (?:a|an|the)?\s*([^,]+?\s+(?:bot|assistant|advisor|chatbot))',
        # "Taking on the role of [Name]"
        r'taking on the role of ([^,]+)',
        # "You are now [Name]"
        r'you are now ([^,]+)',
        # "Act as [Name]"
        r'act as (?:a|an|the)?\s*([^,]+)',
        # "You will act as [Name]"
        r'you will act as (?:a|an|the)?\s*([^,]+)',
        # "As [Name], your role is" or "As the [Name], your role is"
        r'as (?:the\s+)?([^,]+),\s*your role is',
        # "You are interacting with [Name]"
        r'you are (?:now )?interacting with ([^,]+)',
        # "You are now operating as [Name]"
        r'you are now operating as (?:a|an|the)?\s*([^,]+)',
        # "Assume the role of [Name]"
        r'assume the role of (?:a|an|the)?\s*([^,]+)',
        # "You are to embody [Name]"
        r'you are to embody (?:the role of )?(?:a|an|the)?\s*([^,]+)',
        # "You are designated as [Name]"
        r'you are designated as ([^,]+)',
        # "You are [Name] whose role"
        r'you are ([^,]+?)\s+whose role',
        # "[Name] is a chatbot"
        r'^([^,]+?)\s+is a chatbot',
        # "Please act as [Name]"
        r'please act as (?:a|an|the)?\s*([^,]+)',
        # Simple "You are [Name]" at the beginning
        r'^you are ([A-Z][a-zA-Z\s]+?)(?:,|\.|$)',
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
                if word.lower() in ['bot', 'ai', 'dr', 'mr', 'ms']:
                    title_words.append(word.capitalize())
                elif word.lower() == 'chatgpt':
                    title_words.append('ChatGPT')
                elif len(word) <= 3 and word.isupper():  # Keep acronyms
                    title_words.append(word.upper())
                else:
                    title_words.append(word.capitalize())
            
            result = ' '.join(title_words)
            
            # If result is too generic or too long, skip to next pattern
            generic_terms = ['chatbot', 'assistant', 'bot', 'ai', 'artificial intelligence', 'system', 'model']
            if result.lower() in generic_terms or len(result) > 50:
                continue
                
            return result
    
    # Pattern 3: Look for sentences that start with a proper name
    # "[Name], [description]"
    name_first_pattern = r'^([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*),\s+'
    match = re.search(name_first_pattern, original_text)
    if match:
        return match.group(1)
    
    # Fallback: use first few meaningful words, avoiding common starters
    words = original_text.split()
    meaningful_words = []
    skip_words = {'you', 'are', 'a', 'an', 'the', 'please', 'as', 'act', 'now', 'will', 'to', 'is', 'in', 'on', 'at', 'for', 'with', 'by'}
    
    for word in words[:10]:  # Look at first 10 words
        clean_word = word.strip('.,!?()[]').lower()
        if clean_word not in skip_words and len(clean_word) > 2:
            meaningful_words.append(word.strip('.,!?()[]'))
        if len(meaningful_words) >= 3:
            break
    
    if meaningful_words:
        return ' '.join(meaningful_words).title()
    
    # Final fallback
    return ' '.join(original_text.split()[:3]).strip('.,!?')


def create_prompty_content(system_prompt, user_prompt_example=None, extracted_name=None):
    """
    Create the content for a .prompty file based on the SPML template.
    """
    # Use the passed extracted name or extract it if not provided
    if extracted_name:
        role_name = extracted_name
    else:
        role_name = extract_role_name(system_prompt)
    
    # Clean up the role name for YAML
    clean_role_name = role_name.replace('"', "'").strip()
    
    template = f"""---
name: "{clean_role_name}"
description: "Source: SPML Chatbot Prompt Injection Dataset - https://huggingface.co/datasets/reshabhs/SPML_Chatbot_Prompt_Injection"
tags:
  - unlisted 
  - spml-dataset
  - prompt-injection
inputs:
    user_input:
        type: string
---
system:
{system_prompt}
user:
{{{{user_input}}}}"""
    
    return template


def process_csv_to_prompty(csv_file_path, output_dir_path):
    """
    Process the SPML CSV file and create .prompty files for unique system prompts.
    """
    # Create output directory if it doesn't exist
    output_dir = Path(output_dir_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    created_files = []
    unique_system_prompts = set()
    prompt_counter = {}
    
    print("Reading CSV file and extracting unique system prompts...")
    
    # Read and process the CSV file
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row_num, row in enumerate(reader, 1):
            if row_num % 1000 == 0:
                print(f"Processed {row_num} rows...")
            
            system_prompt = row['System Prompt'].strip()
            
            # Skip empty system prompts
            if not system_prompt:
                continue
            
            # Check if we've seen this system prompt before
            if system_prompt not in unique_system_prompts:
                unique_system_prompts.add(system_prompt)
                
                # Extract role name first
                extracted_name = extract_role_name(system_prompt)
                
                # Generate filename
                filename_base = generate_filename_from_system_prompt(system_prompt, extracted_name)
                
                # Handle potential filename collisions
                if filename_base in prompt_counter:
                    prompt_counter[filename_base] += 1
                    filename = f"{filename_base}_{prompt_counter[filename_base]}.prompty"
                else:
                    prompt_counter[filename_base] = 0
                    filename = f"{filename_base}.prompty"
                
                file_path = output_dir / filename
                
                # Get an example user prompt for context (optional)
                user_prompt_example = row.get('User Prompt', '').strip()
                
                # Create prompty content (pass the extracted name)
                content = create_prompty_content(system_prompt, user_prompt_example, extracted_name)
                
                # Write to file
                with open(file_path, 'w', encoding='utf-8') as prompty_file:
                    prompty_file.write(content)
                
                created_files.append(file_path)
                print(f"Created: {file_path}")
    
    print(f"\nProcessed {row_num} total rows")
    print(f"Found {len(unique_system_prompts)} unique system prompts")
    
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
        print("Usage: python generate_spml_prompty_files.py [csv_file_path] <output_directory>")
        print("Examples:")
        print("  python generate_spml_prompty_files.py ./spml_output")
        print("  python generate_spml_prompty_files.py spml_prompt_injection.csv ./spml_output")
        print("\nIf csv_file_path is not provided, the CSV will be downloaded from:")
        print(f"  {DEFAULT_CSV_URL}")
        sys.exit(1)
    
    # Determine if CSV file path was provided
    if len(sys.argv) == 2:
        # Only output directory provided, download CSV
        output_dir_path = sys.argv[1]
        csv_file_path = None
    else:
        # Both CSV file and output directory provided
        csv_file_path = sys.argv[1]
        output_dir_path = sys.argv[2]
    
    # Handle CSV file
    temp_csv_file = None
    if csv_file_path is None:
        # Download CSV file to temporary location
        temp_csv_file = tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False)
        temp_csv_file.close()
        
        if not download_csv_file(DEFAULT_CSV_URL, temp_csv_file.name):
            print("Failed to download CSV file.")
            sys.exit(1)
        
        csv_file_path = temp_csv_file.name
    else:
        # Check if provided CSV file exists
        if not os.path.exists(csv_file_path):
            print(f"Error: CSV file '{csv_file_path}' not found.")
            sys.exit(1)
    
    try:
        # Generate prompty files
        created_files = process_csv_to_prompty(csv_file_path, output_dir_path)
        print(f"\nGenerated {len(created_files)} unique .prompty files in '{output_dir_path}'")
        
        # Validate generated files
        validation_success = validate_generated_files(created_files)
        
        # Clean up temporary file if it was created
        if temp_csv_file is not None:
            try:
                os.unlink(temp_csv_file.name)
                print(f"\nCleaned up temporary CSV file: {temp_csv_file.name}")
            except:
                pass
        
        if not validation_success:
            print("\nSome files failed validation. Please check the errors above.")
            sys.exit(1)
        else:
            print(f"\n🎉 Successfully generated and validated all .prompty files!")
        
    except Exception as e:
        print(f"Error processing files: {e}")
        if temp_csv_file is not None:
            try:
                os.unlink(temp_csv_file.name)
            except:
                pass
        sys.exit(1)


if __name__ == "__main__":
    main() 