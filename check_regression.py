from src import StringFrontEnd, Module, TestCaseGenerator, AskLLMTestValidator, Mutator, Dbg
import time, os, pathlib

dir_name = "result-20240718-191459"

input_file = pathlib.Path("samples", "ReleaseNotes-variant1.txt")
with open(input_file, "r") as f:
    system_prompt = f.read()

Dbg.set_debug_file(pathlib.Path(dir_name, "reg-log.txt"))

module = Module()
module.import_rules(pathlib.Path(dir_name, "rules.txt"))
original_prompt = system_prompt
mutator = Mutator(system_prompt)
mutator.add_rules(800)
system_prompt = mutator.get_prompt()
module = Module()
front_end = StringFrontEnd()
module = front_end.parse(system_prompt)
module.export(pathlib.Path(dir_name, "rules-variants.txt"))

test_runner = AskLLMTestValidator(module, original_prompt, system_prompt)
test_runner.append(pathlib.Path(dir_name, "negative.txt"))
test_runner.append(pathlib.Path(dir_name, "positive.txt"))
test_runner.run_tests()
test_runner.print_results()