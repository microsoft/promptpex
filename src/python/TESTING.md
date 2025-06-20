# PromptPex Python Testing Guide

This guide covers testing the Python PromptPex implementation.

## Overview

The Python implementation includes comprehensive tests to ensure reliability:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test the full pipeline with GitHub Models
- **Sample Demo**: Demonstrate the complete pipeline structure

## Running Tests

### 1. Basic Tests (No API Key Required)

Run basic functionality tests without external dependencies:

```bash
cd src/python
python basic_test.py
```

This tests:
- Core module imports and functionality
- File utilities and prompty parsing
- PromptPex initialization and configuration
- Result generation and saving
- Summary creation

### 2. Unit Tests with pytest

Install test dependencies and run pytest:

```bash
cd src/python
pip install -r requirements.txt  # May require API access
python -m pytest tests/ -v
```

Or run with the test runner:

```bash
python run_tests.py
```

### 3. Integration Tests with GitHub Models

For full end-to-end testing with real LLM responses:

```bash
export GITHUB_TOKEN=your_github_token_here
cd src/python
python integration_test.py
```

Or with the test runner:

```bash
export GITHUB_TOKEN=your_github_token_here
python run_tests.py --integration
```

### 4. Sample Demo

See the complete pipeline structure:

```bash
cd src/python
python sample_demo.py
```

## Test Structure

```
src/python/
├── tests/                    # Unit tests
│   ├── test_core.py         # Core PromptPex functionality
│   ├── test_file_utils.py   # File utilities
│   ├── test_llm_client.py   # LLM client
│   └── test_helpers.py      # Helper functions
├── basic_test.py            # Basic functionality test
├── integration_test.py      # End-to-end with GitHub Models
├── sample_demo.py           # Pipeline demonstration
└── run_tests.py            # Test runner script
```

## GitHub Models Setup

To test with GitHub Models:

1. Get a GitHub personal access token with model access
2. Set the environment variable:
   ```bash
   export GITHUB_TOKEN=your_token_here
   ```
3. Run integration tests or use the CLI:
   ```bash
   python -m promptpex.cli prompt.prompty results.json --model github:gpt-4o-mini
   ```

## Supported Models

Thanks to litellm integration:

- **GitHub Models**: `github:gpt-4o-mini`, `github:gpt-4o`
- **OpenAI**: `gpt-4o-mini`, `gpt-4`, `gpt-3.5-turbo`
- **Azure OpenAI**: `azure/deployment-name`
- **Anthropic**: `anthropic/claude-3-sonnet`
- **Local/Ollama**: `ollama/llama2`

## Environment Variables

- `GITHUB_TOKEN`: Required for GitHub Models
- `OPENAI_API_KEY`: Required for OpenAI models
- `AZURE_OPENAI_*`: Required for Azure OpenAI models

## Test Coverage

The tests cover:

- ✅ Module imports and basic functionality
- ✅ Prompty file parsing (with and without external packages)
- ✅ LLM client initialization and mocking
- ✅ Core PromptPex pipeline structure
- ✅ Test generation and parsing
- ✅ Result saving and file creation
- ✅ Summary generation and reporting
- ✅ Error handling and edge cases
- ✅ GitHub Models integration
- ✅ CLI interface functionality

## Mock vs Real Testing

- **Mock Tests**: Work without API keys, test structure and logic
- **Real Tests**: Require API keys, test actual LLM integration
- **Hybrid**: Some tests use mocks for speed, real APIs for verification

## Continuous Integration

Tests can be run in CI environments by:
1. Running basic tests always (no API keys)
2. Running integration tests when tokens are available
3. Using test matrices for different Python versions