from . import LLMFrontEnd
import csv, pathlib

class TestValidator:
    def __init__(self, module, validation_sp, execution_sp, execution_model, path=None):
        self.execution_model = execution_model
        self.tests = []
        self.keys = []
        self.passed = []
        self.output = []
        self.reason = []
        self.validation_sp = validation_sp
        self.execution_sp = execution_sp
        self.module = module
        self.results = []
        self.failed_tests = []
        self.path = path

    def append(self, file_path):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as csvfile:
            reader = csv.reader(csvfile)
            self.tests.extend([line[-1] for line in reader])

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
        result_path = open(pathlib.Path(self.path), "w", encoding="utf-8", errors="ignore")
        csvwriter = csv.writer(result_path, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
        csvwriter.writerow(["rule id", "input", "output", "result", "reason for failure", "expected output"])

        for test in self.tests:
            passed, output, reason = self.run_test(test.strip(), "0")
            self.results.append(passed)
            self.passed.append(passed)
            self.output.append(output)  
            self.reason.append(reason)
            expected_output = self.guess_expected_output(test)  

            if passed:
                passed_str = "Passed"
            else:
                passed_str = "Failed"

            data = [self.keys[self.tests.index(test)], test, output, passed_str, reason, expected_output]
            data = [s.replace('\n', '\\n') for s in data]
            self.csvwriter.writerow(data)

            if not passed:
                self.failed_tests.append("input:\n" + test + "\noutput:\n" + output + "\nreason for failure: " + reason+"\n\n")

        result_path.close()

    def importResults(self, path):
        with open(path, "r", encoding="utf-8", errors="ignore") as csvfile:
            reader = csv.reader(csvfile)
            self.keys = [line[0] for line in reader]
            self.tests = [line[1] for line in reader]
            self.output = [line[2] for line in reader]
            self.results = [line[3] == "Passed" for line in reader]
            self.reason = [line[4] for line in reader]

        for test in self.tests:
            if not self.results[self.tests.index(test)]:
                self.failed_tests.append("input:\n" + test + "\noutput:\n" + self.output[self.tests.index(test)] + "\nreason for failure: " + self.reason[self.tests.index(test)]+"\n\n")

    def print_results(self):
        for i, res in enumerate(self.results):
            print(f"Test {self.keys[i]}: {'Passed' if res else 'Failed'}")

    def validate(self, test_case):
        raise NotImplementedError("Subclasses should implement this method")

    def guess_expected_output(self, test_case):
        raise NotImplementedError("Subclasses should implement this method")

    def all_passed(self):
        return all(self.results)
    
class AskLLMTestValidator(TestValidator):
    def __init__(self, module, validation_sp, execution_sp, execution_model, path=None):
        super().__init__(module, validation_sp, execution_sp, execution_model, path)

    def validate(self, test_case):
        # result = LLMFrontEnd().execute(self.validation_sp, test_case, "gpt-35-turbo")
        output = LLMFrontEnd().execute(self.execution_sp, test_case, self.execution_model)
        result = LLMFrontEnd().check_violation_with_system_prompt(output, self.validation_sp)
        return [output, result]

    def guess_expected_output(self, test_case):
        return LLMFrontEnd().expected_output(self.execution_sp, test_case)