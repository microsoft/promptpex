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


import os
from typing import Tuple
import logging
from prompty import load_prompty

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)


def parse_prompty_file(content: str) -> Tuple[str, str]:
    """Parse .prompty file into system and user prompts using prompty package.
    
    Args:
        content: Content of the prompty file
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    # For simplicity, assuming content is a file path or we can write to temp file
    # In a production version, we'd handle this more elegantly
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