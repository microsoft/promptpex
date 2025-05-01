import os
import json
import logging
import hashlib
import csv
import io
import argparse
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# Constants
PROMPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "prompts")

# Hash function for test and rule IDs
def hash_string(content: str, length: int = 7) -> str:
    """Generate a hash from a string."""
    return hashlib.md5(content.encode('utf-8')).hexdigest()[:length]

class PromptPexIntegrator:
    """Class that implements core PromptPEX functionality."""

    def __init__(self, 
                 azure_config: Optional[Dict[str, str]] = None,
                 generate_tests: bool = True,
                 tests_per_rule: int = 3,
                 runs_per_test: int = 1,
                 models_to_test: Optional[List[str]] = None):
        """Initialize the PromptPEX integrator with configuration.
        
        Args:
            azure_config: Dictionary with Azure OpenAI configuration
            generate_tests: Whether to generate tests
            tests_per_rule: Number of tests to generate per rule
            runs_per_test: Number of times to run each test
            models_to_test: List of Azure deployment names to test against
        """
        self.generate_tests = generate_tests
        self.tests_per_rule = tests_per_rule
        self.runs_per_test = runs_per_test
        self.models_to_test = models_to_test or []

        if azure_config is None:
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
            azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
            self.azure_config = {
                "azure_endpoint": azure_endpoint,
                "azure_deployment": azure_deployment,
                "api_version": api_version
            }
        else:
            self.azure_config = azure_config

        if not self.models_to_test:
            self.models_to_test = [self.azure_config["azure_deployment"]]

        self._setup_openai_client()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _setup_openai_client(self):
        """Set up the Azure OpenAI client."""
        credential = DefaultAzureCredential()
        token = credential.get_token("https://cognitiveservices.azure.com/.default").token
        base_url = self.azure_config["azure_endpoint"].strip()
        if not base_url:
            raise ValueError("Azure OpenAI endpoint URL cannot be empty")
        if not base_url.startswith(("http://", "https://")):
            base_url = f"https://{base_url}"
            
        self.client = AzureOpenAI(
            api_key=token,
            api_version=self.azure_config["api_version"],
            azure_endpoint=base_url
        )

    def run(self, prompt_file_path: str, output_json_path: str) -> Dict[str, Any]:
        """Run the full PromptPEX pipeline.
        
        Args:
            prompt_file_path: Path to the prompt file to test (PUT - Prompt Under Test)
            output_json_path: Path to save the main JSON results
            
        Returns:
            Dictionary with results
        """
        if not self.generate_tests:
            logger.info("Test generation disabled, skipping PromptPEX")
            return {"status": "skipped", "reason": "Test generation disabled"}
        
        logger.info(f"Starting PromptPEX pipeline for prompt: {prompt_file_path}")
        
        try:
            with open(prompt_file_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
        except FileNotFoundError:
            logger.error(f"Prompt file not found: {prompt_file_path}")
            return {"status": "error", "reason": f"Prompt file not found: {prompt_file_path}"}
        except Exception as e:
            logger.error(f"Error reading prompt file {prompt_file_path}: {e}")
            return {"status": "error", "reason": f"Error reading prompt file: {e}"}

        context = self._create_context_obj(prompt_content, prompt_file_path)

        logger.info("Step 1: Generating prompt intent (PUTI)")
        context["intent"] = self._extract_intent(prompt_content)
        
        logger.info("Step 2: Generating input specification (IS)")
        context["input_spec"] = self._generate_input_specification(prompt_content)
        
        logger.info("Step 3: Extracting output rules (OR)")
        context["rules"] = self._extract_output_rules(prompt_content)
        
        logger.info("Step 4: Generating inverse output rules (IOR)")
        context["inverse_rules"] = self._generate_inverse_rules(context["rules"], prompt_content)
        
        logger.info("Step 5: Evaluating rule groundedness (ORG)")
        context["rule_evaluations"] = self._evaluate_rules_groundedness(context["rules"], prompt_content)
        
        logger.info("Step 6: Generating prompt tests (PPT)")
        context["tests"] = self._generate_tests(prompt_content, context["input_spec"], 
                                               context["rules"], context["inverse_rules"])
        
        logger.info("Step 7: Generating baseline tests (BT)")
        context["baseline_tests"] = self._generate_baseline_tests(prompt_content)
        
        logger.info("Step 8: Evaluating test validity (TV)")
        context["test_validity"] = self._evaluate_test_validity(context["tests"] + context["baseline_tests"], 
                                                             context["input_spec"])
        
        logger.info("Step 9: Running tests and checking compliance (TO & TNC)")
        context["test_results"] = self._run_tests(prompt_content, context["tests"] + context["baseline_tests"])
        
        context["summary"] = self._generate_summary(context)
        
        self._save_results(context, output_json_path)
        
        return context
    
    def _create_context_obj(self, prompt_content: str, prompt_file_path: str) -> Dict[str, Any]:
        """Create the context object with proper naming for components."""
        prompt_name = os.path.splitext(os.path.basename(prompt_file_path))[0]
        context = {
            "prompt_file": prompt_file_path,
            "prompt": prompt_content,
            "name": f"{prompt_name}_{self.timestamp}",
            "intent": "",
            "input_spec": {},
            "rules": [],
            "inverse_rules": [],
            "rule_evaluations": [],
            "tests": [],
            "baseline_tests": [],
            "test_validity": [],
            "test_results": [],
            "summary": {}
        }
        return context
    
    def _extract_intent(self, prompt: str) -> str:
        """Extract the intent from the prompt (PUTI)."""
        prompt_path = os.path.join(PROMPT_DIR, "generate_intent.prompty")
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
                
            system_prompt, user_prompt_template = self._parse_prompty_file(prompt_content)
            
            user_prompt = user_prompt_template.replace("{{ prompt }}", prompt)
            
            response = self._call_openai(system_prompt, user_prompt)
            
            intent = response["choices"][0]["message"]["content"].strip()
            return intent
            
        except Exception as e:
            logger.error(f"Error extracting intent: {e}")
            return "Unknown intent"
    
    def _generate_input_specification(self, prompt: str) -> Dict[str, Any]:
        """Generate input specification from prompt (IS)."""
        prompt_path = os.path.join(PROMPT_DIR, "generate_input_spec.prompty")
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
                
            system_prompt, user_prompt_template = self._parse_prompty_file(prompt_content)
            
            user_prompt = user_prompt_template.replace("{{context}}", prompt)
            
            response = self._call_openai(system_prompt, user_prompt)
            
            content = response["choices"][0]["message"]["content"].strip()
            
            rules = [rule.strip() for rule in content.split("\n") if rule.strip()]
            
            input_spec = {
                "input_constraints": rules,
                "raw": content
            }
            
            return input_spec
            
        except Exception as e:
            logger.error(f"Error generating input specification: {e}")
            return {"input_constraints": [], "raw": ""}
    
    def _extract_output_rules(self, prompt: str) -> List[str]:
        """Extract output rules from prompt (OR)."""
        prompt_path = os.path.join(PROMPT_DIR, "generate_output_rules.prompty")
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
                
            system_prompt, user_prompt_template = self._parse_prompty_file(prompt_content)
            
            system_prompt = system_prompt.replace("{{instructions}}", "")
            system_prompt = system_prompt.replace("{{num_rules}}", "0")
            user_prompt = user_prompt_template.replace("{{input_data}}", prompt)
            
            response = self._call_openai(system_prompt, user_prompt)
            
            content = response["choices"][0]["message"]["content"]
            rules = [rule.strip() for rule in content.split("\n") if rule.strip()]
            
            return rules
            
        except Exception as e:
            logger.error(f"Error extracting output rules: {e}")
            return []
    
    def _generate_inverse_rules(self, rules: List[str], prompt: str) -> List[str]:
        """Generate inverse rules from existing rules (IOR)."""
        if not rules:
            return []
            
        prompt_path = os.path.join(PROMPT_DIR, "generate_inverse_rules.prompty")
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
                
            system_prompt, user_prompt_template = self._parse_prompty_file(prompt_content)
            
            system_prompt = system_prompt.replace("{{instructions}}", "")
            user_prompt = user_prompt_template.replace("{{rule}}", "\n".join(rules))
            
            response = self._call_openai(system_prompt, user_prompt)
            
            content = response["choices"][0]["message"]["content"]
            inverse_rules = [rule.strip() for rule in content.split("\n") if rule.strip()]
            
            return inverse_rules
            
        except Exception as e:
            logger.error(f"Error generating inverse rules: {e}")
            return []
    
    def _evaluate_rules_groundedness(self, rules: List[str], prompt: str) -> List[Dict[str, Any]]:
        """Evaluate if rules are grounded in the prompt (ORG)."""
        if not rules:
            return []
            
        prompt_path = os.path.join(PROMPT_DIR, "eval_rule_grounded.prompty")
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
                
            system_prompt, user_prompt_template = self._parse_prompty_file(prompt_content)
            
            evaluations = []
            
            for rule_id, rule in enumerate(rules, 1):
                user_prompt = user_prompt_template.replace("{{ rule }}", rule)
                user_prompt = user_prompt.replace("{{ description }}", prompt)
                
                response = self._call_openai(system_prompt, user_prompt)
                
                content = response["choices"][0]["message"]["content"].strip()
                
                rule_hash = hash_string(rule)
                promptid = hash_string(prompt)
                
                evaluation = {
                    "id": rule_hash,
                    "promptid": promptid,
                    "ruleid": rule_id,
                    "rule": rule,
                    "groundedText": content,
                    "grounded": "ok" if content.upper() == "OK" else "err"
                }
                
                evaluations.append(evaluation)
            
            return evaluations
            
        except Exception as e:
            logger.error(f"Error evaluating rule groundedness: {e}")
            return []
    
    def _generate_tests(self, prompt: str, input_spec: Dict[str, Any], 
                       rules: List[str], inverse_rules: List[str]) -> List[Dict[str, Any]]:
        """Generate test cases based on rules and input specification (PPT)."""
        if not rules:
            return []
            
        prompt_path = os.path.join(PROMPT_DIR, "generate_tests.prompty")
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
                
            system_prompt, user_prompt_template = self._parse_prompty_file(prompt_content)
            
            all_tests = []
            
            for rule_id, rule in enumerate(rules, 1):
                user_prompt = "List of Rules:\n{}".format(rule)
                
                input_spec_text = "\n".join(input_spec.get("input_constraints", []))
                
                current_system = system_prompt.replace("{{input_spec}}", input_spec_text)
                current_system = current_system.replace("{{context}}", prompt)
                current_system = current_system.replace("{{num}}", str(self.tests_per_rule))
                current_system = current_system.replace("{{rule}}", rule)
                current_system = current_system.replace("{{num_rules}}", "1")
                
                response = self._call_openai(current_system, user_prompt)
                
                content = response["choices"][0]["message"]["content"].strip()
                tests = self._parse_csv_tests(content, rule_id, rule, is_inverse=False)
                all_tests.extend(tests)
                
            for rule_id, rule in enumerate(inverse_rules, 1):
                user_prompt = "List of Rules:\n{}".format(rule)
                
                input_spec_text = "\n".join(input_spec.get("input_constraints", []))
                
                current_system = system_prompt.replace("{{input_spec}}", input_spec_text)
                current_system = current_system.replace("{{context}}", prompt)
                current_system = current_system.replace("{{num}}", str(self.tests_per_rule))
                current_system = current_system.replace("{{rule}}", rule)
                current_system = current_system.replace("{{num_rules}}", "1")
                
                response = self._call_openai(current_system, user_prompt)
                
                content = response["choices"][0]["message"]["content"].strip()
                tests = self._parse_csv_tests(content, rule_id, rule, is_inverse=True)
                all_tests.extend(tests)
                
            return all_tests
            
        except Exception as e:
            logger.error(f"Error generating tests: {e}")
            return []
    
    def _parse_csv_tests(self, csv_content: str, rule_id: int, rule: str, 
                        is_inverse: bool = False) -> List[Dict[str, Any]]:
        """Parse CSV test cases from response."""
        try:
            lines = csv_content.split('\n')
            if len(lines) > 1:
                csv_content = '\n'.join(lines)
            
            tests = []
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            for row in csv_reader:
                test = {
                    "ruleid": rule_id,
                    "rule": rule,
                    "inverse": is_inverse,
                    "testinput": row.get("testinput", ""),
                    "expectedoutput": row.get("expectedoutput", ""),
                    "reasoning": row.get("reasoning", "")
                }
                tests.append(test)
            
            return tests
        except Exception as e:
            logger.error(f"Error parsing CSV test cases: {e}")
            return []
    
    def _generate_baseline_tests(self, prompt: str) -> List[Dict[str, Any]]:
        """Generate baseline test cases without using rules (BT)."""
        prompt_path = os.path.join(PROMPT_DIR, "generate_baseline_tests.prompty")
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
                
            system_prompt, user_prompt_template = self._parse_prompty_file(prompt_content)
            
            system_prompt = system_prompt.replace("{{num}}", str(self.tests_per_rule))
            user_prompt = user_prompt_template.replace("{{prompt}}", prompt)
            
            response = self._call_openai(system_prompt, user_prompt)
            
            content = response["choices"][0]["message"]["content"].strip()
            
            test_contents = content.split("===")
            tests = []
            
            for test_content in test_contents:
                test_input = test_content.strip()
                if test_input:
                    test = {
                        "baseline": True,
                        "testinput": test_input
                    }
                    tests.append(test)
            
            return tests
            
        except Exception as e:
            logger.error(f"Error generating baseline tests: {e}")
            return []
    
    def _evaluate_test_validity(self, tests: List[Dict[str, Any]], 
                              input_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate if test inputs comply with input specification (TV)."""
        prompt_path = os.path.join(PROMPT_DIR, "eval_test_validity.prompty")
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
                
            system_prompt, user_prompt_template = self._parse_prompty_file(prompt_content)
            
            evaluations = []
            input_spec_text = "\n".join(input_spec.get("input_constraints", []))
            
            for test in tests:
                current_user_prompt = user_prompt_template.replace("{{test}}", test["testinput"])
                current_system_prompt = system_prompt.replace("{{input_spec}}", input_spec_text)
                
                response = self._call_openai(current_system_prompt, current_user_prompt)
                
                content = response["choices"][0]["message"]["content"].strip()
                
                lines = content.strip().split("\n")
                decision = lines[-1].strip().upper() if lines else "ERR"
                
                test_hash = hash_string(test["testinput"])
                evaluation = {
                    "id": test_hash,
                    "test": test["testinput"],
                    "validityText": content,
                    "validity": "ok" if decision == "OK" else "err" 
                }
                
                evaluations.append(evaluation)
            
            return evaluations
            
        except Exception as e:
            logger.error(f"Error evaluating test validity: {e}")
            return []
    
    def _run_tests(self, prompt: str, tests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run tests against models and evaluate compliance (TO & TNC)."""
        prompt_path = os.path.join(PROMPT_DIR, "eval_test_result.prompty")
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
                
            system_prompt, user_prompt_template = self._parse_prompty_file(prompt_content)
            
            results = []
            
            for test in tests:
                for model in self.models_to_test:
                    for run in range(self.runs_per_test):
                        test_result = self._run_single_test(prompt, test, model, run, 
                                                          system_prompt, user_prompt_template)
                        results.append(test_result)
                        
            return results
            
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            return []
    
    def _run_single_test(self, prompt: str, test: Dict[str, Any], model: str, run_id: int,
                       eval_system_prompt: str, eval_user_prompt_template: str) -> Dict[str, Any]:
        """Run a single test against a model (TO) and check compliance (TNC)."""
        try:
            test_input = test["testinput"]
            response = self._call_openai(prompt, test_input, model=model)
            model_output = response["choices"][0]["message"]["content"]
            
            rule_part = test.get('ruleid', 'baseline')
            test_input_hash = hash_string(test_input)
            test_id = f"{rule_part}-{test_input_hash}-{model}-{run_id}"
            result = {
                "id": test_id,
                "ruleid": test.get('ruleid'),
                "rule": test.get('rule', ""),
                "inverse": test.get('inverse', False),
                "baseline": test.get('baseline', False),
                "model": model,
                "input": test_input,
                "output": model_output
            }
            
            if test.get('rule'):
                current_system_prompt = eval_system_prompt.replace("{{ system }}", prompt)
                current_user_prompt = eval_user_prompt_template.replace("{{ result }}", model_output)
                
                eval_response = self._call_openai(current_system_prompt, current_user_prompt)
                eval_content = eval_response["choices"][0]["message"]["content"].strip()
                
                lines = eval_content.strip().split("\n")
                decision = lines[-1].strip().upper() if lines else "ERR"
                
                expected_compliance = "err" if test.get('inverse', False) else "ok"
                actual_compliance = "ok" if decision == "OK" else "err"
                
                result["complianceText"] = eval_content
                result["compliance"] = actual_compliance
                result["compliance_matched"] = actual_compliance == expected_compliance
            
            return result
            
        except Exception as e:
            logger.error(f"Error running test {test.get('testinput', '')[:30]} on model {model}: {e}")
            rule_part = test.get('ruleid', 'baseline')
            test_input_hash = hash_string(test.get('testinput', ''))
            test_id = f"{rule_part}-{test_input_hash}-{model}-{run_id}"
            return {
                "id": test_id,
                "ruleid": test.get('ruleid'),
                "rule": test.get('rule', ""),
                "inverse": test.get('inverse', False),
                "baseline": test.get('baseline', False),
                "model": model,
                "input": test.get('testinput', ""),
                "output": "ERROR",
                "error": str(e)
            }
    
    def _generate_summary(self, context: Dict[str, Any]) -> Dict[str, Any]:
        rules = context.get("rules", [])
        rule_evaluations = context.get("rule_evaluations", [])
        test_results = context.get("test_results", [])
        tests = context.get("tests", [])
        baseline_tests = context.get("baseline_tests", [])
        test_validity = context.get("test_validity", [])
        
        grounded_rules = sum(1 for r in rule_evaluations if r.get("grounded") == "ok")
        valid_tests = sum(1 for t in test_validity if t.get("validity") == "ok")
        rule_test_results = [r for r in test_results if "compliance" in r]
        compliant_tests = sum(1 for r in rule_test_results if r.get("compliance") == "ok")
        
        model_results = {}
        for result in test_results:
            model = result.get("model", "unknown")
            if model not in model_results:
                model_results[model] = {"total": 0, "ok": 0}
            
            if "compliance" in result:
                model_results[model]["total"] += 1
                if result.get("compliance") == "ok":
                    model_results[model]["ok"] += 1
        
        grounded_percentage = round((grounded_rules / len(rules) * 100) if rules else 0, 1)
        valid_percentage = round((valid_tests / len(test_validity) * 100) if test_validity else 0, 1)
        compliant_percentage = round((compliant_tests / len(rule_test_results) * 100) 
                                   if rule_test_results else 0, 1)
        
        summary = {
            "total_rules": len(rules),
            "inverse_rules": len(context.get("inverse_rules", [])),
            "grounded_rules": grounded_rules,
            "grounded_percentage": grounded_percentage,
            
            "total_tests": len(tests) + len(baseline_tests),
            "rule_tests": len(tests),
            "baseline_tests": len(baseline_tests),
            "valid_tests": valid_tests,
            "valid_percentage": valid_percentage,
            
            "test_results": len(test_results),
            "compliant_tests": compliant_tests,
            "compliant_percentage": compliant_percentage,
            
            "model_results": model_results
        }
        
        return summary
    
    def _parse_prompty_file(self, content: str) -> Tuple[str, str]:
        """Parse .prompty file into system and user prompts."""
        system_prompt = ""
        user_prompt = ""

        parts = content.split("---", 2)
        if len(parts) >= 3:
            content_part = parts[2].strip()
        else:
            content_part = content.strip()

        if "system:" in content_part:
            sys_user_split = content_part.split("user:", 1)
            system_part = sys_user_split[0].replace("system:", "", 1).strip()
            system_prompt = system_part
            if len(sys_user_split) > 1:
                user_prompt = sys_user_split[1].strip()
        elif "user:" in content_part:
            user_prompt = content_part.split("user:", 1)[1].strip()
        else:
            user_prompt = content_part

        return system_prompt, user_prompt
    
    def _call_openai(self, system_prompt: str, user_prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Call the Azure OpenAI API."""
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
    
    def _save_results(self, context: Dict[str, Any], output_json_path: str):
        """Save results to files."""
        output_dir = os.path.dirname(output_json_path)
        if output_dir and not os.path.exists(output_dir):
             os.makedirs(output_dir, exist_ok=True)

        try:
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(context, f, indent=2)
            logger.info(f"Full results saved to {output_json_path}")
        except Exception as e:
            logger.error(f"Error saving JSON results to {output_json_path}: {e}")
            return

        base_dir = os.path.join(output_dir, "promptpex_components")
        os.makedirs(base_dir, exist_ok=True)

        with open(os.path.join(base_dir, "intent.txt"), 'w', encoding='utf-8') as f:
            f.write(context["intent"])
        
        with open(os.path.join(base_dir, "input_spec.txt"), 'w', encoding='utf-8') as f:
            f.write(context["input_spec"].get("raw", ""))
            
        with open(os.path.join(base_dir, "rules.txt"), 'w', encoding='utf-8') as f:
            for i, rule in enumerate(context["rules"]):
                f.write(f"{i+1}. {rule}\n")
                
        with open(os.path.join(base_dir, "inverse_rules.txt"), 'w', encoding='utf-8') as f:
            for i, rule in enumerate(context["inverse_rules"]):
                f.write(f"{i+1}. {rule}\n")
                
        with open(os.path.join(base_dir, "rule_evals.csv"), 'w', encoding='utf-8') as f:
            f.write("ruleid,rule,grounded\n")
            for eval in context["rule_evaluations"]:
                ruleid = eval.get("ruleid", "")
                rule = eval.get("rule", "").replace(",", "\\,").replace("\n", "\\n")
                grounded = eval.get("grounded", "")
                f.write(f"{ruleid},\"{rule}\",{grounded}\n")
                
        with open(os.path.join(base_dir, "tests.csv"), 'w', encoding='utf-8') as f:
            f.write("ruleid,inverse,testinput,expectedoutput\n")
            for test in context["tests"]:
                ruleid = test.get("ruleid", "")
                inverse = "TRUE" if test.get("inverse", False) else "FALSE"
                testinput = test["testinput"].replace(",", "\\,").replace("\n", "\\n").replace("\"", "\"\"")
                expectedoutput = test.get("expectedoutput", "").replace(",", "\\,").replace("\n", "\\n").replace("\"", "\"\"")
                f.write(f"{ruleid},{inverse},\"{testinput}\",\"{expectedoutput}\"\n")
                
        with open(os.path.join(base_dir, "baseline_tests.txt"), 'w', encoding='utf-8') as f:
            for test in context["baseline_tests"]:
                f.write(f"{test['testinput']}\n\n===\n\n")
                
        with open(os.path.join(base_dir, "test_validity.csv"), 'w', encoding='utf-8') as f:
            f.write("testid,test,validity\n")
            for validity in context["test_validity"]:
                testid = validity.get("id", "")
                test = validity.get("test", "").replace(",", "\\,").replace("\n", "\\n").replace("\"", "\"\"")
                validity_status = validity.get("validity", "")
                f.write(f"{testid},\"{test}\",{validity_status}\n")
                
        with open(os.path.join(base_dir, "test_results.csv"), 'w', encoding='utf-8') as f:
            f.write("id,ruleid,rule,inverse,model,input,output,compliance\n")
            for result in context["test_results"]:
                result_id = result.get("id", "")
                ruleid = result.get("ruleid", "")
                rule = result.get("rule", "").replace(",", "\\,").replace("\n", "\\n").replace("\"", "\"\"")
                inverse = "TRUE" if result.get("inverse", False) else "FALSE"
                model = result.get("model", "")
                input_text = result.get("input", "").replace(",", "\\,").replace("\n", "\\n").replace("\"", "\"\"")
                output_text = result.get("output", "").replace(",", "\\,").replace("\n", "\\n").replace("\"", "\"\"")
                compliance = result.get("compliance", "")
                f.write(f"{result_id},{ruleid},\"{rule}\",{inverse},{model},\"{input_text}\",\"{output_text}\",{compliance}\n")
                
        with open(os.path.join(base_dir, "summary.md"), 'w', encoding='utf-8') as f:
            summary = context["summary"]
            f.write(f"# PromptPEX Test Results Summary\n\n")
            
            f.write(f"## Overview\n\n")
            f.write(f"<details><summary>Glossary</summary>\n\n")
            f.write(f"- Prompt Under Test (PUT) - like Program Under Test; the prompt\n")
            f.write(f"- Model Under Test (MUT) - Models being tested with the prompt\n")
            f.write(f"- Model Used by PromptPEX (MPP) - Model used for rule extraction & test generation\n\n")
            
            f.write(f"- Input Specification (IS) - Input constraints extracted from the prompt\n")
            f.write(f"- Output Rules (OR) - Output constraints extracted from the prompt\n")
            f.write(f"- Output Rules Groundedness (ORG) - Whether rules are grounded in the prompt\n\n")
            
            f.write(f"- Prompt Under Test Intent (PUTI) - Primary intent extracted from the prompt\n\n")
            
            f.write(f"- PromptPEX Tests (PPT) - Test cases generated using rules\n")
            f.write(f"- Baseline Tests (BT) - Generic test cases without rule focus\n")
            f.write(f"</details>\n\n")
            
            f.write(f"## Rules\n")
            f.write(f"- Total rules: {summary['total_rules']}\n")
            f.write(f"- Inverse rules: {summary['inverse_rules']}\n")
            f.write(f"- Grounded rules: {summary['grounded_rules']} ({summary['grounded_percentage']}%)\n\n")
            
            f.write(f"## Tests\n")
            f.write(f"- Total tests: {summary['total_tests']}\n")
            f.write(f"- Rule-based tests: {summary['rule_tests']}\n")
            f.write(f"- Baseline tests: {summary['baseline_tests']}\n")
            f.write(f"- Valid tests: {summary['valid_tests']} ({summary['valid_percentage']}%)\n\n")
            
            f.write(f"## Test Results\n")
            f.write(f"- Total test runs: {summary['test_results']}\n")
            f.write(f"- Compliant outputs: {summary['compliant_tests']} ({summary['compliant_percentage']}%)\n\n")
            
            if "model_results" in summary:
                f.write(f"### Model-specific Results\n")
                for model, stats in summary["model_results"].items():
                    percentage = round((stats["ok"] / stats["total"] * 100) if stats["total"] else 0, 1)
                    f.write(f"- {model}: {stats['ok']}/{stats['total']} ({percentage}%) compliant\n")
        
        logger.info(f"Component files saved to {base_dir}")
        
        html_report_path = os.path.join(base_dir, "report.html")
        try:
            self._generate_html_report(context, html_report_path)
        except Exception as e:
            logger.error(f"Error generating HTML report to {html_report_path}: {e}")
        
    def _generate_html_report(self, context: Dict[str, Any], output_path: str):
        summary = context["summary"]
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PromptPEX Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
        h1, h2, h3, h4 {{ color: #333; margin-top: 30px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .card {{ background: #fff; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stats {{ display: flex; flex-wrap: wrap; gap: 20px; }}
        .stat-card {{ background: #f9f9f9; border-radius: 8px; padding: 15px; flex: 1; min-width: 200px; }}
        .progress-bar {{ height: 10px; background: #e0e0e0; border-radius: 5px; overflow: hidden; margin-top: 5px; }}
        .progress {{ height: 100%; background: #4CAF50; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .model-chart {{ height: 250px; margin-top: 30px; }}
        pre {{ background: #f5f5f5; padding: 15px; border-radius: 5px; overflow: auto; }}
        .tab {{ overflow: hidden; border: 1px solid #ccc; background-color: #f1f1f1; }}
        .tab button {{ background-color: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 14px 16px; }}
        .tab button:hover {{ background-color: #ddd; }}
        .tab button.active {{ background-color: #ccc; }}
        .tabcontent {{ display: none; padding: 6px 12px; border: 1px solid #ccc; border-top: none; }}
        .show {{ display: block; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>PromptPEX Test Results</h1>
        
        <div class="card">
            <h2>Summary</h2>
            <div class="stats">
                <div class="stat-card">
                    <h3>Rules</h3>
                    <p>{summary['total_rules']} total rules ({summary['grounded_rules']} grounded)</p>
                    <div class="progress-bar">
                        <div class="progress" style="width: {summary['grounded_percentage']}%;"></div>
                    </div>
                    <small>{summary['grounded_percentage']}% grounded</small>
                </div>
                
                <div class="stat-card">
                    <h3>Tests</h3>
                    <p>{summary['total_tests']} total tests ({summary['valid_tests']} valid)</p>
                    <div class="progress-bar">
                        <div class="progress" style="width: {summary['valid_percentage']}%;"></div>
                    </div>
                    <small>{summary['valid_percentage']}% valid</small>
                </div>
                
                <div class="stat-card">
                    <h3>Test Results</h3>
                    <p>{summary['test_results']} test runs ({summary['compliant_tests']} compliant)</p>
                    <div class="progress-bar">
                        <div class="progress" style="width: {summary['compliant_percentage']}%;"></div>
                    </div>
                    <small>{summary['compliant_percentage']}% compliant</small>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>Model Results</h2>
            <table>
                <tr>
                    <th>Model</th>
                    <th>Compliant</th>
                    <th>Total</th>
                    <th>Compliance Rate</th>
                </tr>
                """
                
        for model, stats in summary.get("model_results", {}).items():
            percentage = round((stats["ok"] / stats["total"] * 100) if stats["total"] else 0, 1)
            html += f"""
                <tr>
                    <td>{model}</td>
                    <td>{stats['ok']}</td>
                    <td>{stats['total']}</td>
                    <td>{percentage}%</td>
                </tr>"""
                
        html += """
            </table>
        </div>
        
        <div class="card">
            <div class="tab">
                <button class="tablinks active" onclick="openTab(event, 'Rules')">Rules</button>
                <button class="tablinks" onclick="openTab(event, 'Tests')">Tests</button>
                <button class="tablinks" onclick="openTab(event, 'Results')">Results</button>
            </div>
            
            <div id="Rules" class="tabcontent show">
                <h3>Output Rules</h3>
                <table>
                    <tr>
                        <th>#</th>
                        <th>Rule</th>
                        <th>Grounded</th>
                    </tr>
        """
        
        for i, rule in enumerate(context.get("rules", []), 1):
            grounded = "Unknown"
            for eval in context.get("rule_evaluations", []):
                if eval.get("ruleid") == i:
                    grounded = "Yes" if eval.get("grounded") == "ok" else "No"
                    
            html += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{rule}</td>
                        <td>{grounded}</td>
                    </tr>"""
        
        html += """
                </table>
                
                <h3>Inverse Rules</h3>
                <table>
                    <tr>
                        <th>#</th>
                        <th>Inverse Rule</th>
                    </tr>
        """
        
        for i, rule in enumerate(context.get("inverse_rules", []), 1):
            html += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{rule}</td>
                    </tr>"""
                    
        html += """
                </table>
            </div>
            
            <div id="Tests" class="tabcontent">
                <h3>Rule-Based Tests</h3>
                <table>
                    <tr>
                        <th>Rule ID</th>
                        <th>Inverse</th>
                        <th>Test Input</th>
                        <th>Expected Output</th>
                    </tr>
        """
        
        for test in context.get("tests", []):
            inverse = "Yes" if test.get("inverse", False) else "No"
            html += f"""
                    <tr>
                        <td>{test.get('ruleid', '')}</td>
                        <td>{inverse}</td>
                        <td>{test.get('testinput', '')[:100]}...</td>
                        <td>{test.get('expectedoutput', '')[:100]}...</td>
                    </tr>"""
                    
        html += """
                </table>
                
                <h3>Baseline Tests</h3>
                <table>
                    <tr>
                        <th>#</th>
                        <th>Test Input</th>
                    </tr>
        """
        
        for i, test in enumerate(context.get("baseline_tests", []), 1):
            html += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{test.get('testinput', '')[:150]}...</td>
                    </tr>"""
                    
        html += """
                </table>
            </div>
            
            <div id="Results" class="tabcontent">
                <h3>Test Results</h3>
                <p>Showing up to 50 most recent results</p>
                <table>
                    <tr>
                        <th>Rule ID</th>
                        <th>Model</th>
                        <th>Input (excerpt)</th>
                        <th>Output (excerpt)</th>
                        <th>Compliance</th>
                    </tr>
        """
        
        for result in context.get("test_results", [])[:50]:
            compliance = result.get('compliance', '')
            compliance_display = "✓" if compliance == "ok" else "✗" if compliance == "err" else "-"
            html += f"""
                    <tr>
                        <td>{result.get('ruleid', 'baseline')}</td>
                        <td>{result.get('model', '')}</td>
                        <td>{result.get('input', '')[:80]}...</td>
                        <td>{result.get('output', '')[:80]}...</td>
                        <td>{compliance_display}</td>
                    </tr>"""
                    
        html += """
                </table>
            </div>
        </div>
    </div>
    
    <script>
    function openTab(evt, tabName) {
        var i, tabcontent, tablinks;
        tabcontent = document.getElementsByClassName("tabcontent");
        for (i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
        }
        tablinks = document.getElementsByClassName("tablinks");
        for (i = 0; i < tablinks.length; i++) {
            tablinks[i].className = tablinks[i].className.replace(" active", "");
        }
        document.getElementById(tabName).style.display = "block";
        evt.currentTarget.className += " active";
    }
    </script>
</body>
</html>
        """
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"HTML report saved to {output_path}")
        except Exception as e:
            logger.error(f"Error writing HTML report to {output_path}: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Run PromptPEX analysis on a prompt file.")
    parser.add_argument("prompt_file", help="Path to the .prompty file to analyze.")
    parser.add_argument("output_json", help="Path to save the main output JSON results file.")
    parser.add_argument("--models", help="Comma-separated list of Azure deployment names to test against (e.g., gpt-4o,gpt-35-turbo). Defaults to AZURE_OPENAI_DEPLOYMENT env var or 'gpt-4o'.", default=None)
    parser.add_argument("--tests-per-rule", type=int, default=3, help="Number of tests to generate per rule.")
    parser.add_argument("--runs-per-test", type=int, default=1, help="Number of times to run each test against each model.")
    parser.add_argument("--no-generate-tests", action="store_false", dest="generate_tests", help="Disable test generation and execution.")

    args = parser.parse_args()

    models_list = args.models.split(',') if args.models else None

    integrator = PromptPexIntegrator(
        generate_tests=args.generate_tests,
        tests_per_rule=args.tests_per_rule,
        runs_per_test=args.runs_per_test,
        models_to_test=models_list
    )

    results = integrator.run(args.prompt_file, args.output_json)

    if results and results.get("status") != "error" and "summary" in results:
        print("\n--- PromptPEX Summary ---")
        print(json.dumps(results['summary'], indent=2))
        print(f"\nFull results saved to: {args.output_json}")
        component_dir = os.path.join(os.path.dirname(args.output_json), "promptpex_components")
        print(f"Component files (rules, tests, report.html, etc.) saved in: {component_dir}")
    elif results and results.get("status") == "error":
        print(f"\nPromptPEX failed: {results.get('reason')}")
    else:
        print("\nPromptPEX run finished.")