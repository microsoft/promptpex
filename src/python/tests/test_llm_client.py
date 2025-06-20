"""Test LLM client functionality."""
import pytest
from unittest.mock import patch, Mock
from promptpex.utils.llm_client import LiteLLMClient


def test_llm_client_init():
    """Test LLM client initialization."""
    client = LiteLLMClient("gpt-4o-mini")
    assert client.model == "gpt-4o-mini"
    
    # Test default model
    client_default = LiteLLMClient()
    assert client_default.model == "gpt-4o-mini"


@patch('promptpex.utils.llm_client.litellm.completion')
def test_call_llm(mock_completion):
    """Test calling the LLM."""
    # Mock the response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "Test response"
    mock_completion.return_value = mock_response
    
    client = LiteLLMClient("gpt-4o-mini")
    result = client.call_llm("System prompt", "User prompt")
    
    # Verify the call was made correctly
    mock_completion.assert_called_once_with(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "User prompt"}
        ],
        temperature=0.2,
        max_tokens=4000,
    )
    
    # Verify the response format
    assert result["choices"][0]["message"]["content"] == "Test response"


@patch('promptpex.utils.llm_client.litellm.completion')
def test_call_llm_with_custom_model(mock_completion):
    """Test calling the LLM with a custom model."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "Test response"
    mock_completion.return_value = mock_response
    
    client = LiteLLMClient("gpt-4o-mini")
    result = client.call_llm("System prompt", "User prompt", model="custom-model")
    
    # Verify the custom model was used
    mock_completion.assert_called_once_with(
        model="custom-model",
        messages=[
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "User prompt"}
        ],
        temperature=0.2,
        max_tokens=4000,
    )