import hashlib
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)


def hash_string(content: str, length: int = 7) -> str:
    """Generate a hash from a string."""
    return hashlib.md5(content.encode('utf-8')).hexdigest()[:length]