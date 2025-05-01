import os
import json
import logging
import hashlib
import csv
import io
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
PROMPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")

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
            models_to_test: List of models to test against
        """
        self.generate_tests = generate_tests
        self.tests_per_rule = tests_per_rule
        self.runs_per_test = runs_per_test
        self.models_to_test = models_to_test or ["gpt-4"]
        
        # Configure Azure OpenAI client
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
            
        # Set up Azure OpenAI client
        self._setup_openai_client()
        
        # Output directory setup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.timestamp = timestamp
        self.output_dir = os.path.join("output", f"promptpex_results_{timestamp}")
        os.makedirs(self.output_dir, exist_ok=True)
        
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

    def run(self, prompt_content: str, output_path: str) -> Dict[str, Any]:
        """Run the full PromptPEX pipeline.
        
        Args:
            prompt_content: The prompt to test (PUT - Prompt Under Test)
            output_path: Path to save the results
            
        Returns:
            Dictionary with results
        """
        if not self.generate_tests:
            logger.info("Test generation disabled, skipping PromptPEX")
            return {"status": "skipped", "reason": "Test generation disabled"}
        
        logger.info("Starting PromptPEX pipeline")
        
        context = self._create_context_obj(prompt_content)
        
        # Step 1: Extract intent
        logger.info("Step 1: Generating prompt intent (PUTI)")
        context["intent"] = self._extract_intent(prompt_content)
        
        # Step 2: Extract input specification
        logger.info("Step 2: Generating input specification (IS)")
        context["input_spec"] = self._generate_input_specification(prompt_content)
        
        # Step 3: Extract output rules
        logger.info("Step 3: Extracting output rules (OR)")
        context["rules"] = self._extract_output_rules(prompt_content)
        
        # Step 4: Generate inverse rules
        logger.info("Step 4: Generating inverse output rules (IOR)")
        context["inverse_rules"] = self._generate_inverse_rules(context["rules"], prompt_content)
        
        # Step 5: Evaluate rule groundedness
        logger.info("Step 5: Evaluating rule groundedness (ORG)")
        context["rule_evaluations"] = self._evaluate_rules_groundedness(context["rules"], prompt_content)
        
        # Step 6: Generate tests based on rules
        logger.info("Step 6: Generating prompt tests (PPT)")
        context["tests"] = self._generate_tests(prompt_content, context["input_spec"], 
                                               context["rules"], context["inverse_rules"])
        
        # Step 7: Generate baseline tests
        logger.info("Step 7: Generating baseline tests (BT)")
        context["baseline_tests"] = self._generate_baseline_tests(prompt_content)
        
        # Step 8: Evaluate test validity
        logger.info("Step 8: Evaluating test validity (TV)")
        context["test_validity"] = self._evaluate_test_validity(context["tests"] + context["baseline_tests"], 
                                                             context["input_spec"])
        
        # Step 9: Run tests against models
        logger.info("Step 9: Running tests and checking compliance (TO & TNC)")
        context["test_results"] = self._run_tests(prompt_content, context["tests"] + context["baseline_tests"])
        
        # Generate summary
        context["summary"] = self._generate_summary(context)
        
        # Save results
        self._save_results(context, output_path)
        
        return context
    
    def _create_context_obj(self, prompt_content: str) -> Dict[str, Any]:
        """Create the context object with proper naming for components."""
        context = {
            "prompt": prompt_content,
            "name": f"prompt_{self.timestamp}",
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
            
            # Extract content
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
            
            # Extract content
            content = response["choices"][0]["message"]["content"].strip()
            
            # Parse input spec into a structured format
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
            
            # Replace placeholders in template
            system_prompt = system_prompt.replace("{{instructions}}", "")
            system_prompt = system_prompt.replace("{{num_rules}}", "0")
            user_prompt = user_prompt_template.replace("{{input_data}}", prompt)
            
            response = self._call_openai(system_prompt, user_prompt)
            
            # Extract rules from response
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
            
            # Replace placeholders in template
            system_prompt = system_prompt.replace("{{instructions}}", "")
            user_prompt = user_prompt_template.replace("{{rule}}", "\n".join(rules))
            
            response = self._call_openai(system_prompt, user_prompt)
            
            # Extract inverse rules
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
                # Replace placeholders in template for each rule
                user_prompt = user_prompt_template.replace("{{ rule }}", rule)
                user_prompt = user_prompt.replace("{{ description }}", prompt)
                
                response = self._call_openai(system_prompt, user_prompt)
                
                # Extract evaluation
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
            
            # Process regular rules
            for rule_id, rule in enumerate(rules, 1):
                # Create prompt for test generation
                user_prompt = "List of Rules:\n{}".format(rule)
                
                # Format the input spec as text
                input_spec_text = "\n".join(input_spec.get("input_constraints", []))
                
                # Replace all placeholders
                current_system = system_prompt.replace("{{input_spec}}", input_spec_text)
                current_system = current_system.replace("{{context}}", prompt)
                current_system = current_system.replace("{{num}}", str(self.tests_per_rule))
                current_system = current_system.replace("{{rule}}", rule)
                current_system = current_system.replace("{{num_rules}}", "1")
                
                response = self._call_openai(current_system, user_prompt)
                
                # Parse CSV response
                content = response["choices"][0]["message"]["content"].strip()
                tests = self._parse_csv_tests(content, rule_id, rule, is_inverse=False)
                all_tests.extend(tests)
                
            # Process inverse rules
            for rule_id, rule in enumerate(inverse_rules, 1):
                # Create prompt for test generation
                user_prompt = "List of Rules:\n{}".format(rule)
                
                # Format the input spec as text
                input_spec_text = "\n".join(input_spec.get("input_constraints", []))
                
                # Replace all placeholders
                current_system = system_prompt.replace("{{input_spec}}", input_spec_text)
                current_system = current_system.replace("{{context}}", prompt)
                current_system = current_system.replace("{{num}}", str(self.tests_per_rule))
                current_system = current_system.replace("{{rule}}", rule)
                current_system = current_system.replace("{{num_rules}}", "1")
                
                response = self._call_openai(current_system, user_prompt)
                
                # Parse CSV response
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
            # Skip header and parse CSV
            lines = csv_content.split('\n')
            if len(lines) > 1:  # Only if there's more than just the header
                csv_content = '\n'.join(lines)
            
            # Use Python's CSV module to parse the CSV content
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
            
            # Replace placeholders
            system_prompt = system_prompt.replace("{{num}}", str(self.tests_per_rule))
            user_prompt = user_prompt_template.replace("{{prompt}}", prompt)
            
            response = self._call_openai(system_prompt, user_prompt)
            
            # Extract and process tests
            content = response["choices"][0]["message"]["content"].strip()
            
            # Split by the === delimiter
            test_contents = content.split("===")
            tests = []
            
            for test_content in test_contents:
                test_input = test_content.strip()
                if test_input:  # Skip empty entries
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
                # Replace placeholders
                current_user_prompt = user_prompt_template.replace("{{test}}", test["testinput"])
                current_system_prompt = system_prompt.replace("{{input_spec}}", input_spec_text)
                
                response = self._call_openai(current_system_prompt, current_user_prompt)
                
                # Extract result
                content = response["choices"][0]["message"]["content"].strip()
                
                # Get last line for decision
                lines = content.strip().split("\n")
                decision = lines[-1].strip().upper() if lines else "ERR"
                
                # Create evaluation object
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
            # Step 1: Get model response (TO)
            test_input = test["testinput"]
            response = self._call_openai(prompt, test_input, model=model)
            model_output = response["choices"][0]["message"]["content"]
            
            # Create initial result object
            test_id = f"{test.get('ruleid', 'baseline')}-{model}-{run_id}"
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
            
            # Step 2: Check compliance if this is a rule-based test (TNC)
            if test.get('rule'):
                # Replace placeholders in evaluation prompt
                current_system_prompt = eval_system_prompt.replace("{{ system }}", prompt)
                current_user_prompt = eval_user_prompt_template.replace("{{ result }}", model_output)
                
                eval_response = self._call_openai(current_system_prompt, current_user_prompt)
                eval_content = eval_response["choices"][0]["message"]["content"].strip()
                
                # Extract compliance decision from last line
                lines = eval_content.strip().split("\n")
                decision = lines[-1].strip().upper() if lines else "ERR"
                
                # For inverse rules, we reverse the compliance check
                expected_compliance = "err" if test.get('inverse', False) else "ok"
                actual_compliance = "ok" if decision == "OK" else "err"
                
                # Add compliance information to result
                result["complianceText"] = eval_content
                result["compliance"] = actual_compliance
                result["compliance_matched"] = actual_compliance == expected_compliance
            
            return result
            
        except Exception as e:
            logger.error(f"Error running test {test.get('testinput', '')[:30]} on model {model}: {e}")
            test_id = f"{test.get('ruleid', 'baseline')}-{model}-{run_id}"
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
        """Generate a summary of the PromptPEX results."""
        rules = context.get("rules", [])
        rule_evaluations = context.get("rule_evaluations", [])
        test_results = context.get("test_results", [])
        tests = context.get("tests", [])
        baseline_tests = context.get("baseline_tests", [])
        test_validity = context.get("test_validity", [])
        
        # Count grounded rules
        grounded_rules = sum(1 for r in rule_evaluations if r.get("grounded") == "ok")
        
        # Count valid tests
        valid_tests = sum(1 for t in test_validity if t.get("validity") == "ok")
        
        # Count compliance results
        rule_test_results = [r for r in test_results if "compliance" in r]
        compliant_tests = sum(1 for r in rule_test_results if r.get("compliance") == "ok")
        
        # Group by model
        model_results = {}
        for result in test_results:
            model = result.get("model", "unknown")
            if model not in model_results:
                model_results[model] = {"total": 0, "ok": 0}
            
            if "compliance" in result:
                model_results[model]["total"] += 1
                if result.get("compliance") == "ok":
                    model_results[model]["ok"] += 1
        
        # Calculate percentages
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
        # Split frontmatter and content
        parts = content.split("---", 2)
        if len(parts) >= 3:
            # Extract content part (after second ---)
            content_part = parts[2].strip()
            
            # Split into system and user prompts
            prompts = content_part.split("user:", 1)
            
            if len(prompts) == 2:
                system_prompt = prompts[0].replace("system:", "", 1).strip()
                user_prompt = prompts[1].strip()
                return system_prompt, user_prompt
        
        # Fall back if format can't be parsed
        raise ValueError("Invalid prompty file format")
    
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
                temperature=0.2,  # Low temperature for deterministic responses
                max_tokens=4000,
                n=1,
                stop=None,
                timeout=30
            )
            
            # Convert the response to match the old format expected by the rest of the code
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
    
    def _save_results(self, context: Dict[str, Any], output_path: str):
        """Save results to files."""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save full results JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(context, f, indent=2)
            
        logger.info(f"Full results saved to {output_path}")
        
        # Create component directory
        base_dir = os.path.join(os.path.dirname(output_path), "promptpex_components")
        os.makedirs(base_dir, exist_ok=True)
        
        # Save intent
        with open(os.path.join(base_dir, "intent.txt"), 'w', encoding='utf-8') as f:
            f.write(context["intent"])
        
        # Save input spec
        with open(os.path.join(base_dir, "input_spec.txt"), 'w', encoding='utf-8') as f:
            f.write(context["input_spec"].get("raw", ""))
            
        # Save rules
        with open(os.path.join(base_dir, "rules.txt"), 'w', encoding='utf-8') as f:
            for i, rule in enumerate(context["rules"]):
                f.write(f"{i+1}. {rule}\n")
                
        # Save inverse rules
        with open(os.path.join(base_dir, "inverse_rules.txt"), 'w', encoding='utf-8') as f:
            for i, rule in enumerate(context["inverse_rules"]):
                f.write(f"{i+1}. {rule}\n")
                
        # Save rule evaluations
        with open(os.path.join(base_dir, "rule_evals.csv"), 'w', encoding='utf-8') as f:
            f.write("ruleid,rule,grounded\n")
            for eval in context["rule_evaluations"]:
                ruleid = eval.get("ruleid", "")
                rule = eval.get("rule", "").replace(",", "\\,").replace("\n", "\\n")
                grounded = eval.get("grounded", "")
                f.write(f"{ruleid},\"{rule}\",{grounded}\n")
                
        # Save tests in CSV format
        with open(os.path.join(base_dir, "tests.csv"), 'w', encoding='utf-8') as f:
            f.write("ruleid,inverse,testinput,expectedoutput\n")
            for test in context["tests"]:
                ruleid = test.get("ruleid", "")
                inverse = "TRUE" if test.get("inverse", False) else "FALSE"
                testinput = test["testinput"].replace(",", "\\,").replace("\n", "\\n").replace("\"", "\"\"")
                expectedoutput = test.get("expectedoutput", "").replace(",", "\\,").replace("\n", "\\n").replace("\"", "\"\"")
                f.write(f"{ruleid},{inverse},\"{testinput}\",\"{expectedoutput}\"\n")
                
        # Save baseline tests
        with open(os.path.join(base_dir, "baseline_tests.txt"), 'w', encoding='utf-8') as f:
            for test in context["baseline_tests"]:
                f.write(f"{test['testinput']}\n\n===\n\n")
                
        # Save test validity
        with open(os.path.join(base_dir, "test_validity.csv"), 'w', encoding='utf-8') as f:
            f.write("testid,test,validity\n")
            for validity in context["test_validity"]:
                testid = validity.get("id", "")
                test = validity.get("test", "").replace(",", "\\,").replace("\n", "\\n").replace("\"", "\"\"")
                validity_status = validity.get("validity", "")
                f.write(f"{testid},\"{test}\",{validity_status}\n")
                
        # Save test results
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
                
        # Save summary as Markdown
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
        
        # Save report (HTML)
        self._generate_html_report(context, os.path.join(base_dir, "report.html"))
        
    def _generate_html_report(self, context: Dict[str, Any], output_path: str):
        """Generate an HTML report for better visualization."""
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
            # Find matching evaluation
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
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
            
        logger.info(f"HTML report saved to {output_path}")

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    integrator = PromptPexIntegrator()
    
    # Load prompt
    with open("optimized_prompt.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
        prompt = data["final_prompt_with_safety"]
        
    # Run tests
    results = integrator.run(prompt, "promptpex_results.json")
    
    print(f"Summary:\n{json.dumps(results['summary'], indent=2)}")