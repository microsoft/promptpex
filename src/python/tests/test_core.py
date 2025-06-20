"""Test core PromptPex functionality."""
import pytest
import tempfile
import os
import json
from unittest.mock import patch, Mock
from promptpex.core import PythonPromptPex


def test_promptpex_init():
    """Test PromptPex initialization."""
    pex = PythonPromptPex(
        model="gpt-4o-mini",
        generate_tests=True,
        tests_per_rule=2,
        runs_per_test=1
    )
    
    assert pex.generate_tests is True
    assert pex.tests_per_rule == 2
    assert pex.runs_per_test == 1
    assert pex.models_to_test == ["gpt-4o-mini"]
    assert pex.llm_client.model == "gpt-4o-mini"


def test_promptpex_init_defaults():
    """Test PromptPex initialization with defaults."""
    pex = PythonPromptPex()
    
    assert pex.generate_tests is True
    assert pex.tests_per_rule == 3
    assert pex.runs_per_test == 1
    assert pex.models_to_test == ["gpt-4o-mini"]


def test_promptpex_disabled():
    """Test PromptPex with generation disabled."""
    pex = PythonPromptPex(generate_tests=False)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.prompty') as f:
        f.write("test prompt")
        temp_path = f.name
    
    try:
        result = pex.run(temp_path, "/tmp/output.json")
        assert result["status"] == "skipped"
        assert result["reason"] == "Test generation disabled"
    finally:
        os.unlink(temp_path)


def test_create_context_obj():
    """Test context object creation."""
    pex = PythonPromptPex()
    context = pex._create_context_obj("test prompt", "/path/to/test.prompty")
    
    assert context["prompt"] == "test prompt"
    assert context["prompt_file"] == "/path/to/test.prompty"
    assert context["name"].startswith("test_")
    assert "intent" in context
    assert "rules" in context
    assert "tests" in context


def test_parse_csv_tests():
    """Test CSV test parsing."""
    pex = PythonPromptPex()
    
    csv_content = """testinput,expectedoutput,reasoning
"Hello world","Positive","Greeting message"
"I hate this","Negative","Negative sentiment"
"""
    
    tests = pex._parse_csv_tests(csv_content, 1, "Test rule", is_inverse=False)
    
    assert len(tests) == 2
    assert tests[0]["testinput"] == "Hello world"
    assert tests[0]["expectedoutput"] == "Positive"
    assert tests[0]["reasoning"] == "Greeting message"
    assert tests[0]["ruleid"] == 1
    assert tests[0]["rule"] == "Test rule"
    assert tests[0]["inverse"] is False


def test_generate_summary():
    """Test summary generation."""
    pex = PythonPromptPex()
    
    context = {
        "rules": ["Rule 1", "Rule 2"],
        "inverse_rules": ["Inverse 1"],
        "rule_evaluations": [
            {"grounded": "ok"},
            {"grounded": "err"}
        ],
        "tests": [{"testinput": "test1"}, {"testinput": "test2"}],
        "baseline_tests": [{"testinput": "baseline1"}],
        "test_validity": [
            {"validity": "ok"},
            {"validity": "ok"},
            {"validity": "err"}
        ],
        "test_results": [
            {"model": "gpt-4", "compliance": "ok"},
            {"model": "gpt-4", "compliance": "err"},
            {"model": "gpt-3.5", "compliance": "ok"}
        ]
    }
    
    summary = pex._generate_summary(context)
    
    assert summary["total_rules"] == 2
    assert summary["inverse_rules"] == 1
    assert summary["grounded_rules"] == 1
    assert summary["grounded_percentage"] == 50.0
    
    assert summary["total_tests"] == 3
    assert summary["rule_tests"] == 2
    assert summary["baseline_tests"] == 1
    assert summary["valid_tests"] == 2
    assert summary["valid_percentage"] == 66.7
    
    assert summary["test_results"] == 3
    assert summary["compliant_tests"] == 2
    assert summary["compliant_percentage"] == 66.7
    
    assert "gpt-4" in summary["model_results"]
    assert "gpt-3.5" in summary["model_results"]


@patch('promptpex.core.read_prompt_file')
def test_run_file_not_found(mock_read_file):
    """Test running with non-existent file."""
    mock_read_file.side_effect = FileNotFoundError("File not found")
    
    pex = PythonPromptPex()
    result = pex.run("nonexistent.prompty", "/tmp/output.json")
    
    assert result["status"] == "error"
    assert "not found" in result["reason"]


def test_save_results():
    """Test saving results to files."""
    pex = PythonPromptPex()
    
    context = {
        "intent": "Test intent",
        "input_spec": {"raw": "Input specification"},
        "rules": ["Rule 1", "Rule 2"],
        "inverse_rules": ["Inverse 1"],
        "rule_evaluations": [
            {"ruleid": 1, "rule": "Rule 1", "grounded": "ok"}
        ],
        "tests": [
            {"ruleid": 1, "inverse": False, "testinput": "Test input", "expectedoutput": "Expected"}
        ],
        "baseline_tests": [
            {"testinput": "Baseline test"}
        ],
        "test_validity": [
            {"id": "test1", "test": "Test input", "validity": "ok"}
        ],
        "test_results": [
            {
                "id": "result1", "ruleid": 1, "rule": "Rule 1", "inverse": False,
                "model": "gpt-4", "input": "Test input", "output": "Test output", "compliance": "ok"
            }
        ],
        "summary": {"total_rules": 2}
    }
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, "results.json")
        pex._save_results(context, output_path)
        
        # Check main JSON file
        assert os.path.exists(output_path)
        with open(output_path, 'r') as f:
            saved_data = json.load(f)
            assert saved_data["intent"] == "Test intent"
        
        # Check component files
        components_dir = os.path.join(temp_dir, "promptpex_components")
        assert os.path.exists(os.path.join(components_dir, "intent.txt"))
        assert os.path.exists(os.path.join(components_dir, "rules.txt"))
        assert os.path.exists(os.path.join(components_dir, "summary.md"))
        assert os.path.exists(os.path.join(components_dir, "report.html"))