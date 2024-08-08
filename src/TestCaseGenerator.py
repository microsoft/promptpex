import hashlib, csv, pathlib, pandas
from . import LLMFrontEnd, Rule, SemanticDiff

class TestCaseGenerator:
    def __init__(self, module, context=None, test_path=None):
        self.module = module
        self.context = context
        self.tests = []
        self.result_path = None
        self.input_spec = None
        self.csvwriter = None
        
        if test_path is None:
            test_path = pathlib.Path("tests.csv")

        self.test_path = test_path

    def setup(self):
        self.input_spec = self.extract_input_spec(self.context)
        self.result_path = open(self.test_path, "w", encoding="utf-8", errors="ignore", newline='')
        self.csvwriter = csv.writer(self.result_path, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
        self.csvwriter.writerow(["rule id", "test type", "rule", "test case"])

    def __del__(self):
        if self.result_path is not None:
            self.result_path.close()
    
    def export_csv(self):
        self.result_path.close()
        if len(self.tests) != 0:
            self.tests.to_csv(self.result_path.name, index=False)
        else:
            self.tests = self.import_csv(self.result_path.name)

    def extract_input_spec(self, context):
        return LLMFrontEnd().generate_input_spec(context)

    def generate_test_case(self, rule):
        test_case = LLMFrontEnd().generate_test(rule, self.context, self.input_spec)
        return test_case

    def generate_test_cases(self, rule):
        invrule = LLMFrontEnd().inverse_rule(rule.get_rule())
        positive = self.generate_test_case(rule.get_rule())
        with open(self.dir_path + "positive.txt", "a", encoding="utf-8", errors="ignore") as f:
            f.write("=> " + positive + "\n")
        negative = self.generate_test_case(invrule)
        with open(self.dir_path + "negative.txt", "a", encoding="utf-8", errors="ignore") as f:
            f.write("=> " + negative + "\n")

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
                negative = self.generate_test_case(invrule)
                index = str(self.module.instructions.index(instruction) + 1)
                hash = str(hashlib.md5(invrule.encode()).hexdigest())
                rule_hash = str(hashlib.md5(instruction.get_rule().encode()).hexdigest())

                if file_path:
                    with open(file_path, "a", encoding="utf-8", errors="ignore") as f:
                        f.write("=> " + index + " " + hash + " " + negative + "\n")
                        f.write(negative + "\n")

                data = [hash, "negative", invrule, negative]
                data = [s.replace('\n', '\\n') for s in data]
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

                if file_path:
                    with open(file_path, "a", encoding="utf-8", errors="ignore") as f:
                        f.write("=> " + index + " " + rule_hash + "\n")
                        f.write(positive + "\n")

                data = [rule_hash, "positive", instruction.get_rule(), positive]
                data = [s.replace('\n', '\\n') for s in data]
                self.csvwriter.writerow(data)

            instruction = instruction.next

    def import_csv(self, file_path):
        reader = pandas.read_csv(file_path)
        for index, row in reader.iterrows():
            self.tests.append(row.tolist())

    def update_tests(self, diff : SemanticDiff):
        negative_hashes = diff.get_negative_hash()
        # delete rows in self.tests with "rule id" in negative_hashes
        import pdb; pdb.set_trace()
        self.tests = self.tests[~self.tests["rule id"].isin(negative_hashes)]

        positive_hashes = diff.get_positive_hash()
        positive_rules = diff.get_positive_rules() 
        for i in range(len(positive_hashes)):
            rule_hash = positive_hashes[i]
            rule = positive_rules[i]
            test_case = self.generate_test_case(rule)

            self.tests.loc[len(self.tests)] = [rule_hash, "positive", rule, test_case]

            inv_rule = LLMFrontEnd().inverse_rule(rule)
            inv_rule_hash = str(hashlib.md5(inv_rule.encode()).hexdigest())
            inv_test_case = self.generate_test_case(inv_rule)

            self.tests.loc[len(self.tests)] = [inv_rule_hash, "negative", inv_rule, inv_test_case]

        self.export_csv()