"""Test file utility functions."""
import pytest
import tempfile
import os
from promptpex.utils.file_utils import parse_prompty_file, read_prompt_file, get_prompt_dir


def test_parse_prompty_file():
    """Test parsing of prompty files."""
    content = """---
name: Test Prompt
description: A test prompt
---
system:
You are a helpful assistant.

user:
Hello {{name}}!
"""
    
    system_prompt, user_prompt = parse_prompty_file(content)
    
    assert "You are a helpful assistant." in system_prompt
    assert "Hello {{name}}!" in user_prompt


def test_parse_prompty_file_user_only():
    """Test parsing prompty file with user prompt only."""
    content = """---
name: Test Prompt
---
user:
What is the weather like?
"""
    
    system_prompt, user_prompt = parse_prompty_file(content)
    
    assert system_prompt == ""
    assert "What is the weather like?" in user_prompt


def test_parse_prompty_file_no_sections():
    """Test parsing prompty file with no system/user sections."""
    content = """---
name: Test Prompt
---
Just a simple prompt text.
"""
    
    system_prompt, user_prompt = parse_prompty_file(content)
    
    assert system_prompt == ""
    assert "Just a simple prompt text." in user_prompt


def test_read_prompt_file():
    """Test reading a prompt file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.prompty') as f:
        f.write("test content")
        temp_path = f.name
    
    try:
        content = read_prompt_file(temp_path)
        assert content == "test content"
    finally:
        os.unlink(temp_path)


def test_read_prompt_file_not_found():
    """Test reading a non-existent file."""
    with pytest.raises(FileNotFoundError):
        read_prompt_file("/nonexistent/file.prompty")


def test_get_prompt_dir():
    """Test getting the prompt directory."""
    prompt_dir = get_prompt_dir()
    assert prompt_dir.endswith("src/prompts")
    # Note: We don't test if the directory exists as it might not in all environments