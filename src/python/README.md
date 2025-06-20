# PromptPex Python Implementation

A basic, minimalistic, idiomatic Python implementation of PromptPex test generation.

## Features

- 🚀 **Simplified**: Uses standard Python packages instead of custom implementations
- 🔧 **litellm**: Supports 100+ LLM providers (OpenAI, Azure, Anthropic, etc.)
- 📝 **prompty**: Uses the official prompty package for parsing .prompty files
- 🎯 **Minimal**: Clean, idiomatic Python code with minimal configuration
- 🔄 **Compatible**: Maintains the same interface as the original implementation

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your LLM provider** (example with OpenAI):
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

3. **Run the demo**:
   ```bash
   python demo.py
   ```

## Usage

```python
from promptpex.core import PythonPromptPex

# Initialize with any litellm-supported model
pex = PythonPromptPex(
    model="gpt-4o-mini",  # or "azure/your-deployment", "anthropic/claude-3", etc.
    generate_tests=True,
    tests_per_rule=3
)

# Run on a .prompty file
results = pex.run("your_prompt.prompty", "results.json")

print(f"Generated {len(results['tests'])} tests")
```

## Supported Models

Thanks to litellm, this implementation supports:

- **OpenAI**: `gpt-4`, `gpt-4o-mini`, etc.
- **Azure OpenAI**: `azure/your-deployment-name`
- **Anthropic**: `anthropic/claude-3-sonnet`
- **Google**: `gemini/gemini-pro`
- **Local/Ollama**: `ollama/llama2`
- **And 100+ more providers**

See [litellm docs](https://docs.litellm.ai/docs/providers) for the full list.

## Changes from Original

### Before (Azure-specific):
```python
pex = PythonPromptPex(azure_config={
    "azure_endpoint": "https://...",
    "azure_deployment": "gpt-4",
    "api_version": "2024-02-01"
})
```

### After (Universal):
```python
pex = PythonPromptPex(model="gpt-4o-mini")  # Works with any provider
```

## Dependencies

- `litellm`: Universal LLM interface
- `prompty`: Official prompty file parser
- `python-dotenv`: Environment variable management
- `PyYAML`: YAML processing

## Architecture

- **Core**: `promptpex/core.py` - Main PromptPex pipeline
- **LLM Client**: `utils/llm_client.py` - litellm wrapper
- **File Utils**: `utils/file_utils.py` - prompty parsing utilities
- **Helpers**: `utils/helpers.py` - Shared utilities

This implementation follows the "happy path" approach as requested - minimal error checking, clean code, standard libraries.