# PromptPex Python Implementation

A basic, minimalistic, idiomatic Python implementation of PromptPex test generation using standard packages.

## Features

- 🌐 **Universal LLM Support**: Uses `litellm` library supporting 100+ providers
- 📝 **Standard Prompty Parsing**: Uses official `prompty` package
- 🔧 **Simple Configuration**: Minimal setup, just specify a model
- 🧪 **Comprehensive Testing**: Full test suite with mock and real LLM integration
- 🎯 **GitHub Models Ready**: Built-in support for GitHub Models API

## Quick Start

### Installation

```bash
cd src/python
pip install -r requirements.txt
```

### Basic Usage

```python
from promptpex.core import PythonPromptPex

# Initialize with any litellm-supported model
pex = PythonPromptPex(model="gpt-4o-mini")

# Run analysis on a prompty file
results = pex.run("your_prompt.prompty", "results.json")
```

### CLI Usage

```bash
# With OpenAI
export OPENAI_API_KEY=your_key_here
python -m promptpex.cli prompt.prompty results.json --model gpt-4o-mini

# With GitHub Models
export GITHUB_TOKEN=your_token_here
python -m promptpex.cli prompt.prompty results.json --model github:gpt-4o-mini

# Multiple models for testing
python -m promptpex.cli prompt.prompty results.json --model gpt-4o-mini --test-models github:gpt-4o-mini,gpt-3.5-turbo
```

## Testing

### Quick Test (No API Keys Required)

```bash
cd src/python
python basic_test.py
```

### Full Test Suite

```bash
cd src/python
python run_tests.py                    # Unit tests only
python run_tests.py --integration      # Include integration tests
```

### Sample Demo

```bash
cd src/python
python sample_demo.py                  # Shows complete pipeline structure
```

### GitHub Models Integration Test

```bash
export GITHUB_TOKEN=your_github_token_here
cd src/python
python integration_test.py
```

See [TESTING.md](TESTING.md) for complete testing documentation.

## Supported Models

Thanks to litellm integration:

- **GitHub Models**: `github:gpt-4o-mini`, `github:gpt-4o`, `github:phi-4-mini-instruct`
- **OpenAI**: `gpt-4o-mini`, `gpt-4`, `gpt-3.5-turbo`
- **Azure OpenAI**: `azure/deployment-name`
- **Anthropic**: `anthropic/claude-3-sonnet`
- **Google**: `gemini/gemini-pro`
- **Local/Ollama**: `ollama/llama2`
- **100+ more providers**

## Architecture

The implementation follows a clean, modular structure:

```
promptpex/
├── core.py              # Main PythonPromptPex class
├── cli.py               # Command-line interface
└── utils/
    ├── llm_client.py    # LiteLLM client with GitHub Models support
    ├── file_utils.py    # Prompty file parsing utilities
    └── helpers.py       # Utility functions
```

## Key Components

### PythonPromptPex Class

The main class that orchestrates the 9-step PromptPex pipeline:

1. **PUTI**: Prompt Under Test Intent extraction
2. **IS**: Input Specification generation
3. **OR**: Output Rules extraction
4. **IOR**: Inverse Output Rules generation
5. **ORG**: Output Rules Groundedness evaluation
6. **PPT**: PromptPex Tests generation
7. **BT**: Baseline Tests generation
8. **TV**: Test Validity evaluation
9. **TO & TNC**: Test Orchestration and Non-Compliance checking

### LiteLLM Client

Unified interface for multiple LLM providers with special support for GitHub Models:

```python
from promptpex.utils.llm_client import LiteLLMClient

# Works with any litellm-supported model
client = LiteLLMClient("github:gpt-4o-mini")
response = client.call_llm("System prompt", "User prompt")
```

### File Utilities

Robust prompty file parsing with fallback options:

```python
from promptpex.utils.file_utils import parse_prompty_file

# Automatically uses prompty package if available, falls back to basic parsing
system_prompt, user_prompt = parse_prompty_file(content)
```

## Output

The system generates comprehensive outputs:

- **Main JSON**: Complete results with all pipeline data
- **Component Files**: Individual files for each pipeline step
- **HTML Report**: Interactive report for result visualization
- **CSV Files**: Structured data for analysis
- **Summary Markdown**: Human-readable summary

## Environment Variables

- `GITHUB_TOKEN`: Required for GitHub Models (`github:` prefix)
- `OPENAI_API_KEY`: Required for OpenAI models
- `AZURE_OPENAI_*`: Required for Azure OpenAI models

## Design Principles

- **Minimalistic**: Simple, clean API with sensible defaults
- **Idiomatic**: Follows Python best practices and conventions
- **Universal**: Works with any LLM provider supported by litellm
- **Testable**: Comprehensive test coverage with mock and real options
- **Robust**: Graceful degradation when dependencies are unavailable

## Demo

Run the included demo to see the system in action:

```bash
cd src/python
python demo.py
```

This demonstrates:
- ✅ Prompty file parsing
- ✅ LLM client initialization
- ✅ End-to-end pipeline execution
- ✅ Result generation and visualization