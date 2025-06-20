from typing import Dict, Any, Optional
import logging
import litellm

logger = logging.getLogger(__name__)


class LiteLLMClient:
    """Simple LLM client using litellm."""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        """Initialize the LiteLLM client.
        
        Args:
            model: Model name to use (defaults to gpt-4o-mini)
        """
        self.model = model
    
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