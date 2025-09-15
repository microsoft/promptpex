#!/usr/bin/env python3
"""
Random Prompty File Picker

This script takes a list of directories and a number n, then randomly selects 
n prompty files from each given directory and prints them in a comma-separated format.

Usage:
    python random_prompty_picker.py <n> <dir1> <dir2> ... <dirN>
    
Example:
    python random_prompty_picker.py 3 SPML demo azure-ai-studio
"""

import os
import sys
import random
import glob
from pathlib import Path
from typing import List


def find_prompty_files(directory: str) -> List[str]:
    """
    Find all .prompty files in the given directory recursively.
    
    Args:
        directory (str): The directory path to search in
        
    Returns:
        List[str]: List of .prompty file paths
    """
    directory_path = Path(directory)
    if not directory_path.exists():
        return []
    
    if not directory_path.is_dir():
        return []
    
    # Use glob to find all .prompty files recursively
    pattern = os.path.join(directory, "**", "*.prompty")
    prompty_files = glob.glob(pattern, recursive=True)
    
    return prompty_files


def pick_random_files(files: List[str], n: int) -> List[str]:
    """
    Pick n random files from the given list.
    
    Args:
        files (List[str]): List of file paths
        n (int): Number of files to pick
        
    Returns:
        List[str]: List of randomly selected file paths
    """
    if not files:
        return []
    
    # If n is greater than available files, return all files
    if n >= len(files):
        return files.copy()
    
    return random.sample(files, n)


def main():
    """Main function to handle command line arguments and execute the script."""
    if len(sys.argv) < 3:
        print("Usage: python random_prompty_picker.py <n> <dir1> <dir2> ... <dirN>")
        print("Example: python random_prompty_picker.py 3 SPML demo azure-ai-studio")
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
        if n <= 0:
            print("Error: n must be a positive integer")
            sys.exit(1)
    except ValueError:
        print("Error: n must be a valid integer")
        sys.exit(1)
    
    directories = sys.argv[2:]
    
    if not directories:
        print("Error: At least one directory must be specified")
        sys.exit(1)
    
    all_selected_files = []
    
    for directory in directories:
        # Find all prompty files in the directory
        prompty_files = find_prompty_files(directory)
        
        if not prompty_files:
            continue
        
        # Pick n random files
        selected_files = pick_random_files(prompty_files, n)
        
        # Add to the overall list
        all_selected_files.extend(selected_files)
    
    if not all_selected_files:
        sys.exit(1)
    
    # Print the selected files in the requested format
    for i, file_path in enumerate(all_selected_files):
        # Extract just the filename for cleaner output
        filename = os.path.basename(file_path)
        if i == len(all_selected_files) - 1:
            # Last file - no comma
            print(f'"{filename}"')
        else:
            # Not the last file - include comma
            print(f'"{filename}",')


if __name__ == "__main__":
    main()
