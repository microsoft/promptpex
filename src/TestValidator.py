from . import LLMFrontEnd

class TestValidator:
    def __init__(self, module, system_prompt):
        self.tests = []
        self.keys = []
        self.system_prompt = system_prompt
        self.module = module
        self.results = []

    def append(self, file_path):
        test = ""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("=>"):
                    self.keys.append(line.split(" ")[2].replace("\n", ""))
                    if test != "":
                        self.tests.append(test)
                    test = ""
                    continue
                test += line + "\n"

    def init(self, file_path):
        self.tests = []
        self.append(file_path)
        
    def run_test(self, test, expected):
        return self.validate(test) == expected

    def run_tests(self):
        for test in self.tests:
            self.results.append(self.run_test(test.strip(), "0"))

    def print_results(self):
        for i, res in enumerate(self.results):
            print(f"Test {self.keys[i]}: {'Passed' if res else 'Failed'}")

    def validate(self, test_case):
        raise NotImplementedError("Subclasses should implement this method")

    def all_passed(self):
        return all(self.results)
    
class AskLLMTestValidator(TestValidator):
    def __init__(self, system_prompt, module):
        super().__init__(system_prompt, module)

    def validate(self, test_case):
        result = LLMFrontEnd().execute(self.system_prompt, test_case, "gpt-35-turbo")
        return LLMFrontEnd().check_violation(result, self.module.__str__())