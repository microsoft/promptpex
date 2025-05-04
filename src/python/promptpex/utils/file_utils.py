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


def parse_prompty_file(content: str) -> Tuple[str, str]:
    """Parse .prompty file into system and user prompts.
    
    Args:
        content: Content of the prompty file
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system_prompt = ""
    user_prompt = ""

    parts = content.split("---", 2)
    if len(parts) >= 3:
        content_part = parts[2].strip()
    else:
        content_part = content.strip()

    if "system:" in content_part:
        sys_user_split = content_part.split("user:", 1)
        system_part = sys_user_split[0].replace("system:", "", 1).strip()
        system_prompt = system_part
        if len(sys_user_split) > 1:
            user_prompt = sys_user_split[1].strip()
    elif "user:" in content_part:
        user_prompt = content_part.split("user:", 1)[1].strip()
    else:
        user_prompt = content_part

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