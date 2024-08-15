import hashlib, csv, pathlib, pandas
from . import LLMFrontEnd, Rule, SemanticDiff

class TestCaseGenerator:
    def __init__(self, module, context=None, test_path=None, input_spec=[]):
        self.module = module
        self.context = context
        self.tests = []
        self.result_path = None
        self.input_spec = input_spec
        self.csvwriter = None
        
        if test_path is None:
            test_path = pathlib.Path("tests.csv")

        self.test_path = test_path

    def generate_test_case(self, rule):
        test_case = LLMFrontEnd().generate_test(rule, self.context, self.input_spec)
        return test_case

    def get_rules(self):
        entry = self.module.get_entry()
        rules = []
        while entry:
            if isinstance(entry, Rule):
                rules.append(entry.get_rule())
            entry = entry.next
        return rules

    def get_inv_rules(self):
        inv_rules = []
        rules = self.get_rules()
        inv_rules = LLMFrontEnd().inverse_rule("\n".join(rules)).split("\n")
        return inv_rules

    def get_all_rules(self):
        rules = self.get_rules()
        inv_rules = self.get_inv_rules()
        return rules + inv_rules

    def gen_all_tests(self, num_tests=1):
        rules_list = self.get_all_rules()
        rules = "\n".join(rules_list)
        tests = LLMFrontEnd().generate_test(rules, self.context, self.input_spec, num_tests)
        with open(self.test_path, "w", encoding="utf-8", errors="ignore", newline='') as f:
            f.write(tests)
        self.import_csv(self.test_path)
        if self.tests is None:
            self.tests = []
        return self.tests

        

        #     csv_writer = csv.writer(f, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
        #     csv_writer.writerow(["rule id", "test type", "rule", "test case"])
        #     for tests in tests_list:
        #         test = tests.split(",")
        #         self.tests.append(test)
        #         index = tests_list.index(tests)
        #         type = "positive"
        #         if index >= len(rules_list) / 2:
        #             type = "negative"
        #         csv_writer.writerow(["rule id", type, rules_list[index], test[2]])

    def generate(self):
        return self.gen_all_tests()

    def import_csv(self, file_path):
        self.tests = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            self.tests = f.readlines()

    def update_tests(self, diff : SemanticDiff):
        assert False, "Not implemented for batch mode"
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