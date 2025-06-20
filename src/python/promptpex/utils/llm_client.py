from typing import Dict, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)

# Try to import litellm, but make it optional
try:
    import litellm
    HAS_LITELLM = True
except ImportError:
    HAS_LITELLM = False
    logger.warning("litellm package not available - LLM calls will be mocked")


class LiteLLMClient:
    """Simple LLM client using litellm with GitHub Models support."""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        """Initialize the LiteLLM client.
        
        Args:
            model: Model name to use (defaults to gpt-4o-mini)
                   Supports GitHub Models with "github:" prefix
        """
        self.model = model
        if HAS_LITELLM:
            self._setup_github_models()
    
    def _setup_github_models(self):
        """Set up GitHub Models configuration if using GitHub Models."""
        if self.model.startswith("github:"):
            # GitHub Models configuration
            github_token = os.getenv("GITHUB_TOKEN")
            if github_token:
                # Configure GitHub Models endpoint
                litellm.api_base = "https://models.inference.ai.azure.com"
                litellm.api_key = github_token
                
                # For GitHub Models, we need to remove the "github:" prefix
                # and use the model name directly with GitHub's format
                model_name = self.model.replace("github:", "")
                self.model = model_name
                
                logger.info(f"Configured GitHub Models with model: {model_name}")
            else:
                logger.warning("GitHub Models requested but GITHUB_TOKEN not found")
    
    def call_llm(self, system_prompt: str, user_prompt: str, 
                 model: Optional[str] = None) -> Dict[str, Any]:
        """Call the LLM using litellm.
        
        Args:
            system_prompt: System prompt to send
            user_prompt: User prompt to send
            model: Model to use, defaults to self.model
            
        Returns:
            Response from the API in OpenAI format
        """
        if not model:
            model = self.model
            
        if not HAS_LITELLM:
            # Return a mock response when litellm is not available
            logger.warning("litellm not available - returning mock response")
            return {
                "choices": [
                    {
                        "message": {
                            "content": "Mock response - litellm not available"
                        }
                    }
                ]
            }
            
        # Handle GitHub Models prefix for per-call model override
        if model.startswith("github:"):
            model = model.replace("github:", "")
            
        response = litellm.completion(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=4000,
        )
        
        return {
            "choices": [
                {
                    "message": {
                        "content": response.choices[0].message.content
                    }
                }
            ]
        }