from src import StringFrontEnd, Module, TestCaseGenerator, AskLLMTestValidator, Mutator, Dbg
import time, os, pathlib

dir_name = "result-20240718-191459"

input_file = pathlib.Path("samples", "ReleaseNotes-variant1.txt")
with open(input_file, "r") as f:
    system_prompt = f.read()

Dbg.set_debug_file(pathlib.Path(dir_name, "fix-log.txt"))

module = Module()
module.import_rules(pathlib.Path(dir_name, "rules.txt"))

test_runner = AskLLMTestValidator(module, system_prompt, system_prompt, "gpt-35-turbo")
test_runner.append(pathlib.Path(dir_name, "negative.txt"))
test_runner.append(pathlib.Path(dir_name, "positive.txt"))
test_runner.run_tests()
test_runner.print_results()