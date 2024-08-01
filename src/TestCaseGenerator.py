import hashlib, csv, pathlib
from . import LLMFrontEnd, Rule, SemanticDiff

class TestCaseGenerator:
    def __init__(self, module, context=None, dir_name=""):
        self.module = module
        self.context = context
        self.input_spec = self.extract_input_spec(self.context)

        self.result_path = open(pathlib.Path(dir_name, "tests.csv"), "w")
        self.csvwriter = csv.writer(self.result_path, delimiter=",")
        self.csvwriter.writerow(["rule id", "test type", "rule", "test case"])

    def __del__(self):
        self.result_path.close()
    
    def exportCSV(self):
        self.result_path.close()

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
        # get next instruction from the enrty point until the end (None)
        instruction = self.module.get_entry()
        while instruction:
            if isinstance(instruction, Rule):
                self.generate_test_cases(instruction)
            instruction = instruction.next

    def generate_negative(self, file_path):
        instruction = self.module.get_entry()
        with open(file_path, "w", encoding="utf-8", errors="ignore") as f:
            f.write("")
        while instruction:
            if isinstance(instruction, Rule):
                invrule = LLMFrontEnd().inverse_rule(instruction.get_rule())
                negative = self.generate_test_case(invrule)
                index = str(self.module.instructions.index(instruction) + 1)
                hash = str(hashlib.md5(invrule.encode()).hexdigest())
                rule_hash = str(hashlib.md5(instruction.get_rule().encode()).hexdigest())
                with open(file_path, "a", encoding="utf-8", errors="ignore") as f:
                    f.write("=> " + index + " " + hash + " " + negative + "\n")
                    f.write(negative + "\n")
                self.csvwriter.writerow([hash, "negative", invrule, negative])
            instruction = instruction.next

    def generate_positive(self, file_path):
        with open(file_path, "w", encoding="utf-8", errors="ignore") as f:
            f.write("")
        instruction = self.module.get_entry()
        while instruction:
            if isinstance(instruction, Rule):
                positive = self.generate_test_case(instruction.get_rule())
                index = str(self.module.instructions.index(instruction) + 1)
                rule_hash = str(hashlib.md5(instruction.get_rule().encode()).hexdigest())
                with open(file_path, "a", encoding="utf-8", errors="ignore") as f:
                    f.write("=> " + index + " " + rule_hash + "\n")
                    f.write(positive + "\n")
                self.csvwriter.writerow([rule_hash, "positive", instruction.get_rule(), positive])
            instruction = instruction.next

    def update_test(self, diff, negative_test, positive_test):
        # generate inverse for + tests
        # generate rule for + and inv(+) rules 
        negative = diff.get_negative_hash()
        negative_tests = open(negative_test, "r").readlines()
        positive_tests = open(positive_test, "r").readlines()

        startDelete = False
        for line in negative_tests:
            if line.startswith("=>"):
                if line.split(" ")[3] in negative:
                    startDelete = True
                else:
                    startDelete = False
            if startDelete:
                negative_tests.remove(line)

        startDelete = False
        for line in positive_tests:
            if line.startswith("=>"):
                if line.split(" ")[3] in negative:
                    startDelete = True
                else:
                    startDelete = False
            if startDelete:
                positive_tests.remove(line)
        
        new_rules = diff.get_positive_rules()

        for rule in new_rules:
            tc = self.generate_test_case(rule)
            rule_hash = str(hashlib.md5(rule.encode()).hexdigest())
            positive_tests.append("=> 0 " + rule_hash + "\n")
            positive_tests.append(tc + "\n")

            inv = LLMFrontEnd().inverse_rule(rule)
            tc = self.generate_test_case(inv)
            rule_hash = str(hashlib.md5(inv.encode()).hexdigest())
            negative_tests.append("=> 0 " + rule_hash + "\n")
            negative_tests.append(tc + "\n")
        
        for index in range(len(positive_tests)):
            pos = positive_tests[index]
            if pos.startswith("=>"):
                pos_list = pos.split(" ")
                pos_list[1] = str(index)
                pos = " ".join(pos_list)
                positive_tests[index] = pos
        
        for index in range(len(negative_tests)):
            neg = negative_tests[index]
            if neg.startswith("=>"):
                neg_list = neg.split(" ")
                neg_list[1] = str(index)
                neg = " ".join(neg_list)
                negative_tests[index] = neg

        with open(negative_test, "w") as f:
            f.writelines(negative_test)
        with open(positive_test, "w") as f:
            f.writelines(positive_test)
        

