import argparse
import sys
import pathlib

CLI = argparse.ArgumentParser(description="PromptPex CLI")
CLI.add_argument("--input-file", "-i", help="path to the input prompt file")
CLI.add_argument("--output-dir", "-o", help="Output dir where all the artifacts will be stored. Default is the current directory")

CLI.add_argument("--use-existing", "-u", help="Use existing artifacts: rules, tests and the first test run", action="store_true")

CLI.add_argument("--extract-rules", "-r", help="Extract rules for the input prompts and exit", action="store_true")
CLI.add_argument("--import-rules-from-file", "-rf", help="Import rules from the provided file")
CLI.add_argument("--use-existing-rules", "-ur", help="Use existing rules from rules-0.csv", action="store_true")

CLI.add_argument("--gen-tests", "-t", help="Generate tests and exit", action="store_true")
CLI.add_argument("--import-tests-from-file", "-tf", help="Extract tests from the given file")
CLI.add_argument("--use-existing-tests", "-ut", help="Use existing tests from tests.csv", action="store_true")

CLI.add_argument("--run-tests", "-rt", help="Run tests and exit", action="store_true")
CLI.add_argument("--num-test-runs", "-n", help="Number of test runs.", type=int)
CLI.add_argument("--import-test-results-from-file", "-ot", help="Use original test results from given file")
CLI.add_argument("--use-existing-test-results", "-utr", help="Use existing test results from variant-run-0.csv", action="store_true")

CLI.add_argument("--test-runner-model", "-m", help="Model used for running tests")
CLI.add_argument("--output-run-file", "-of", help="Output file for the test run results")