from src import InputSpec, StringFrontEnd, Module, TestCaseGenerator, AskLLMTestValidator, Mutator, Dbg, SemanticDiff, Utils, CLI
import sys, time, os, pathlib

# todo: add a classification test case sample
# todo: model downsizing
# todo: number of rules generated
# explain why this is a good input
# are there conflicts in the rules

args = CLI.parse_args()

input_file = args.input_file
input_dir_name = "/".join(input_file.split("/")[:-1])
input_file = input_file.split("/")[-1]
input_path = pathlib.Path(input_dir_name, input_file)

output_dir = os.getcwd()
if args.output_dir:
    output_dir = args.output_dir

dir_name = output_dir + "/" + input_file.split(".")[0]
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
if args.import_rules_from_file:
    rule_path = pathlib.Path(dir_name, args.import_rules_from_file)

if args.use_existing or args.use_existing_rules or args.import_rules_from_file:
    module = Module()
    module.import_rules(rule_path)
else:
    module = front_end.parse(system_prompt)
    module.export(rule_path)

if args.extract_rules:
    sys.exit(0)

test_path = pathlib.Path(dir_name, "tests.csv")
if args.import_tests_from_file:
    test_path = pathlib.Path(dir_name, args.import_tests_from_file)

input_spec_path = pathlib.Path(dir_name, "input_spec.txt")
IS = InputSpec(system_prompt)
IS.export_csv(input_spec_path)
input_spec = IS.import_csv(input_spec_path)

test_gen = TestCaseGenerator(module, system_prompt, test_path, input_spec)

if args.use_existing or args.use_existing_tests or args.import_tests_from_file:
    test_gen.import_csv(test_path)
else:
    test_gen.generate()
    test_gen.export_csv()

if args.gen_tests:
    sys.exit(0)

num_iterations = 101
if args.num_test_runs:
    print("TODO: Implement num_test_runs")
    num_iterations = args.num_test_runs

exec_model = "gpt-35-turbo"
if args.test_runner_model:
    exec_model = args.test_runner_model

original_test_run_path = pathlib.Path(dir_name, "variant-run-0.csv")
if args.import_test_results_from_file:
    original_test_run_path = pathlib.Path(dir_name, args.use_test_results_from_file)

test_runner = AskLLMTestValidator(module, system_prompt, system_prompt, exec_model, original_test_run_path)

if args.use_existing or args.use_existing_test_results or args.import_test_results_from_file:
    test_runner.importResults(original_test_run_path)
else:
    test_runner.append(test_path)
    test_runner.run_tests()

test_runner.print_results()

output_file_path = pathlib.Path(dir_name, "result.csv")
if args.output_run_file:
    output_file_path = pathlib.Path(dir_name, args.output_run_file)

Utils.join_csv_files(test_path, original_test_run_path, "rule id", output_file_path)

if args.run_tests:
    sys.exit(0)

result = 0
if not test_runner.all_passed():
    result = -1
    fixed_prompts = [system_prompt]
    new_failed_tests = [test_runner.get_failed_tests()]
    ImmutableRules = []
    for num in range(1, num_iterations):
        print(f"Trying variant {num}")
        fixed_prompt = Mutator(original_prompt).fix_prompt(test_runner.get_failed_tests(), fixed_prompts, new_failed_tests, ImmutableRules)
        if fixed_prompt == None:
            fixed_prompt = original_prompt
        fixed_prompts.append(fixed_prompt)
        with open(pathlib.Path(dir_name, f"variant-{num}.txt"), "w") as f:
            f.write(fixed_prompt)

        fixed = front_end.parse(fixed_prompt)
        fixed.export(pathlib.Path(dir_name, f"rules-{num}.csv"))

        new_test_runner = AskLLMTestValidator(fixed, fixed_prompt, fixed_prompt, exec_model, pathlib.Path(dir_name, f"variant-run-{num}.csv"))
        new_test_runner.append(test_path)
        new_test_runner.run_tests()
        new_test_runner.print_results()
        new_failed_tests.append(new_test_runner.get_failed_tests())

        if new_test_runner.all_passed():
            Diff = SemanticDiff(pathlib.Path(dir_name, f"rules-0.csv"), pathlib.Path(dir_name, f"rules-{num}.csv"))
            if Diff.is_same():
                print(f"All tests passed with variant {num}.")
                result = num
                break            
            else:
                user = input(f"Do you accept the changes to the rules: {Diff.get_changes()}? (y/n): ")
                if user == "y":
                    test_gen.update_tests(Diff)
                    result = num
                    break
                else:
                    ImmutableRules.append(fixed_prompts.pop())

        Utils.join_csv_files(pathlib.Path(dir_name, "tests.csv"), pathlib.Path(dir_name, f"variant-run-{num}.csv"), "rule id", pathlib.Path(dir_name, "result.csv"))

else:
    print("All tests passed with the original system prompt.")
    result = 0

if result == -1:
    print("Some tests failed. No variant found.")
    sys.exit(1)
            
result_system_prompt = open(pathlib.Path(dir_name, f"variant-{result}.txt"), "r").read()
result_rules = pathlib.Path(dir_name, f"rules-{result}.csv")

module = Module()
module.import_rules(result_rules)

mutated_prompt = result_system_prompt
for num in range(1, 1000, 50):
    print("Mutating the variant")
    prompt_before_mutation = mutated_prompt
    mutator = Mutator(mutated_prompt)
    mutator.add_rules(3)
    mutated_prompt = mutator.get_prompt()

    if mutated_prompt is None:
        mutated_prompt = prompt_before_mutation
        continue

    with open(pathlib.Path(dir_name, f"mutant-final.txt"), "w") as f:
        f.write(mutated_prompt)

    variant = front_end.parse(mutated_prompt)
    variant.export(pathlib.Path(dir_name, "rules-variants.csv"))

    print("Test after mutation")
    test_runner = AskLLMTestValidator(module, result_system_prompt, mutated_prompt, exec_model, pathlib.Path(dir_name, f"mutant-run-{num}.csv"))
    test_runner.append(test_path)
    test_runner.run_tests()
    test_runner.print_results()
    if not test_runner.all_passed():
        sys.exit(0)