"""
Test runner script for basic functionality without external dependencies.

This script tests the core functionality without requiring litellm or prompty packages.
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_basic_imports():
    """Test that core modules can be imported."""
    print("🔍 Testing basic imports...")
    
    try:
        from promptpex.utils.helpers import hash_string
        print("✅ helpers module imported successfully")
        
        # Test hash function
        hash1 = hash_string("test")
        hash2 = hash_string("test")
        assert hash1 == hash2, "Hash function should be consistent"
        print("✅ hash_string function works correctly")
        
        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_file_utils_basic():
    """Test basic file utilities."""
    print("\n🔍 Testing file utilities...")
    
    try:
        from promptpex.utils.file_utils import read_prompt_file, get_prompt_dir
        
        # Test reading a file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.prompty') as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            content = read_prompt_file(temp_path)
            assert content == "test content", "File content should match"
            print("✅ read_prompt_file works correctly")
        finally:
            os.unlink(temp_path)
        
        # Test get_prompt_dir
        prompt_dir = get_prompt_dir()
        assert prompt_dir.endswith("src/prompts"), f"Prompt dir should end with src/prompts, got: {prompt_dir}"
        print("✅ get_prompt_dir works correctly")
        
        return True
    except Exception as e:
        print(f"❌ File utils test failed: {e}")
        return False

def test_core_initialization():
    """Test core PromptPex initialization without external dependencies."""
    print("\n🔍 Testing core initialization...")
    
    try:
        # Mock the external dependencies
        import sys
        from unittest.mock import Mock
        
        # Create mock modules
        mock_litellm = Mock()
        mock_prompty = Mock()
        
        sys.modules['litellm'] = mock_litellm
        sys.modules['prompty'] = mock_prompty
        
        # Mock the load_prompty function
        mock_prompty.load_prompty = Mock(return_value={
            'body': 'system:\nYou are helpful.\n\nuser:\nHello {{name}}!'
        })
        
        from promptpex.core import PythonPromptPex
        
        # Test initialization
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
        print("✅ PythonPromptPex initialization works correctly")
        
        # Test context creation
        context = pex._create_context_obj("test prompt", "/path/to/test.prompty")
        assert context["prompt"] == "test prompt"
        assert context["prompt_file"] == "/path/to/test.prompty"
        assert "intent" in context
        assert "rules" in context
        print("✅ Context object creation works correctly")
        
        # Test CSV parsing
        csv_content = """testinput,expectedoutput,reasoning
"Hello world","Positive","Greeting message"
"I hate this","Negative","Negative sentiment"
"""
        tests = pex._parse_csv_tests(csv_content, 1, "Test rule", is_inverse=False)
        assert len(tests) == 2
        assert tests[0]["testinput"] == "Hello world"
        assert tests[0]["expectedoutput"] == "Positive"
        print("✅ CSV parsing works correctly")
        
        # Test summary generation
        context = {
            "rules": ["Rule 1", "Rule 2"],
            "inverse_rules": ["Inverse 1"],
            "rule_evaluations": [
                {"grounded": "ok"},
                {"grounded": "err"}
            ],
            "tests": [{"testinput": "test1"}],
            "baseline_tests": [{"testinput": "baseline1"}],
            "test_validity": [{"validity": "ok"}, {"validity": "err"}],
            "test_results": [
                {"model": "gpt-4", "compliance": "ok"},
                {"model": "gpt-4", "compliance": "err"}
            ]
        }
        
        summary = pex._generate_summary(context)
        assert summary["total_rules"] == 2
        assert summary["grounded_percentage"] == 50.0
        print("✅ Summary generation works correctly")
        
        return True
    except Exception as e:
        print(f"❌ Core initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_result_saving():
    """Test result saving functionality."""
    print("\n🔍 Testing result saving...")
    
    try:
        import sys
        from unittest.mock import Mock
        
        # Mock external dependencies
        sys.modules['litellm'] = Mock()
        sys.modules['prompty'] = Mock()
        sys.modules['prompty'].load_prompty = Mock(return_value={'body': 'test'})
        
        from promptpex.core import PythonPromptPex
        
        pex = PythonPromptPex()
        
        context = {
            "intent": "Test intent",
            "input_spec": {"raw": "Input specification"},
            "rules": ["Rule 1", "Rule 2"],
            "inverse_rules": ["Inverse 1"],
            "rule_evaluations": [{"ruleid": 1, "rule": "Rule 1", "grounded": "ok"}],
            "tests": [{"ruleid": 1, "inverse": False, "testinput": "Test input", "expectedoutput": "Expected"}],
            "baseline_tests": [{"testinput": "Baseline test"}],
            "test_validity": [{"id": "test1", "test": "Test input", "validity": "ok"}],
            "test_results": [{
                "id": "result1", "ruleid": 1, "rule": "Rule 1", "inverse": False,
                "model": "gpt-4", "input": "Test input", "output": "Test output", "compliance": "ok"
            }]
        }
        
        # Generate the summary properly like the core does
        context["summary"] = pex._generate_summary(context)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "results.json")
            pex._save_results(context, output_path)
            
            # Check main JSON file
            assert os.path.exists(output_path), "Main JSON file should be created"
            with open(output_path, 'r') as f:
                saved_data = json.load(f)
                assert saved_data["intent"] == "Test intent"
            
            # Check component files
            components_dir = os.path.join(temp_dir, "promptpex_components")
            assert os.path.exists(os.path.join(components_dir, "intent.txt"))
            assert os.path.exists(os.path.join(components_dir, "rules.txt"))
            assert os.path.exists(os.path.join(components_dir, "summary.md"))
            assert os.path.exists(os.path.join(components_dir, "report.html"))
            
            print("✅ Result saving works correctly")
        
        return True
    except Exception as e:
        print(f"❌ Result saving test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all basic tests."""
    print("🚀 PromptPex Basic Test Suite")
    print("="*50)
    
    tests = [
        test_basic_imports,
        test_file_utils_basic,
        test_core_initialization,
        test_result_saving
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print(f"\n📊 Test Results:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 All basic tests passed!")
        return 0
    else:
        print(f"\n💥 {failed} test(s) failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())