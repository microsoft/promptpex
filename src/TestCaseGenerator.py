import hashlib
from . import LLMFrontEnd, Rule

class TestCaseGenerator:
    def __init__(self, module, context=None):
        self.module = module
        self.context = context
        self.input_spec = self.extract_input_spec(self.context)
    
    def extract_input_spec(self, context):
        return LLMFrontEnd().generate_input_spec(context)

    def generate_test_case(self, rule):
        test_case = LLMFrontEnd().generate_test(rule, self.context, self.input_spec)
        return test_case

    def generate_test_cases(self, rule):
        invrule = LLMFrontEnd().inverse_rule(rule.get_rule())
        positive = self.generate_test_case(rule.get_rule())
        with open(self.dir_path + "positive.txt", "a") as f:
            f.write("=> " + positive + "\n")
        negative = self.generate_test_case(invrule)
        with open(self.dir_path + "negative.txt", "a") as f:
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
        with open(file_path, "w") as f:
            f.write("")
        while instruction:
            if isinstance(instruction, Rule):
                invrule = LLMFrontEnd().inverse_rule(instruction.get_rule())
                negative = self.generate_test_case(invrule)
                index = str(self.module.instructions.index(instruction) + 1)
                hash = str(hashlib.md5(negative.encode()).hexdigest())
                rule_hash = str(hashlib.md5(instruction.get_rule().encode()).hexdigest())
                with open(file_path, "a") as f:
                    f.write("=> " + index + " " + hash + " " + rule_hash + " " + negative + "\n")
                    f.write(negative + "\n")
            instruction = instruction.next

    def generate_positive(self, file_path):
        with open(file_path, "w") as f:
            f.write("")
        instruction = self.module.get_entry()
        while instruction:
            if isinstance(instruction, Rule):
                positive = self.generate_test_case(instruction.get_rule())
                index = str(self.module.instructions.index(instruction) + 1)
                rule_hash = str(hashlib.md5(instruction.get_rule().encode()).hexdigest())
                with open(file_path, "a") as f:
                    f.write("=> " + index + " " + rule_hash + "\n")
                    f.write(positive + "\n")
            instruction = instruction.next