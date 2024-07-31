from . import LLMFrontEnd 

class SemanticDiff:
    def __init__(self, src1, src2):
        with open(src1, "r") as f:
            self.src1 = f.read()
        with open(src2, "r") as f:
            self.src2 = f.read()
        result = LLMFrontEnd().rule_diff(src1, src2)
        # result has two lines of integers separated by a space
        result = result.split("\n")
        self.deletion = result[0].split(" ")
        self.addition = result[1].split(" ")
        self.changes = ""
        self.calculate_changes()

    def is_same(self):
        return len(self.deletion) == 0 and len(self.addition) == 0

    def calculate_changes(self):
        rules1 = self.src1.split("\n")
        rules2 = self.src2.split("\n")
        for i in self.deletion:
          self.changes += f"- {rules1[int(i)]}\n"
        for i in self.addition:
          self.changes += f"+ {rules2[int(i)]}\n"   

    def get_changes(self):
        return self.changes

    def get_hash(self, sign):
        changes = self.changes.split("\n")
        hashes = []
        for change in changes:
            if change[0] == sign:
                hashes.append(changes[2])
        return hashes

    def get_positive_hash(self):
        return self.get_hash('+')
    
    def get_negative_hash(self):
        return self.get_hash('-')

    def get_rules(self, sign):
        changes = self.changes.split("\n")
        rules = []
        for change in changes:
            if change[0] == sign:
                rules.append(changes[3])
        return rules

    def get_positive_rules(self):
        return self.get_rules('+')
    
    def get_negative_rules(self):
        return self.get_rules('-')
