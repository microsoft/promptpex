from src import StringFrontEnd, Module, TestCaseGenerator, AskLLMTestValidator, Mutator, Dbg
import time, os, pathlib

time_stamp = time.strftime("%Y%m%d-%H%M%S")
dir_name = "result-" + time_stamp
os.makedirs(dir_name)

input_file = pathlib.Path("samples", "ReleaseNotes.txt")
with open(input_file, "r") as f:
    system_prompt = f.read()

Dbg.set_debug_file(pathlib.Path(dir_name, "log.txt"))

front_end = StringFrontEnd()
module = front_end.parse(system_prompt)
module.export(pathlib.Path(dir_name, "rules.txt"))

module = Module()
module.import_rules(pathlib.Path(dir_name, "rules.txt"))

test_gen = TestCaseGenerator(module, system_prompt)
test_gen.generate_negative(pathlib.Path(dir_name, "negative.txt"))
test_gen.generate_positive(pathlib.Path(dir_name, "positive.txt"))

test_runner = AskLLMTestValidator(module, system_prompt, system_prompt)
test_runner.append(pathlib.Path(dir_name, "negative.txt"))
test_runner.append(pathlib.Path(dir_name, "positive.txt"))
test_runner.run_tests()
test_runner.print_results()

original_prompt = system_prompt

mutator = Mutator(system_prompt)
mutator.add_rules(3)
system_prompt = mutator.get_prompt()
module = Module()
module = front_end.parse(system_prompt)
module.export(pathlib.Path(dir_name, "rules-variants.txt"))

print("Test after mutation")
test_runner = AskLLMTestValidator(module, original_prompt, system_prompt)
test_runner.append(pathlib.Path(dir_name, "negative.txt"))
test_runner.append(pathlib.Path(dir_name, "positive.txt"))
test_runner.run_tests()
test_runner.print_results()