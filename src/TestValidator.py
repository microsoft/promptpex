from . import LLMFrontEnd

class TestValidator:
    def __init__(self, module, validation_sp, execution_sp):
        self.tests = []
        self.keys = []
        self.validation_sp = validation_sp
        self.execution_sp = execution_sp
        self.module = module
        self.results = []
        self.failed_tests = []

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
        results = self.validate(test)
        output = results[0]
        result = results[1]
        passed = result[0] == expected
        reason = "\n".join(result.split("\n")[1:])
        if not passed:
            self.failed_tests.append("input:\n" + test + "\noutput:\n" + output + "\nreason for failure: " + reason+"\n\n")
        return passed

    def get_failed_tests(self):
        return " ".join(self.failed_tests)

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
    def __init__(self, module, validation_sp, execution_sp):
        super().__init__(module, validation_sp, execution_sp)

    def validate(self, test_case):
        # result = LLMFrontEnd().execute(self.validation_sp, test_case, "gpt-35-turbo")
        output = LLMFrontEnd().execute(self.execution_sp, test_case, "gpt-4o")
        result = LLMFrontEnd().check_violation_with_system_prompt(output, self.validation_sp)
        return [output, result]