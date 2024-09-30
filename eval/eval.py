import sys
sys.path.insert(0, '..')

from src import InputSpec, LLMFrontEnd, StringFrontEnd, Module, TestCaseGenerator, AskLLMTestValidator, Mutator, Dbg, SemanticDiff, Utils, CLI, Rule
import sys, time, os, pathlib
import argparse
import re
import shutil
import csv

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
    valid_tests_index = []
    for test in tests:
        result = LLMFrontEnd().check_violation_with_input_spec(test, input_spec)
        if result is not None and "0" in result:
            valid_tests_index.append(tests.index(test))
    return valid_tests_index

def emb_dedupe(reasons):
    return 0 # TODO remove entirely
    #reasons = [item for item in reasons if item]
    #if len(reasons) == 0:
    #    return 0
    #if len(reasons) == 1:
    #    return 1
    # from wordllama import WordLlama
    # wl = WordLlama.load(config="l3_supercat", dim=1024)
    #wl.binary = False
    #return len(wl.deduplicate(reasons, threshold=0.3))

def exportTables(result, dir_name):
	import pandas as pd
	data = result

    # Convert nested dicts to dataframes
	def prepare_dataframe(primary_keys, data_dict):
		all_models = list(set(m['model'] for d in data_dict.values() for m in d['failures']))
		rows = []
		for key in primary_keys:
			row = [data_dict[key]['name'], data_dict[key].get('count'), data_dict[key].get('grounded', data_dict[key].get('valid', None))]
			for model in all_models:
				failures = next((f['percentage'] for f in data_dict[key]['failures'] if f['model'] == model), None)
				row.append(failures)
			for model in all_models:
				valid_failures = next((f['percentage'] for f in data_dict[key]['valid_failures'] if f['model'] == model), None)
				row.append(valid_failures)
			row += [len(data_dict[key].get('categories_failures', [])), len(data_dict[key].get('valid_categories_failures', []))]
			row += [len(data_dict[key].get('categories_failures_emb', [])), len(data_dict[key].get('valid_categories_failures_emb', []))]
			rows.append(row)
		columns = (
			['name', 'count', 'valid'] +
			[f'{model}-failures' for model in all_models] +
			[f'{model}-valid_failures' for model in all_models] +
			['categories_failures', 'valid_categories_failures'] +
			['categories_failures_emb', 'valid_categories_failures_emb']
		)
		return pd.DataFrame(rows, columns=columns)

	rules_df = prepare_dataframe(['rules'], data)
	rules_markdown = rules_df.to_markdown(index=False)

	comparison_df = prepare_dataframe(['tests', 'baseline'], data)
	comparison_df['name'] = ['sammo-pos-prompt-tests', 'sammo-pos-prompt-baseline']
	comparison_markdown = comparison_df.to_markdown(index=False)

	# Write markdowns to files
	with open(pathlib.Path(dir_name, "rules_table.md"), "w") as file:
		file.write("# Table 1: Rules\n\n")
		file.write(rules_markdown)

	with open(pathlib.Path(dir_name, "comparison_table.md"), "w") as file:
		file.write("# Table 2: System Vs Baseline\n\n")
		file.write(comparison_markdown)

if __name__ == "__main__":
    CLI = argparse.ArgumentParser(description="PromptPex Eval CLI")
    CLI.add_argument("--input-file", "-i", help="path to the input prompt file")
    CLI.add_argument("--output-dir", "-o", help="Output dir where all the artifacts will be stored. Default is the current directory")
    CLI.add_argument("--input-dir", "-id", help="Input dir")
    # model name, default is gpt-35-turbo
    CLI.add_argument("--test-runner-model", "-m", help="Model used for running tests")
    # number of times to run the test, default is 1
    CLI.add_argument("--num-tests", "-t", help="Number of times to run the test", type=int, default=1)
    # number of test sets to generate, default is 1
    CLI.add_argument("--num-test-sets", "-n", help="Number of test sets to generate", type=int, default=1)
    # take input as csv file but do not allow input file or input dir
    CLI.add_argument("--csv", "-c", help="Take input as csv file", type=str)
    # Only generate tests and do not run them
    CLI.add_argument("--only-gen", "-g", help="Only generate tests and do not run them", action="store_true")

    args = CLI.parse_args()

    input_file_list = []

    if args.csv:
        # create a unique directory for the csv file name
        csv_file = pathlib.Path(args.csv)
        # name of the file without extension
        csv_input_file = csv_file.stem
        # create a directory with the name of the file
        dir_name = os.getcwd() + "/tmp/" + csv_input_file
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
        os.makedirs(dir_name, exist_ok=True)
        # for each row in the csv file, create a file with the name of the row index like 0.txt
        with open(csv_file, newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            csv_data = list(csv_reader)
            for index, row in enumerate(csv_data):
                line = row[0]
                with open(pathlib.Path(dir_name, f"{index}.txt"), "w") as f:
                    f.write(line)

        args.input_dir = dir_name
        if args.output_dir is None:
            args.output_dir = os.getcwd() + "/result/" + csv_input_file

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
        print(input_path)

        _result ={}
        dir_name = output_dir + "/" + input_path.stem
        os.makedirs(dir_name, exist_ok=True)

        if pathlib.Path(dir_name, "tests.csv").exists():
            print('tests already exists, skip')
            continue

        with open(input_path, "r") as f:
            system_prompt = f.read()

        with open(pathlib.Path(dir_name, "variant-0.txt"), "w") as f:
            f.write(system_prompt)

        Dbg.set_debug_file(pathlib.Path(dir_name, "log.txt"))

        # Extract rules
        print("Extracting rules")
        original_prompt = system_prompt

        front_end = StringFrontEnd()

        module = None

        rule_path = pathlib.Path(dir_name, "rules-0.csv")
        if rule_path.exists():
            module = Module()
            module.import_rules(rule_path)
        else:
            module = front_end.parse(system_prompt)
            module.export(rule_path)

        # Check if all rules are grounded
        print("Checking if all rules are grounded")
        total, grounded = check_rules_grounded(module, system_prompt)
        percent_grounded = grounded / total * 100

        # Initialize Rules results
        _result["rules"] = {"name": input_path.stem, "count": total, "grounded": percent_grounded, "failures": [], "valid_failures": [], "categories_failures": [], "valid_categories_failures": [], "categories_failures_emb": [], "valid_categories_failures_emb": []}

        # Augment prompt for checking exhaustive coverage
        print("Extracting intent")
        intent = LLMFrontEnd().extract_intent(system_prompt)
        output_spec = ""
        for inst in module.instructions:
            if isinstance(inst, Rule):
                rule = inst.get_rule()
                output_spec += rule + "\n"
        augmented_prompt = f"""Task: {intent}
        Rules: {output_spec}
        """

        # Generate tests
        test_path = pathlib.Path(dir_name, "tests.csv")

        print("Extracting input spec")
        input_spec_path = pathlib.Path(dir_name, "input_spec.txt")

        IS = InputSpec(system_prompt)
        IS.export_csv(input_spec_path)

        input_spec = IS.import_csv(input_spec_path)

        test_gen = TestCaseGenerator(module, system_prompt, test_path, input_spec)

        if not test_path.exists():
            print("Generating tests using promptpex")
            test_gen.gen_all_tests(args.num_test_sets)

        if args.only_gen:
            continue

        original_test_run_path = pathlib.Path(dir_name, "variant-run-0.csv")
        test_runner = AskLLMTestValidator(module, system_prompt, system_prompt, None, original_test_run_path, batch_mode=False)
        test_runner.append(test_path)

        total = len(test_runner.tests)

        print("Checking valid tests")
        valid_tests_index = check_test_format(test_runner.tests, "\n".join(input_spec))
        total_valid = len(valid_tests_index)

        assert total != 0, "No tests found"
        assert total_valid != 0, "No valid tests found"

        percent_valid = total_valid / total * 100

        # Initialize Tests results
        _result["tests"] = {"name": input_path.stem, "count": total, "valid": percent_valid, "failures": [], "valid_failures": [], "categories_failures": [], "valid_categories_failures": [], "categories_failures_emb": [], "valid_categories_failures_emb": []}

        # Generate tests with baseline
        print("Generating tests with baseline")
        baseline_tests = LLMFrontEnd().generate_baseline_test(system_prompt, total)
        baseline_test_run_path = pathlib.Path(dir_name, "baseline-run-0.csv")
        baseline_test_runner = AskLLMTestValidator(module, system_prompt, system_prompt, None, baseline_test_run_path, batch_mode=False)
        baseline_test_runner.force_append_tests(baseline_tests)

        print("Checking valid tests in baseline")
        baseline_valid_tests_index = check_test_format(baseline_test_runner.tests, "\n".join(input_spec))

        baseline_total = len(baseline_test_runner.tests)
        baseline_total_valid = len(baseline_valid_tests_index)

        baseline_percent_valid = baseline_total_valid / baseline_total * 100
        # Initialize Baseline results
        _result["baseline"] = {"name": input_path.stem, "count": total, "valid": percent_valid, "failures": [], "valid_failures": [], "categories_failures": [], "valid_categories_failures": [], "categories_failures_emb": [], "valid_categories_failures_emb": []}

        _exec_model = "gpt-4o-mini"
        if args.test_runner_model:
            _exec_model = args.test_runner_model

        exec_models = _exec_model.split(",")
        for exec_model in exec_models:
            print(f"Running tests with model {exec_model}")

            variant_run_path = pathlib.Path(dir_name, f"variant-run-0-{exec_model}.csv")
            test_runner.updatePath(variant_run_path)
            test_runner.updateModel(exec_model)

            if not variant_run_path.exists():
                for i in range(args.num_tests):
                    print(f"Running test {i}")
                    test_runner.run_tests()
            else:
                test_runner.importResults(variant_run_path)

            failed = sum(1 for test in test_runner.results if test != "passed")

            _failure = failed
            _result["tests"]["failures"].append({"model": exec_model, "percentage": failed / total * 100})

            # Check categories
            reasons = test_runner.get_reasons()
            for idx in range(len(test_runner.results)):
                if test_runner.results[idx] == "passed":
                    reasons[idx] = ""

            reasons_str = "\n".join(reasons)
            categories = LLMFrontEnd().extract_failure_categories(reasons_str)
            categories_emb = emb_dedupe(reasons)

            _result["tests"]["categories_failures"].append({"model": exec_model, "count": categories})
            _result["tests"]["categories_failures_emb"].append({"model": exec_model, "count": categories_emb})

            failed = sum(1 for test in test_runner.results if test_runner.results.index(test) in valid_tests_index and test != "passed")

            _failure_valid = failed
            _result["tests"]["valid_failures"].append({"model": exec_model, "percentage": failed / total * 100})

            # Check categories
            reasons = test_runner.get_reasons()
            for idx in range(len(test_runner.results)):
                if test_runner.results[idx] == "passed" or idx not in valid_tests_index:
                    reasons[idx] = ""

            reasons_str = "\n".join(reasons)
            categories = LLMFrontEnd().extract_failure_categories(reasons_str)
            categories_emb = emb_dedupe(reasons)

            _result["tests"]["valid_categories_failures"].append({"model": exec_model, "count": categories})
            _result["tests"]["valid_categories_failures_emb"].append({"model": exec_model, "count": categories_emb})

            print("Running test for checking exhaustive coverage")
            augmented_test_run_path = pathlib.Path(dir_name, f"augmented-run-0-{exec_model}.csv")
            test_runner = AskLLMTestValidator(module, system_prompt, augmented_prompt, exec_model, augmented_test_run_path, batch_mode=False)
            test_runner.append(test_path)

            if not augmented_test_run_path.exists():
                for i in range(args.num_tests):
                    print(f"Running test {i}")
                    test_runner.run_tests()
            else:
                test_runner.importResults(augmented_test_run_path)

            failed = sum(1 for test in test_runner.results if test != "passed")
            _result["rules"]["failures"].append({"model": exec_model, "percentage": failed - _failure / total * 100})

            # Check categories
            reasons = test_runner.get_reasons()
            for idx in range(len(test_runner.results)):
                if test_runner.results[idx] == "passed":
                    reasons[idx] = ""

            reasons_str = "\n".join(reasons)
            categories = LLMFrontEnd().extract_failure_categories(reasons_str)
            categories_emb = emb_dedupe(reasons)

            _result["rules"]["categories_failures"].append({"model": exec_model, "count": categories})
            _result["rules"]["categories_failures_emb"].append({"model": exec_model, "count": categories_emb})

            failed = sum(1 for test in test_runner.results if test_runner.results.index(test) in valid_tests_index and test != "passed")

            # Check categories
            reasons = test_runner.get_reasons()
            for idx in range(len(test_runner.results)):
                if test_runner.results[idx] == "passed" or idx not in valid_tests_index:
                    reasons[idx] = ""

            reasons_str = "\n".join(reasons)
            categories = LLMFrontEnd().extract_failure_categories(reasons_str)
            categories_emb = emb_dedupe(reasons)

            _result["rules"]["valid_categories_failures"].append({"model": exec_model, "count": categories})
            _result["rules"]["valid_categories_failures_emb"].append({"model": exec_model, "count": categories_emb})
            _result["rules"]["valid_failures"].append({"model": exec_model, "percentage": failed - _failure_valid / total * 100})

            # baseline
            print("Running tests with baseline")
            baseline_test_runner_path = pathlib.Path(dir_name, f"baseline-run-0-{exec_model}.csv")
            baseline_test_runner.updatePath(baseline_test_runner_path)
            baseline_test_runner.updateModel(exec_model)

            if not baseline_test_runner_path.exists():
                for i in range(args.num_tests):
                    print(f"Running test {i}")
                    baseline_test_runner.run_tests()
            else:
                baseline_test_runner.importResults(baseline_test_runner_path)

            # Check categories
            reasons = baseline_test_runner.get_reasons()
            for idx in range(len(baseline_test_runner.results)):
                if baseline_test_runner.results[idx] == "passed":
                    reasons[idx] = ""

            reasons_str = "\n".join(reasons)
            categories = LLMFrontEnd().extract_failure_categories(reasons_str)
            categories_emb = emb_dedupe(reasons)

            _result["baseline"]["categories_failures"].append({"model": exec_model, "count": categories})
            _result["baseline"]["categories_failures_emb"].append({"model": exec_model, "count": categories_emb})

            failed = sum(1 for test in baseline_test_runner.results if test != "passed")
            _result["baseline"]["failures"].append({"model": exec_model, "percentage": failed / baseline_total * 100})

            # Check categories
            reasons = baseline_test_runner.get_reasons()
            for idx in range(len(baseline_test_runner.results)):
                if baseline_test_runner.results[idx] == "passed" or idx not in baseline_valid_tests_index:
                    reasons[idx] = ""

            reasons_str = "\n".join(reasons)
            categories = LLMFrontEnd().extract_failure_categories(reasons_str)
            categories_emb = emb_dedupe(reasons)

            _result["baseline"]["valid_categories_failures"].append({"model": exec_model, "count": categories})
            _result["baseline"]["valid_categories_failures_emb"].append({"model": exec_model, "count": categories_emb})

            failed = sum(1 for test in baseline_test_runner.results if test_runner.results.index(test) in valid_tests_index and test != "passed")
            _result["baseline"]["valid_failures"].append({"model": exec_model, "percentage": failed / baseline_total * 100})

        print(_result)
        exportTables(_result, dir_name)
