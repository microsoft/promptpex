from src import StringFrontEnd, Module, TestCaseGenerator, AskLLMTestValidator, Mutator, Dbg, SemanticDiff, Utils
import sys, time, os, pathlib

# todo: add a classification test case sample
# todo: model downsizing
# todo: number of rules generated
# explain why this is a good input
# are there conflicts in the rules

input_file = sys.argv[1]
input_dir_name = "/".join(input_file.split("/")[:-1])
input_file = input_file.split("/")[-1]
input_path = pathlib.Path(input_dir_name, input_file)

input_dir_name = "".join(input_dir_name.split("samples/")[1:])
dir_name = "ap-results/" + input_dir_name + "/" + input_file.split(".")[0]
os.makedirs(dir_name, exist_ok=True)

mode = "init"
if len(sys.argv) > 2:
    mode = sys.argv[2]

with open(input_path, "r") as f:
    system_prompt = f.read()

with open(pathlib.Path(dir_name, "variant-0.txt"), "w") as f:
    f.write(system_prompt)

Dbg.set_debug_file(pathlib.Path(dir_name, "log.txt"))

original_prompt = system_prompt

num_iterations = 100

front_end = StringFrontEnd()

module = None
test_gen = None

if mode == "init":
    module = front_end.parse(system_prompt)
    module.export(pathlib.Path(dir_name, f"rules-0.txt"))

    test_gen = TestCaseGenerator(module, system_prompt, dir_name)
    test_gen.generate_negative(pathlib.Path(dir_name, f"negative.txt"))
    test_gen.generate_positive(pathlib.Path(dir_name, f"positive.txt"))
    test_gen.export_csv()
else:
    module = Module()
    module.import_rules(pathlib.Path(dir_name, "rules-0.txt"))

test_runner = AskLLMTestValidator(module, system_prompt, system_prompt, pathlib.Path(dir_name, "variant-run-0.csv"))
test_runner.append(pathlib.Path(dir_name, "negative.txt"))
test_runner.append(pathlib.Path(dir_name, "positive.txt"))
test_runner.run_tests()
test_runner.print_results()

Utils.join_csv_files(pathlib.Path(dir_name, "tests.csv"), pathlib.Path(dir_name, "variant-run-0.csv"), "rule id", pathlib.Path(dir_name, "result.csv"))

result = 0
if not test_runner.all_passed():
    result = -1
    fixed_prompts = [system_prompt]
    new_failed_tests = [test_runner.get_failed_tests()]
    ImmutableRules = ""
    for num in range(1, num_iterations):
        print(f"Trying variant {num}")
        fixed_prompt = Mutator(original_prompt).fix_prompt(test_runner.get_failed_tests(), fixed_prompts, new_failed_tests, ImmutableRules)
        fixed_prompts.append(fixed_prompt)
        with open(pathlib.Path(dir_name, f"variant-{num}.txt"), "w") as f:
            f.write(fixed_prompt)

        fixed = front_end.parse(fixed_prompt)
        fixed.export(pathlib.Path(dir_name, f"rules-{num}.txt"))

        new_test_runner = AskLLMTestValidator(fixed, fixed_prompt, fixed_prompt, pathlib.Path(dir_name, f"variant-run-{num}.csv"))
        new_test_runner.append(pathlib.Path(dir_name, "negative.txt"))
        new_test_runner.append(pathlib.Path(dir_name, "positive.txt"))
        new_test_runner.run_tests()
        new_test_runner.print_results()
        new_failed_tests.append(new_test_runner.get_failed_tests())

        if new_test_runner.all_passed():
            Diff = SemanticDiff(pathlib.Path(dir_name, f"rules.txt"), pathlib.Path(dir_name, f"rules-{num}.txt"))
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
result_rules = pathlib.Path(dir_name, f"rules-{result}.txt")

module = Module()
module.import_rules(result_rules)

mutated_prompt = result_system_prompt
for num in range(1, 1000, 50):
    print("Mutating the variant")
    mutator = Mutator(mutated_prompt)
    mutator.add_rules(3)
    mutated_prompt = mutator.get_prompt()

    with open(pathlib.Path(dir_name, f"mutant-final.txt"), "w") as f:
        f.write(mutated_prompt)

    variant = front_end.parse(mutated_prompt)
    variant.export(pathlib.Path(dir_name, "rules-variants.txt"))

    print("Test after mutation")
    test_runner = AskLLMTestValidator(module, result_system_prompt, mutated_prompt, pathlib.Path(dir_name, f"mutant-run-{num}.csv"))
    test_runner.append(pathlib.Path(dir_name, "negative.txt"))
    test_runner.append(pathlib.Path(dir_name, "positive.txt"))
    test_runner.run_tests()
    test_runner.print_results()
    if not test_runner.all_passed():
        sys.exit(0)