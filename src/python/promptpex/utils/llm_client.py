from typing import Dict, Any, Optional
import logging
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential

logger = logging.getLogger(__name__)


class AzureOpenAIClient:
    """Client for calling Azure OpenAI API."""
    
    def __init__(self, azure_config: Dict[str, str]):
        """Initialize the Azure OpenAI client.
        
        Args:
            azure_config: Dictionary with Azure OpenAI configuration
        """
        self.azure_config = azure_config
        self.client = self._setup_client()
    
    def _setup_client(self) -> AzureOpenAI:
        """Set up the Azure OpenAI client."""
        credential = DefaultAzureCredential()
        token = credential.get_token("https://cognitiveservices.azure.com/.default").token
        base_url = self.azure_config["azure_endpoint"].strip()
        if not base_url:
            raise ValueError("Azure OpenAI endpoint URL cannot be empty")
        if not base_url.startswith(("http://", "https://")):
            base_url = f"https://{base_url}"
            
        return AzureOpenAI(
            api_key=token,
            api_version=self.azure_config["api_version"],
            azure_endpoint=base_url
        )
    
    def call_openai(self, system_prompt: str, user_prompt: str, 
                    model: Optional[str] = None) -> Dict[str, Any]:
        """Call the Azure OpenAI API.
        
        Args:
            system_prompt: System prompt to send
            user_prompt: User prompt to send
            model: Model to use, defaults to the one in azure_config
            
        Returns:
            Response from the API
            
        Raises:
            Exception: If there's an error calling the API
        """
        try:
            if not model:
                model = self.azure_config["azure_deployment"]
                
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=4000,
                n=1,
                stop=None,
                timeout=30
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
            
        except Exception as e:
            logger.error(f"Error calling Azure OpenAI API: {e}")
            raise