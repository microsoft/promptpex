#!/usr/bin/env python3
"""
Script to convert prompts.csv to individual .prompty files.
Usage: python generate_prompty_files.py [prompts.csv] output_directory
If prompts.csv is not provided, it will be downloaded from the default URL.
"""

import csv
import os
import sys
import re
from pathlib import Path
import urllib.request
import tempfile
import prompty


# Default URL for the prompts CSV file
DEFAULT_CSV_URL = "https://huggingface.co/datasets/fka/awesome-chatgpt-prompts/resolve/main/prompts.csv"


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


def sanitize_filename(text):
    """
    Convert text to a valid filename by:
    1. Converting to lowercase
    2. Replacing spaces and special characters with underscores
    3. Removing multiple consecutive underscores
    4. Removing leading/trailing underscores
    """
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces and special characters with underscores
    text = re.sub(r'[^a-z0-9]+', '_', text)
    
    # Remove multiple consecutive underscores
    text = re.sub(r'_+', '_', text)
    
    # Remove leading/trailing underscores
    text = text.strip('_')
    
    return text


def create_prompty_content(act, prompt):
    """
    Create the content for a .prompty file based on the template.
    """
    # Clean up the act name to avoid YAML issues
    clean_act = act.replace('`', '').strip(':').strip()
    
    template = f"""---
name: "{clean_act}"
description: "Source: Awesome ChatGPT Prompts - https://huggingface.co/datasets/fka/awesome-chatgpt-prompts/blob/main/prompts.csv"
tags:
  - unlisted 
  - awesome-chatgpt-prompts
inputs:
    user_input:
        type: string
---
system:
{prompt}
user:
{{{{user_input}}}}"""
    
    return template


def process_csv_to_prompty(csv_file_path, output_dir_path):
    """
    Process the CSV file and create .prompty files in the output directory.
    """
    # Create output directory if it doesn't exist
    output_dir = Path(output_dir_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    created_files = []
    
    # Read and process the CSV file
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            act = row['act']
            prompt = row['prompt']
            
            # Generate filename
            filename = sanitize_filename(act) + '.prompty'
            file_path = output_dir / filename
            
            # Create prompty content
            content = create_prompty_content(act, prompt)
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as prompty_file:
                prompty_file.write(content)
            
            created_files.append(file_path)
            print(f"Created: {file_path}")
    
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
        print("Usage: python generate_prompty_files.py [csv_file_path] <output_directory>")
        print("Examples:")
        print("  python generate_prompty_files.py ./output")
        print("  python generate_prompty_files.py prompts.csv ./output")
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
        print(f"\nGenerated {len(created_files)} .prompty files in '{output_dir_path}'")
        
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