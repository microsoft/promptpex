from numpy.random import f
from . import LLMFrontEnd
import csv, pathlib, os

class TestValidator:
    def __init__(self, module, validation_sp, execution_sp, execution_model, path=None):
        self.execution_model = execution_model
        self.tests = []
        self.keys = []
        self.passed = []
        self.output = []
        self.reason = []
        self.expected = []
        self.validation_sp = validation_sp
        self.execution_sp = execution_sp
        self.module = module
        self.results = []
        self.failed_tests = []
        self.path = path

    def append(self, file_path):
        import re
        tests = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            tests = f.readlines()
        tests = tests[1:]
        for test in tests:
            row = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', str(test))
            if len(row) != 5:
                print("[Wrong data]: ", row)
                continue
            row = [x.strip().strip('"') for x in row]
            self.keys.append(row[0])
            self.tests.append(row[2])
            self.expected.append(row[3])
    
    def force_append_tests(self, tests):
        def guess_expected_output(test_case):
            return ""
        self.tests = tests
        self.keys = [str(i) for i in range(len(tests))]
        self.expected = [guess_expected_output(test) for test in tests]

    def run_test(self, test, expected):
        results = self.validate(test)
        output = results[0]
        result = results[1]
        passed = result[0] == expected
        reason = "\n".join(result.split("\n")[1:])
        return passed, output, reason

    def get_failed_tests(self):
        return " ".join(self.failed_tests)

    def run_tests(self, temp=1.0):
        assert self.path is not None
        result_path = pathlib.Path(self.path).open("a", encoding="utf-8", errors="ignore", newline='')
        csvwriter = csv.writer(result_path, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)

        with open(self.path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            if len(lines) == 0:
                csvwriter.writerow(["rule id", "input", "output", "result", "reason for failure", "expected output"])

        local_output = []
        for test in self.tests:
            output = self.run_single_test(test.strip(), temp)
            self.output.append(output)
            local_output.append(output)

        local_ouptut_str = "\n\n".join(local_output)
        validation_result = self.validate_batch(local_ouptut_str, "0", len(local_output))

        # assert len(validation_result) == len(local_output)

        for res in validation_result:
            self.results.append(res[0])
            self.passed.append(res[0])
            self.reason.append(res[1])

            if res[0] != "passed":
                self.failed_tests.append("INPUT:\n" + self.tests[validation_result.index(res)] + "\n\nOUTPUT:\n" + local_output[validation_result.index(res)] + "\n\nREASON: " + res[1]+"\n\n\n\n")

        for test in self.tests:
            idx = self.tests.index(test)
            offset = idx - len(local_output)

            data = [self.keys[idx], test, local_output[idx], self.passed[offset], self.reason[offset], self.expected[idx]]
            data = [s.replace('\n', '\\n') for s in data]
            csvwriter.writerow(data)

        result_path.close()

    def importResults(self, path):
        with open(path, "r", encoding="utf-8", errors="ignore") as csvfile:
            reader = csv.reader(csvfile)
            self.keys = [line[0] for line in reader]
            self.tests = [line[1] for line in reader]
            self.output = [line[2] for line in reader]
            self.results = [line[3] == "passed" for line in reader]
            self.reason = [line[4] for line in reader]

        for test in self.tests:
            if not self.results[self.tests.index(test)]:
                self.failed_tests.append("input:\n" + test + "\noutput:\n" + self.output[self.tests.index(test)] + "\nreason for failure: " + self.reason[self.tests.index(test)]+"\n\n")

    def print_results(self):
        for i, res in enumerate(self.results):
            print(f"Test {self.keys[i]}: {'passed' if res else 'failed'}")

    def validate(self, test_case):
        raise NotImplementedError("Subclasses should implement this method")

    def guess_expected_output(self, test_case):
        raise NotImplementedError("Subclasses should implement this method")

    def run_single_test(self, test_case, temp):
        raise NotImplementedError("Subclasses should implement this method")

    def validate_batch(self, output, expected, num_tests):
        raise NotImplementedError("Subclasses should implement this method")

    def all_passed(self):
        return all(self.results)
    
class AskLLMTestValidator(TestValidator):
    def __init__(self, module, validation_sp, execution_sp, execution_model, path=None):
        super().__init__(module, validation_sp, execution_sp, execution_model, path)

    def validate(self, test_case):
        # result = LLMFrontEnd().execute(self.validation_sp, test_case, "gpt-35-turbo")
        output = LLMFrontEnd().execute(self.execution_sp, test_case, self.execution_model, 1.0)
        result = LLMFrontEnd().check_violation_with_system_prompt(output, self.validation_sp)
        return [output, result]

    def run_single_test(self, test_case, temp=1.0):
        output = LLMFrontEnd().execute(self.execution_sp, test_case, self.execution_model, temp)
        return output

    def validate_batch(self, output, expected, num_tests):
        result = LLMFrontEnd().check_violation_with_system_prompt_batch(output, self.validation_sp, num_tests)
        if result is None:
            result = ""
        result.replace("\n\n", "\n")
        result = result.split("\n")
        output = []
        for line in result:
            if line == "":
                continue
            if line == "0" or line == "1":
                if line[0] == expected:
                    output.append(["passed", ""])
                else:
                    output.append(["failed", ""])
            else:
                output[-1][1] = output[-1][1] + line
        return output




    def guess_expected_output(self, test_case):
        return LLMFrontEnd().expected_output(self.execution_sp, test_case)