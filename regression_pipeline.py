from src import StringFrontEnd, Module, TestCaseGenerator, AskLLMTestValidator, Mutator, Dbg
import sys, time, os, pathlib

input_file = sys.argv[1]
input_dir_name = "".join(input_file.split("/")[:-1])
input_file = input_file.split("/")[-1]
input_path = pathlib.Path(input_dir_name, input_file)

dir_name = "results/" + input_file.split(".")[0]
os.makedirs(dir_name, exist_ok=True)

with open(input_path, "r") as f:
    system_prompt = f.read()

Dbg.set_debug_file(pathlib.Path(dir_name, "log.txt"))

original_prompt = system_prompt

mode = "init"
if len(sys.argv) > 2:
    mode = sys.argv[2]

test_runner = None
front_end = StringFrontEnd()

if mode == "init":
    module = Module()
    module = front_end.parse(system_prompt)
    module.export(pathlib.Path(dir_name, "rules.txt"))

    test_gen = TestCaseGenerator(module, system_prompt)
    test_gen.generate_negative(pathlib.Path(dir_name, "negative.txt"))
    test_gen.generate_positive(pathlib.Path(dir_name, "positive.txt"))

    test_runner = AskLLMTestValidator(module, system_prompt)
    test_runner.append(pathlib.Path(dir_name, "negative.txt"))
    test_runner.append(pathlib.Path(dir_name, "positive.txt"))
    test_runner.run_tests()
    test_runner.print_results()

if test_runner != None and test_runner.all_passed() and mode != "variant":
    print("All tests passed. No variant needed.")
else: 
    print("Some tests failed. Looking for variant.")
    variant_file = pathlib.Path(input_dir_name, input_file.split(".")[0] + "-variant.txt")
    if not os.path.exists(variant_file):
        print(f"variant does not exist")
        sys.exit(1)

    with open(variant_file, "r") as f:
        system_prompt = f.read()

module = Module()
module.import_rules(pathlib.Path(dir_name, "rules.txt"))
test_runner = AskLLMTestValidator(module, original_prompt)
test_runner.append(pathlib.Path(dir_name, "negative.txt"))
test_runner.append(pathlib.Path(dir_name, "positive.txt"))
test_runner.run_tests()
test_runner.print_results()

if test_runner.all_passed():
    print("All tests passed. Variant is correct.")
else:
    print("Some tests failed. Variant is incorrect.")
    sys.exit(1)

mutated_prompt = system_prompt
for num in range(1, 1000, 50):
    print("Mutating the variant")
    mutator = Mutator(mutated_prompt)
    mutator.add_rules(3)
    mutated_prompt = mutator.get_prompt()
    variant = Module()
    variant = front_end.parse(mutated_prompt)
    variant.export(pathlib.Path(dir_name, "rules-variants.txt"))

    print("Test after mutation")
    test_runner = AskLLMTestValidator(module, original_prompt)
    test_runner.append(pathlib.Path(dir_name, "negative.txt"))
    test_runner.append(pathlib.Path(dir_name, "positive.txt"))
    test_runner.run_tests()
    test_runner.print_results()
    if not test_runner.all_passed():
        sys.exit(0)