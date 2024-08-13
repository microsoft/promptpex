from . import Module, Rule, Instruction

class FrontEnd:
    def parse(self, input_data):
        raise NotImplementedError("Subclasses should implement this method")

class StringFrontEnd(FrontEnd):
    def parse(self, input_data, num_rules=0):
        module = Module()
        instruction = Rule.from_string(input_data, num_rules)

        if isinstance(instruction, list):
            for inst in instruction:
                module.add_instruction(inst)            
        elif isinstance(instruction, Instruction):
            module.add_instruction(instruction)
        
        return module