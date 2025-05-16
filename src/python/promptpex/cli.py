import argparse
import json
import os
import logging

from .core import PythonPromptPex

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the PromptPex CLI."""
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Run PromptPex analysis on a prompt file.")
    parser.add_argument("prompt_file", help="Path to the .prompty file to analyze.")
    parser.add_argument("output_json", help="Path to save the main output JSON results file.")
    parser.add_argument("--models", help="Comma-separated list of Azure deployment names to test against (e.g., gpt-4o,gpt-35-turbo). Defaults to AZURE_OPENAI_DEPLOYMENT env var or 'gpt-4o'.", default=None)
    parser.add_argument("--tests-per-rule", type=int, default=3, help="Number of tests to generate per rule.")
    parser.add_argument("--runs-per-test", type=int, default=1, help="Number of times to run each test against each model.")
    parser.add_argument("--no-generate-tests", action="store_false", dest="generate_tests", help="Disable test generation and execution.")

    args = parser.parse_args()

    models_list = args.models.split(',') if args.models else None

    integrator = PythonPromptPex(
        generate_tests=args.generate_tests,
        tests_per_rule=args.tests_per_rule,
        runs_per_test=args.runs_per_test,
        models_to_test=models_list
    )

    results = integrator.run(args.prompt_file, args.output_json)

    if results and results.get("status") != "error" and "summary" in results:
        print("\n--- PromptPex Summary ---")
        print(json.dumps(results['summary'], indent=2))
        print(f"\nFull results saved to: {args.output_json}")
        component_dir = os.path.join(os.path.dirname(args.output_json), "promptpex_components")
        print(f"Component files (rules, tests, report.html, etc.) saved in: {component_dir}")
    elif results and results.get("status") == "error":
        print(f"\nPromptPex failed: {results.get('reason')}")
    else:
        print("\nPromptPex run finished.")

if __name__ == "__main__":
    main()