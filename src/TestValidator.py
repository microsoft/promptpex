from . import LLMFrontEnd
import csv, pathlib

class TestValidator:
    def __init__(self, module, validation_sp, execution_sp, path=None):
        self.tests = []
        self.keys = []
        self.validation_sp = validation_sp
        self.execution_sp = execution_sp
        self.module = module
        self.results = []
        self.failed_tests = []

        self.result_path = open(pathlib.Path(path), "w")
        self.csvwriter = csv.writer(self.result_path, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
        self.csvwriter.writerow(["rule id", "input", "output", "reason for failure", "expected output"])

    def __del__(self):
        self.result_path.close()

    def dump(self):
        self.result_path.close()

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
        return passed, output, reason

    def get_failed_tests(self):
        return " ".join(self.failed_tests)

    def run_tests(self):
        for test in self.tests:
            passed, output, reason = self.run_test(test.strip(), "0")
            self.results.append(passed)
            expected_output = self.guess_expected_output(test)  

            data = [self.keys[self.tests.index(test)], test, output, reason, expected_output]
            data = [s.replace('\n', '\\n') for s in data]
            self.csvwriter.writerow(data)

            if not passed:
                self.failed_tests.append("input:\n" + test + "\noutput:\n" + output + "\nreason for failure: " + reason+"\n\n")

    def print_results(self):
        for i, res in enumerate(self.results):
            print(f"Test {self.keys[i]}: {'Passed' if res else 'Failed'}")
        self.dump()

    def validate(self, test_case):
        raise NotImplementedError("Subclasses should implement this method")

    def guess_expected_output(self, test_case):
        raise NotImplementedError("Subclasses should implement this method")

    def all_passed(self):
        return all(self.results)
    
class AskLLMTestValidator(TestValidator):
    def __init__(self, module, validation_sp, execution_sp, path=None):
        super().__init__(module, validation_sp, execution_sp, path)

    def validate(self, test_case):
        # result = LLMFrontEnd().execute(self.validation_sp, test_case, "gpt-35-turbo")
        output = LLMFrontEnd().execute(self.execution_sp, test_case, "gpt-4o")
        result = LLMFrontEnd().check_violation_with_system_prompt(output, self.validation_sp)
        return [output, result]

    def guess_expected_output(self, test_case):
        return LLMFrontEnd().expected_output(self.execution_sp, test_case)