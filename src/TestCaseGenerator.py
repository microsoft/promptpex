import hashlib, csv, pathlib, pandas
from . import LLMFrontEnd, Rule, SemanticDiff

class TestCaseGenerator:
    def __init__(self, module, context=None, test_path=None, input_spec=""):
        self.module = module
        self.context = context
        self.tests = []
        self.result_path = None
        self.input_spec = input_spec
        self.csvwriter = None
        
        if test_path is None:
            test_path = pathlib.Path("tests.csv")

        self.test_path = test_path

    def setup(self):
        self.result_path = open(self.test_path, "w", encoding="utf-8", errors="ignore", newline='')
        self.csvwriter = csv.writer(self.result_path, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
        self.csvwriter.writerow(["rule id", "test type", "rule", "test case"])

    def __del__(self):
        if self.result_path is not None:
            self.result_path.close()
    
    def export_csv(self):
        if self.result_path is not None:
            self.result_path.close()

        if self.tests is None:
            self.tests = []

        if len(self.tests) != 0:
            self.result_path = open(self.test_path, "w", encoding="utf-8", errors="ignore", newline='')
            self.csvwriter = csv.writer(self.result_path, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
            self.csvwriter.writerow(["rule id", "test type", "rule", "test case"])
            for test in self.tests:
                self.csvwriter.writerow(test)
        else:
            self.tests = self.import_csv(self.test_path)

    def generate_test_case(self, rule):
        test_case = LLMFrontEnd().generate_test(rule, self.context, self.input_spec)
        return test_case

    def generate(self):
        self.setup()
        self.generate_negative()
        self.generate_positive()

    def generate_negative(self, file_path=""):
        instruction = self.module.get_entry()

        if file_path:
            with open(file_path, "w", encoding="utf-8", errors="ignore") as f:
                f.write("")

        while instruction:
            if isinstance(instruction, Rule):
                invrule = LLMFrontEnd().inverse_rule(instruction.get_rule())
                if invrule is None:
                    instruction = instruction.next
                    continue
                negative = self.generate_test_case(invrule)
                index = str(self.module.instructions.index(instruction) + 1)
                hash = str(hashlib.md5(invrule.encode()).hexdigest())
                rule_hash = str(hashlib.md5(instruction.get_rule().encode()).hexdigest())

                if file_path:
                    with open(file_path, "a", encoding="utf-8", errors="ignore") as f:
                        if negative is not None:
                            f.write("=> " + str(index) + " " + str(hash) + " " + str(negative) + "\n")
                            f.write(negative + "\n")

                data = [hash, "negative", invrule, negative]
                data = [s.replace('\n', '\\n') for s in data]
                assert self.csvwriter is not None
                self.csvwriter.writerow(data)

            instruction = instruction.next

    def generate_positive(self, file_path=""):
        if file_path:
            with open(file_path, "w", encoding="utf-8", errors="ignore") as f:
                f.write("")

        instruction = self.module.get_entry()
        while instruction:
            if isinstance(instruction, Rule):
                positive = self.generate_test_case(instruction.get_rule())
                index = str(self.module.instructions.index(instruction) + 1)
                rule_hash = str(hashlib.md5(instruction.get_rule().encode()).hexdigest())

                if positive is None:
                    instruction = instruction.next
                    continue

                if file_path:
                    with open(file_path, "a", encoding="utf-8", errors="ignore") as f:
                        f.write("=> " + index + " " + rule_hash + "\n")
                        f.write(positive + "\n")

                data = [rule_hash, "positive", instruction.get_rule(), positive]
                data = [s.replace('\n', '\\n') for s in data]
                assert self.csvwriter is not None
                self.csvwriter.writerow(data)

            instruction = instruction.next

    def import_csv(self, file_path):
        reader = pandas.read_csv(file_path)
        assert self.tests is not None
        for index, row in reader.iterrows():
            self.tests.append(row.tolist())

    def update_tests(self, diff : SemanticDiff):
        negative_hashes = diff.get_negative_hash()
        # delete rows in self.tests with "rule id" in negative_hashes
        new_tests = []
        assert self.tests is not None
        for tests in self.tests:
            if tests[0] not in negative_hashes:
                new_tests.append(tests)
        self.tests = new_tests

        positive_hashes = diff.get_positive_hash()
        positive_rules = diff.get_positive_rules() 
        for i in range(len(positive_hashes)):
            rule_hash = positive_hashes[i]
            rule = positive_rules[i]
            test_case = self.generate_test_case(rule)

            self.tests.append([rule_hash, "positive", rule, test_case])

            inv_rule = LLMFrontEnd().inverse_rule(rule)
            assert inv_rule is not None
            inv_rule_hash = str(hashlib.md5(inv_rule.encode()).hexdigest())
            inv_test_case = self.generate_test_case(inv_rule)

            self.tests.append([inv_rule_hash, "negative", inv_rule, inv_test_case])

        self.export_csv()