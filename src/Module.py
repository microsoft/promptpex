import hashlib, csv
from . import Instructions, Rule, LLMFrontEnd

class Module:
    def __init__(self):
        self.instructions = []

    def add_instruction(self, instruction):
        # early exit if instruction is None
        if not instruction:
            return
        instruction.module = self
        if self.instructions:
            instruction.prev = self.instructions[-1]
            self.instructions[-1].next = instruction
        self.instructions.append(instruction)

    def add_instruction_after(self, instruction, prev_instruction):
        instruction.module = self
        instruction.prev = prev_instruction
        instruction.next = prev_instruction.next
        prev_instruction.next = instruction
        if instruction.next:
            instruction.next.prev = instruction
        self.instructions.insert(self.instructions.index(prev_instruction) + 1, instruction)

    def remove_instruction(self, instruction):
        if instruction.prev:
            instruction.prev.next = instruction.next
        if instruction.next:
            instruction.next.prev = instruction.prev
        self.instructions.remove(instruction)

    def get_entry(self):
        return self.instructions[0]

    def __str__(self):
        return "\n".join(instr.__str__() for instr in self.instructions)

    def export(self, file_path):
        with open(file_path, "w", encoding="utf-8", errors="ignore", newline='') as f:
            csv_write = csv.writer(f)
            csv_write.writerow(["rule id", "rule"])

            for instr in self.instructions:
                if isinstance(instr, Rule):
                    rule = instr.get_rule()
                    idx = str(self.instructions.index(instr) + 1)
                    hash = str(hashlib.md5(rule.encode()).hexdigest())
                    csv_write.writerow([hash, rule])

    def import_rules(self, file_path):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            csv_read = csv.reader(f)
            next(csv_read)
            for row in csv_read:
                self.add_instruction(Rule(row[1]))
            for line in f:
                parts = line.strip().split(" ")
                idx = int(parts[0])
                rule = " ".join(parts[2:])
                self.add_instruction(Rule(rule))