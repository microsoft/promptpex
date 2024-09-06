import sys
sys.path.insert(0, '..')

from src import InputSpec, LLMFrontEnd, StringFrontEnd, Module, TestCaseGenerator, AskLLMTestValidator, Mutator, Dbg, SemanticDiff, Utils, CLI, Rule
import sys, time, os, pathlib
import argparse

def check_rules_grounded(module, system_prompt):
    total = len(module.instructions)
    grounded = 0
    for instr in module.instructions:
        if isinstance(instr, Rule):
            rule = instr.get_rule()
            result = LLMFrontEnd().check_rule_grounded(rule, system_prompt)
            if result == "0":
                grounded += 1
    return total, grounded

def check_test_format(tests, input_spec):
    total = len(tests)
    valid = 0
    valid_tests = []
    for test in tests:
        result = LLMFrontEnd().check_violation_with_input_spec(test, input_spec)
        if result == "0":
            valid += 1
            valid_tests.append(test)
    return total, valid, valid_tests

if __name__ == "__main__":
    CLI = argparse.ArgumentParser(description="PromptPex Eval CLI")
    CLI.add_argument("--input-file", "-i", help="path to the input prompt file")
    CLI.add_argument("--output-dir", "-o", help="Output dir where all the artifacts will be stored. Default is the current directory")
    CLI.add_argument("--input-dir", "-id", help="Input dir")
    # model name, default is gpt-35-turbo
    CLI.add_argument("--test-runner-model", "-m", help="Model used for running tests")
    args = CLI.parse_args()

    input_file_list = []
    if args.input_file is not None:
        input_file = args.input_file
        input_dir_name = "/".join(input_file.split("/")[:-1])
        input_file = input_file.split("/")[-1]
        input_path = pathlib.Path(input_dir_name, input_file)
        input_file_list.append(input_path)  

    if args.input_dir is not None:
        input_dir = args.input_dir
        for file in os.listdir(input_dir):
            if file.endswith(".txt") or file.endswith(".md"):
                input_file_list.append(pathlib.Path(input_dir, file))

    if len(input_file_list) == 0:
        print("No input file provided")
        sys.exit(1)

    output_dir = os.getcwd()
    if args.output_dir:
        output_dir = args.output_dir

    for input_path in input_file_list:
        dir_name = output_dir + "/" + input_path.stem        
        os.makedirs(dir_name, exist_ok=True)

        with open(input_path, "r") as f:
            system_prompt = f.read()

        with open(pathlib.Path(dir_name, "variant-0.txt"), "w") as f:
            f.write(system_prompt)

        Dbg.set_debug_file(pathlib.Path(dir_name, "log.txt"))

        original_prompt = system_prompt

        front_end = StringFrontEnd()

        module = None

        rule_path = pathlib.Path(dir_name, "rules-0.csv")
        module = front_end.parse(system_prompt)
        module.export(rule_path)

        grounded_result = pathlib.Path(output_dir, "num-grounded-rules.csv")
        with open(grounded_result, "a") as csv:
            total, grounded = check_rules_grounded(module, system_prompt)
            csv.write(f"{input_path.stem},{total},{grounded}\n")

        test_path = pathlib.Path(dir_name, "tests.csv")

        input_spec_path = pathlib.Path(dir_name, "input_spec.txt")
        IS = InputSpec(system_prompt)
        IS.export_csv(input_spec_path)
        input_spec = IS.import_csv(input_spec_path)

        test_gen = TestCaseGenerator(module, system_prompt, test_path, input_spec)

        test_gen.gen_all_tests(20)

        exec_model = "gpt-35-turbo"
        if args.test_runner_model:
            exec_model = args.test_runner_model

        original_test_run_path = pathlib.Path(dir_name, "variant-run-0.csv")
        test_runner = AskLLMTestValidator(module, system_prompt, system_prompt, exec_model, original_test_run_path)
        test_runner.append(test_path)

        input_spec_result = pathlib.Path(output_dir, "num-valid-tests.csv")
        with open(input_spec_result, "a") as csv:
            total, valid, valid_tests = check_test_format(test_runner.tests, "\n".join(input_spec))
            csv.write(f"{input_path.stem},{total},{valid}\n")

        test_runner.run_tests()

        failed_tests = pathlib.Path(output_dir, "num-failing-tests.csv")
        with open(failed_tests, "a") as csv:
            total = len(test_runner.results)
            failed = 0
            for test in test_runner.results:
                if test != "passed":
                    failed += 1
            csv.write(f"{input_path.stem},{total},{failed}\n")

        valid_test_run_path = pathlib.Path(dir_name, "valid-run-0.csv")
        test_runner = AskLLMTestValidator(module, system_prompt, system_prompt, exec_model, valid_test_run_path)
        test_runner.force_append_tests(valid_tests)
        test_runner.run_tests()

        failed_tests = pathlib.Path(output_dir, "num-valid-failing-tests.csv")
        with open(failed_tests, "a") as csv:
            total = len(test_runner.results)
            failed = 0
            for test in test_runner.results:
                if test != "passed":
                    failed += 1
            csv.write(f"{input_path.stem},{total},{failed}\n")

        intent = LLMFrontEnd().extract_intent(system_prompt)
        output_spec = ""
        for inst in module.instructions:
            if isinstance(inst, Rule):
                rule = inst.get_rule()
                output_spec += rule + "\n"
        augmented_prompt = f"""Task: {intent}
        Rules: {output_spec}
        """
        print(augmented_prompt)
        augmented_test_run_path = pathlib.Path(dir_name, "augmented-run-0.csv")
        test_runner = AskLLMTestValidator(module, system_prompt, augmented_prompt, exec_model, augmented_test_run_path)
        test_runner.append(test_path)
        test_runner.run_tests()

        failed_tests_with_rules = pathlib.Path(output_dir, "num-failing-tests-with-rules.csv")
        with open(failed_tests_with_rules, "a") as csv:
            total = len(test_runner.results)
            failed = 0
            for test in test_runner.results:
                if test != "passed":
                    failed += 1
            csv.write(f"{input_path.stem},{total},{failed}\n")

        # baseline

        tests = LLMFrontEnd().generate_baseline_test(system_prompt, 20)
        baseline_test_run_path = pathlib.Path(dir_name, "baseline-run-0.csv")
        test_runner = AskLLMTestValidator(module, system_prompt, system_prompt, exec_model, baseline_test_run_path)
        test_runner.force_append_tests(tests)

        input_spec_result = pathlib.Path(output_dir, "num-baseline-valid-tests.csv")
        with open(input_spec_result, "a") as csv:
            total, valid, valid_tests = check_test_format(test_runner.tests, "\n".join(input_spec))
            csv.write(f"{input_path.stem},{total},{valid}\n")

        test_runner.run_tests()

        failed_tests = pathlib.Path(output_dir, "num-baseline-failing-tests.csv")
        with open(failed_tests, "a") as csv:
            total = len(test_runner.results)
            failed = 0
            for test in test_runner.results:
                if test != "passed":
                    failed += 1
            csv.write(f"{input_path.stem},{total},{failed}\n")

        valid_test_run_path = pathlib.Path(dir_name, "baseline-valid-run-0.csv")
        test_runner = AskLLMTestValidator(module, system_prompt, system_prompt, exec_model, valid_test_run_path)
        test_runner.force_append_tests(valid_tests)
        test_runner.run_tests()

        failed_tests = pathlib.Path(output_dir, "num-baseline-valid-failing-tests.csv")
        with open(failed_tests, "a") as csv:
            total = len(test_runner.results)
            failed = 0
            for test in test_runner.results:
                if test != "passed":
                    failed += 1
            csv.write(f"{input_path.stem},{total},{failed}\n")