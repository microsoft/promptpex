import os
from typing import Tuple
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# Try to import prompty, but make it optional
try:
    from prompty import load_prompty
    HAS_PROMPTY = True
except ImportError:
    HAS_PROMPTY = False
    logger.warning("prompty package not available - using basic parsing")


def parse_prompty_file(content: str) -> Tuple[str, str]:
    """Parse .prompty file into system and user prompts.
    
    Args:
        content: Content of the prompty file
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    if HAS_PROMPTY:
        return _parse_with_prompty(content)
    else:
        return _parse_basic(content)


def _parse_with_prompty(content: str) -> Tuple[str, str]:
    """Parse using the official prompty package."""
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.prompty', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    try:
        # Load using prompty package
        prompty_data = load_prompty(temp_path)
        
        # Extract system and user content from body
        system_prompt = ""
        user_prompt = ""
        
        body = prompty_data.get('body', '')
        
        if "system:" in body:
            parts = body.split("user:", 1)
            system_part = parts[0].replace("system:", "", 1).strip()
            system_prompt = system_part
            if len(parts) > 1:
                user_prompt = parts[1].strip()
        elif "user:" in body:
            user_prompt = body.split("user:", 1)[1].strip()
        else:
            user_prompt = body.strip()
        
        return system_prompt, user_prompt
        
    finally:
        # Clean up temp file
        os.unlink(temp_path)


def _parse_basic(content: str) -> Tuple[str, str]:
    """Basic parsing without prompty package."""
    # Simple parsing - split on --- to separate frontmatter from body
    parts = content.split('---')
    if len(parts) >= 3:
        # Has frontmatter
        body = '---'.join(parts[2:]).strip()
    else:
        # No frontmatter
        body = content.strip()
    
    system_prompt = ""
    user_prompt = ""
    
    if "system:" in body:
        lines = body.split('\n')
        system_lines = []
        user_lines = []
        current_section = None
        
        for line in lines:
            if line.strip() == "system:":
                current_section = "system"
            elif line.strip() == "user:":
                current_section = "user"
            elif current_section == "system":
                system_lines.append(line)
            elif current_section == "user":
                user_lines.append(line)
        
        system_prompt = '\n'.join(system_lines).strip()
        user_prompt = '\n'.join(user_lines).strip()
    elif "user:" in body:
        user_prompt = body.split("user:", 1)[1].strip()
    else:
        user_prompt = body.strip()
    
    return system_prompt, user_prompt


def get_prompt_dir() -> str:
    """Get the path to the prompts directory.
    
    Returns:
        Path to the prompts directory
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))  # utils folder
    package_dir = os.path.dirname(current_dir)  # promptpex package
    python_dir = os.path.dirname(package_dir)  # python folder
    src_dir = os.path.dirname(python_dir)  # src folder
    
    return os.path.join(src_dir, "prompts")


def read_prompt_file(file_path: str) -> str:
    """Read a prompt file.
    
    Args:
        file_path: Path to the prompt file
        
    Returns:
        Contents of the file
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        Exception: For other errors
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()