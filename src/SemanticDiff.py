from . import LLMFrontEnd 
import pandas, numpy

class SemanticDiff:
    def __init__(self, src1, src2):
        # read csv with delimiter as tab
        self.src1 = pandas.read_csv(src1)
        self.src2 = pandas.read_csv(src2)
        
        # convert csv into text after dropping the second column
        self.rules1 = self.src1.drop("rule id", axis=1)
        self.rules2 = self.src2.drop("rule id", axis=1)

        result = LLMFrontEnd().rule_diff(self.rules1.to_string(index=True), self.rules2.to_string(index=True))
        # result = "1 2\n3 4"

        result = result.replace("\n\n", "\n")
        result = result.strip() 
        result = result.split("\n")
        if len(result) == 1:
            if result[0][0] == "-":
                self.deletion = result[0].split(" ")
            else:
                self.addition = result[0].split(" ")
        elif len(result) == 2:
            if result[0][0] == "-":
                self.deletion = result[0].split(" ")
                self.addition = result[1].split(" ")
            else:
                self.deletion = result[1].split(" ")
                self.addition = result[0].split(" ")
        elif len(result) == 0:
            self.deletion = []
            self.addition = []
        else:
            print("Error in the output of rule_diff")

        self.changes = pandas.DataFrame(columns=["type", "rule"])
        self.calculate_changes()

    def is_same(self):
        return len(self.deletion) == 0 and len(self.addition) == 0

    def calculate_changes(self):
        print(self.addition)
        print(self.deletion)
        print(self.rules1)
        for i in self.deletion:
          self.changes.loc[len(self.changes)] = ["-"] + [self.rules1['rule'][int(i)]]
        for i in self.addition:
          self.changes.loc[len(self.changes)] = ["+"] + [self.rules2['rule'][int(i)]]

    def get_changes(self):
        return self.changes.to_string(index=False, header=False)

    def get_positive_hash(self):
        hashes = []
        for i in self.addition:
            hashes.append(self.src2['rule id'][int(i) - 1])
        return hashes
    
    def get_negative_hash(self):
        hashes = []
        for i in self.deletion:
            hashes.append(self.src1['rule id'][int(i) - 1])
        return hashes

    def get_positive_rules(self):
        rules = []
        for i in self.addition:
            rules.append(self.rules2['rule'][int(i) - 1])
        return rules