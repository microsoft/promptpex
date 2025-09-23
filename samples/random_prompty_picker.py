#!/usr/bin/env python3
"""
Random Prompty File Picker

This script takes a list of directories and a number n, then randomly selects 
n prompty files from each given directory and prints them in a comma-separated format.

Usage:
    python random_prompty_picker.py <n> <dir1> <dir2> ... <dirN> [--min-words MIN_WORDS]
    
Examples:
    python random_prompty_picker.py 3 SPML demo azure-ai-studio
    python random_prompty_picker.py 3 SPML demo azure-ai-studio --min-words 500
"""

import os
import re
import sys
import random
import glob
import argparse
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


def count_words_in_file(file_path: str) -> int:
    """
    Count the number of words in a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        int: Number of words in the file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Split by whitespace and count
            words = content.split()
            return len(words)
    except Exception:
        # If there's any error reading the file, return 0
        return 0


def filter_files_by_word_count(files: List[str], min_words: int) -> List[str]:
    """
    Filter files that have at least min_words words.
    
    Args:
        files (List[str]): List of file paths
        min_words (int): Minimum word count
        
    Returns:
        List[str]: List of files that meet the word count requirement
    """
    if min_words <= 0:
        return files
    
    filtered_files = []
    for file_path in files:
        word_count = count_words_in_file(file_path)
        if word_count >= min_words:
            filtered_files.append(file_path)
    
    return filtered_files


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
    parser = argparse.ArgumentParser(
        description='Randomly select n prompty files from given directories',
        epilog='Example: python random_prompty_picker.py 3 SPML demo azure-ai-studio --min-words 500'
    )
    
    parser.add_argument('n', type=int, help='Number of files to pick from each directory')
    parser.add_argument('directories', nargs='+', help='Directories to search for prompty files')
    parser.add_argument('--min-words', type=int, default=0, 
                       help='Minimum word count for files to be considered (default: 0)')
    
    args = parser.parse_args()
    
    if args.n <= 0:
        print("Error: n must be a positive integer")
        sys.exit(1)
    
    if args.min_words < 0:
        print("Error: min-words must be non-negative")
        sys.exit(1)
    
    n = args.n
    directories = args.directories
    min_words = args.min_words
    
    all_selected_files = []
    
    for directory in directories:
        # Find all prompty files in the directory
        prompty_files = find_prompty_files(directory)
        
        if not prompty_files:
            continue
        
        # Filter files by word count if min_words is specified
        if min_words > 0:
            prompty_files = filter_files_by_word_count(prompty_files, min_words)
        
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
        filename = os.path.relpath(file_path)
        if i == len(all_selected_files) - 1:
            # Last file - no comma
            print(f'"{rel_path}"')
        else:
            # Not the last file - include comma
            print(f'"{rel_path}",')


if __name__ == "__main__":
    main()
