from src import StringFrontEnd, Module, TestCaseGenerator, AskLLMTestValidator, Mutator, LLMFrontEnd

# init log file with empty content
open("log.txt", "w").close()

system_prompt = """
You are an expert software developer who is writing a commit message when they are committing a change in 
a GitHub repo.  

You are given the code changes as <INPUT>. Input must contain filenames, line numbers, and
the code changes at those line numbers in the form of a standard git pull request.  <INPUT> must
contain changes to at least 3 files.

Assume multiple changes were made and the details of the changes are listed in the input.
Your task is to write a commit message for the change.
Commit Messages must have a short description that is less than 50 characters followed by a newline and a more detailed description.
- Write concisely using an informal tone
- List significant changes
- Do not use specific names or files from the code
- Do not use phrases like "this commit", "this change", etc.
"""

front_end = StringFrontEnd()
module = front_end.parse(system_prompt)
module.export("rules.txt")

module = Module()
module.import_rules("rules.txt")

test_gen = TestCaseGenerator(module, system_prompt)
test_gen.generate_negative("negative.txt")
test_gen.generate_positive("positive.txt")

test_runner = AskLLMTestValidator(module, system_prompt)
test_runner.append("negative.txt")
test_runner.append("positive.txt")
test_runner.run_tests()
test_runner.print_results()

mutator = Mutator(system_prompt)
mutator.add_rules(3)
system_prompt = mutator.get_prompt()
module = Module()
module = front_end.parse(system_prompt)
module.export("rules-variant.txt")

print("Test after mutation")
test_runner = AskLLMTestValidator(module, system_prompt)
test_runner.append("negative.txt")
test_runner.append("positive.txt")
test_runner.run_tests()
test_runner.print_results()